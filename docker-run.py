#!/usr/bin/env python3
"""Run the deploy container with the invoking user's existing CLI logins."""

import base64
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile


def keychain_read(service, account):
    result = subprocess.run(
        ["security", "find-generic-password", "-s", service, "-wa", account],
        capture_output=True, text=True, timeout=15,
    )
    if result.returncode == 44:  # Item not found; a file login may exist instead.
        return None
    if result.returncode:
        raise RuntimeError(f"Cannot read {service} login from macOS Keychain")
    value = result.stdout.strip()
    if value.startswith("go-keyring-base64:"):
        value = base64.b64decode(value.split(":", 1)[1]).decode()
    elif value.startswith("go-keyring-encoded:"):
        value = bytes.fromhex(value.split(":", 1)[1]).decode()
    json.loads(value)
    return value


def keychain_write(service, account, value):
    # Feed the secret through stdin, never the process arguments or console.
    if service == "gemini":
        value = "go-keyring-base64:" + base64.b64encode(value.encode()).decode()
    command = shlex.join([
        "add-generic-password", "-U", "-s", service, "-a", account, "-w", value,
    ])
    result = subprocess.run(
        ["security", "-i"], input=command + "\n", capture_output=True,
        text=True, timeout=15,
    )
    if result.returncode:
        raise RuntimeError(f"Cannot save refreshed {service} login to macOS Keychain")


def run(arguments):
    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).resolve()
    codex_account = "cli|" + hashlib.sha256(str(codex_home).encode()).hexdigest()[:16]
    credentials = [
        (codex_home / "auth.json", "/root/.codex/auth.json", "Codex Auth", codex_account),
        (Path.home() / ".gemini/antigravity-cli/antigravity-oauth-token",
         "/root/.gemini/antigravity-cli/antigravity-oauth-token", "gemini", "antigravity"),
    ]
    with tempfile.TemporaryDirectory(prefix="waneye-cli-auth-") as temporary:
        mounts, exported = [], []
        for source, target, service, account in credentials:
            value = None
            # AGY prefers the keyring; Codex normally uses auth.json.
            if sys.platform == "darwin" and (service == "gemini" or not source.is_file()):
                value = keychain_read(service, account)
            if value is not None:
                source = Path(temporary) / Path(target).name
                source.write_text(value)
                source.chmod(0o600)
                exported.append((source, service, account, value))
            elif not source.is_file():
                print(f"No saved {service} login found; using configured provider fallbacks.",
                      file=sys.stderr)
                continue
            # Both CLIs rewrite these files when refreshing OAuth tokens.
            mounts += ["--mount", f"type=bind,src={source},dst={target}"]
        try:
            return subprocess.run(["docker", "run", *mounts, *arguments]).returncode
        finally:
            for source, service, account, original in exported:
                updated = source.read_text()
                if updated != original:
                    json.loads(updated)
                    # Don't overwrite a host login that changed during deployment.
                    if keychain_read(service, account) == original:
                        keychain_write(service, account, updated)
                    else:
                        print(f"Host {service} login changed; leaving it untouched.", file=sys.stderr)


if __name__ == "__main__":
    try:
        sys.exit(run(sys.argv[1:]))
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as error:
        # Do not print subprocess output or JSON contents: they may contain tokens.
        print(f"Cannot prepare/save host CLI authentication ({type(error).__name__}). "
              "Check access to your CLI credential files and unlocked Keychain.", file=sys.stderr)
        sys.exit(1)
