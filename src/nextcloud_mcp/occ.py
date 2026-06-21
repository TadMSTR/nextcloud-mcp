"""occ CLI wrapper — runs commands in the Nextcloud container as root."""

from __future__ import annotations

import asyncio

import structlog

from .config import get_settings

log = structlog.get_logger()


def _sanitize_args(args: tuple[str, ...]) -> list[str]:
    """Redact values that follow --value in occ argv (e.g. config:system:set --value <secret>)."""
    result: list[str] = []
    skip = False
    for arg in args:
        if skip:
            result.append("[REDACTED]")
            skip = False
        elif arg == "--value":
            result.append(arg)
            skip = True
        else:
            result.append(arg)
    return result


async def run_occ(*args: str, timeout: int = 120) -> str:
    """Run an occ command and return stdout. Raises RuntimeError on non-zero exit."""
    cfg = get_settings()
    cmd = ["docker", "exec", cfg.container, "occ", "--no-ansi", *args]
    log.info("occ_exec", args=_sanitize_args(args))

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except TimeoutError:
        proc.kill()
        raise RuntimeError(f"occ timed out after {timeout}s: {' '.join(args)}")

    out = stdout.decode().strip()
    err = stderr.decode().strip()

    if proc.returncode != 0:
        detail = err or out
        raise RuntimeError(f"occ {' '.join(args)} failed (exit {proc.returncode}): {detail}")

    return out
