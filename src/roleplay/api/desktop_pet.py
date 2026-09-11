"""桌面宠物拉起桥接：网页按钮在协议不可用时，由本地后端直接启动 Electron 壳。

仅允许回环来源调用；用于开发态/未注册 roleplaypet:// 协议时的可靠兜底。
"""
from __future__ import annotations

import asyncio
import logging
import os
import subprocess
import urllib.request
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/desktop-pet", tags=["desktop-pet"])

# src/roleplay/api/desktop_pet.py -> 仓库根
REPO_ROOT = Path(__file__).resolve().parents[3]
DESKTOP_DIR = REPO_ROOT / "desktop"
CONTROL_PORTS = range(39231, 39252)  # 与 control-server.js 自动 +1 上限 39251 对齐


def _is_loopback(request: Request) -> bool:
    host = (request.client.host if request.client else "") or ""
    host = host.lower().strip()
    return host in ("127.0.0.1", "::1", "localhost") or host.startswith("::ffff:127.0.0.1")


def _control_server_up() -> bool:
    for port in CONTROL_PORTS:
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/ping", timeout=0.4) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            continue
    return False


def _electron_command() -> list[str]:
    """直接定位 Electron 可执行文件，避免 `cmd /c npm start` 的批处理控制台/中断提示。

    开发态优先使用 node_modules/electron/dist/electron.exe（Windows）或
    node_modules/.bin/electron（macOS/Linux），这是最稳定的拉起方式。
    """
    if os.name == "nt":
        exe = DESKTOP_DIR / "node_modules" / "electron" / "dist" / "electron.exe"
        if exe.is_file():
            return [str(exe), "."]
        cmd = DESKTOP_DIR / "node_modules" / ".bin" / "electron.cmd"
        if cmd.is_file():
            return [os.environ.get("COMSPEC", "cmd.exe"), "/c", str(cmd), "."]
    else:
        bin_path = DESKTOP_DIR / "node_modules" / ".bin" / "electron"
        if bin_path.is_file():
            return [str(bin_path), "."]
    raise RuntimeError("未找到 Electron 可执行文件，请先在 desktop 目录执行 npm install")


def _launch_desktop() -> int:
    if not (DESKTOP_DIR / "package.json").is_file():
        raise RuntimeError(f"未找到桌面宠物工程: {DESKTOP_DIR}")

    cmd = _electron_command()

    log_dir = REPO_ROOT / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    stdout = open(log_dir / "desktop-pet-launch.out.log", "a", encoding="utf-8")
    stderr = open(log_dir / "desktop-pet-launch.err.log", "a", encoding="utf-8")

    popen_kwargs: dict = {}
    if os.name == "nt":
        # DETACHED_PROCESS 让 Electron 脱离后端控制台；CREATE_NEW_PROCESS_GROUP 避免 Ctrl+C 串扰
        popen_kwargs["creationflags"] = (
            subprocess.CREATE_NEW_PROCESS_GROUP
            | subprocess.DETACHED_PROCESS
            | getattr(subprocess, "CREATE_NO_WINDOW", 0)
        )
    else:
        popen_kwargs["start_new_session"] = True  # POSIX 脱离会话，等价 detached

    proc = subprocess.Popen(
        cmd,
        cwd=str(DESKTOP_DIR),
        stdin=subprocess.DEVNULL,
        stdout=stdout,
        stderr=stderr,
        close_fds=True,
        **popen_kwargs,
    )
    # 父进程关闭句柄，子进程继续持有写日志
    stdout.close()
    stderr.close()
    return proc.pid


@router.post("/launch")
async def launch_desktop_pet(request: Request) -> dict:
    if not _is_loopback(request):
        raise HTTPException(status_code=403, detail="仅允许本机网页唤起桌面宠物")

    # 探活是阻塞 IO（最多 21 端口 × 0.4s），必须在 worker 线程执行：
    # 直接在事件循环里跑会把所有并发请求（含进行中的 SSE 流）一起卡住。
    if await asyncio.to_thread(_control_server_up):
        return {"ok": True, "already_running": True}

    try:
        pid = _launch_desktop()
    except Exception as exc:  # noqa: BLE001
        logger.warning("拉起桌面宠物失败: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {"ok": True, "launched": True, "pid": pid}
