"""DevOps Learning App — FastAPI backend with real PTY + k3s."""

import asyncio
import json
import logging
import os
import pty
import signal
import struct
import fcntl
import termios
import select
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from lessons.registry import get_all_lessons, get_lesson

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

DATA_DIR = Path(os.environ.get("DATA_DIR", "/data"))
PROGRESS_FILE = DATA_DIR / "progress.json"
DATA_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="DevOps Learning API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_progress() -> dict:
    if PROGRESS_FILE.exists():
        try:
            return json.loads(PROGRESS_FILE.read_text())
        except Exception as e:
            log.warning("Progress file corrupted, resetting: %s", e)
    return {}


def save_progress(data: dict):
    try:
        PROGRESS_FILE.write_text(json.dumps(data, indent=2))
    except Exception as e:
        log.error("Failed to save progress: %s", e)


@app.get("/api/lessons")
def api_lessons():
    return get_all_lessons()


@app.get("/api/lessons/{key}")
def api_lesson(key: str):
    lesson = get_lesson(key)
    if not lesson:
        from fastapi import HTTPException
        raise HTTPException(404, "Lesson not found")
    return lesson


@app.get("/api/progress")
def api_get_progress():
    return load_progress()


@app.post("/api/progress/{key}")
async def api_set_progress(key: str, body: dict):
    progress = load_progress()
    progress[key] = body.get("done", False)
    save_progress(progress)
    return {"ok": True}


@app.get("/api/cluster/status")
def api_cluster_status():
    """Quick check if k3s is reachable."""
    import subprocess
    try:
        result = subprocess.run(
            ["kubectl", "get", "nodes", "--no-headers"],
            capture_output=True, text=True, timeout=8,
            env={**os.environ, "KUBECONFIG": "/tmp/k3s.yaml"}
        )
        nodes = [l.split()[0] for l in result.stdout.strip().splitlines() if l]
        return {"ready": result.returncode == 0, "nodes": nodes}
    except Exception as e:
        return {"ready": False, "error": str(e)}


# Shell environment for PTY sessions
BASH_ENV = {
    **os.environ,
    "TERM": "xterm-256color",
    "COLORTERM": "truecolor",
    "LANG": "en_US.UTF-8",
    "LC_ALL": "en_US.UTF-8",
    "HOME": "/root",
    "SHELL": "/bin/bash",
    "KUBECONFIG": "/tmp/k3s.yaml",
    "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
    # ArgoCD
    "ARGOCD_OPTS": "--plaintext --port-forward-namespace argocd",
    # AWS (mock credentials for learning exercises)
    "AWS_DEFAULT_REGION": "us-east-1",
    "AWS_REGION": "us-east-1",
    "AWS_PROFILE": "default",
    "AWS_ACCOUNT_ID": "123456789012",
    # Prompt (overridden by .bashrc which is sourced on login shell)
    "PS1": r"\[\033[01;32m\]devops@sandbox\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ ",
}


@app.websocket("/ws/terminal/{session_id}")
async def terminal_ws(websocket: WebSocket, session_id: str):
    await websocket.accept()
    log.info("Terminal session started: %s", session_id)

    pid, fd = pty.fork()

    if pid == 0:
        os.execvpe("/bin/bash", ["/bin/bash", "--login", "-i"], BASH_ENV)
        os._exit(1)

    _set_winsize(fd, 24, 200)
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

    loop = asyncio.get_event_loop()

    async def read_pty():
        while True:
            try:
                await asyncio.sleep(0.01)
                data = await loop.run_in_executor(None, _read_fd, fd)
                if data:
                    await websocket.send_text(json.dumps({
                        "type": "output",
                        "data": data.decode("utf-8", errors="replace"),
                    }))
            except (OSError, EOFError):
                break
            except Exception:
                break

    read_task = asyncio.create_task(read_pty())

    try:
        while True:
            raw = await websocket.receive_text()
            msg = json.loads(raw)
            if msg.get("type") == "input":
                os.write(fd, msg.get("data", "").encode("utf-8", errors="replace"))
            elif msg.get("type") == "resize":
                _set_winsize(fd, msg.get("rows", 24), msg.get("cols", 200))
            elif msg.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
    except WebSocketDisconnect:
        log.info("Terminal session disconnected: %s", session_id)
    except Exception as e:
        log.warning("Terminal session error %s: %s", session_id, e)
    finally:
        read_task.cancel()
        try: os.kill(pid, signal.SIGTERM)
        except Exception: pass
        try: os.close(fd)
        except Exception: pass
        try: os.waitpid(pid, os.WNOHANG)
        except Exception: pass


def _read_fd(fd: int) -> bytes:
    try:
        ready, _, _ = select.select([fd], [], [], 0.05)
        if ready:
            return os.read(fd, 4096)
    except (OSError, ValueError):
        raise EOFError
    return b""


def _set_winsize(fd: int, rows: int, cols: int):
    try:
        fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", rows, cols, 0, 0))
    except Exception:
        pass
