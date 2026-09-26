"""Credential handling tests; never read real host credentials or run Docker."""

import base64
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("docker_run", Path(__file__).with_name("docker-run.py"))
launcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launcher)


class AuthenticationTests(unittest.TestCase):
    def test_file_credentials_and_docker_exit_status(self):
        with tempfile.TemporaryDirectory(prefix="home with spaces ") as home:
            home = Path(home)
            codex = home / "custom-codex/auth.json"
            agy = home / ".gemini/antigravity-cli/antigravity-oauth-token"
            for path in (codex, agy):
                path.parent.mkdir(parents=True)
                path.write_text('{}')
            with patch.object(launcher.Path, "home", return_value=home), \
                 patch.dict(launcher.os.environ, {"CODEX_HOME": str(codex.parent)}), \
                 patch.object(launcher.sys, "platform", "linux"), \
                 patch.object(launcher.subprocess, "run", return_value=subprocess.CompletedProcess([], 7)) as run:
                self.assertEqual(launcher.run(["--rm", "image"]), 7)
                arguments = run.call_args.args[0]
                self.assertIn(f"type=bind,src={codex.resolve()},dst=/root/.codex/auth.json", arguments)
                self.assertIn(f"type=bind,src={agy},dst=/root/.gemini/antigravity-cli/antigravity-oauth-token", arguments)
                self.assertEqual(arguments[-2:], ["--rm", "image"])

    def test_keychain_export_refresh_and_cleanup(self):
        self.check_export(host_changed=False)

    def test_missing_logins_leave_api_fallbacks_available(self):
        with tempfile.TemporaryDirectory() as home, \
             patch.object(launcher.Path, "home", return_value=Path(home)), \
             patch.dict(launcher.os.environ, {"CODEX_HOME": home}), \
             patch.object(launcher.sys, "platform", "linux"), \
             patch.object(launcher.subprocess, "run", return_value=subprocess.CompletedProcess([], 0)) as run:
            self.assertEqual(launcher.run(["--env-file", "env", "image"]), 0)
            run.assert_called_once_with(["docker", "run", "--env-file", "env", "image"])

    def test_concurrent_host_login_is_not_overwritten(self):
        self.check_export(host_changed=True)

    def check_export(self, host_changed):
        mounted = []

        def docker(arguments):
            for argument in arguments:
                if argument.startswith("type=bind,"):
                    path = Path(argument.split("src=", 1)[1].split(",dst=", 1)[0])
                    mounted.append(path)
                    self.assertEqual(path.stat().st_mode & 0o777, 0o600)
                    self.assertEqual(path.read_text(), '{"token":"old"}')
                    path.write_text('{"token":"new"}')
            return subprocess.CompletedProcess(arguments, 0)

        original = '{"token":"old"}'
        with tempfile.TemporaryDirectory() as home, \
             patch.object(launcher.Path, "home", return_value=Path(home)), \
             patch.dict(launcher.os.environ, {"CODEX_HOME": home}), \
             patch.object(launcher.sys, "platform", "darwin"), \
             patch.object(launcher, "keychain_read", side_effect=[original, original] + [None if host_changed else original] * 2), \
             patch.object(launcher, "keychain_write") as save, \
             patch.object(launcher.subprocess, "run", side_effect=docker):
            self.assertEqual(launcher.run(["image"]), 0)
            self.assertEqual(save.call_count, 0 if host_changed else 2)
        self.assertEqual(len(mounted), 2)
        self.assertTrue(all(not path.exists() for path in mounted))

    def test_go_keyring_encodings(self):
        value = '{"token":{}}'
        for encoded in ("go-keyring-base64:" + base64.b64encode(value.encode()).decode(),
                        "go-keyring-encoded:" + value.encode().hex(), value):
            with patch.object(launcher.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, encoded)):
                self.assertEqual(launcher.keychain_read("gemini", "antigravity"), value)

    def test_locked_keychain_is_not_treated_as_missing_login(self):
        with patch.object(launcher.subprocess, "run", return_value=subprocess.CompletedProcess([], 36)):
            with self.assertRaises(RuntimeError):
                launcher.keychain_read("gemini", "antigravity")

    def test_keychain_write_does_not_put_secret_in_arguments(self):
        with patch.object(launcher.subprocess, "run", return_value=subprocess.CompletedProcess([], 0)) as run:
            launcher.keychain_write("gemini", "antigravity", '{"token":"secret"}')
            self.assertEqual(run.call_args.args[0], ["security", "-i"])
            self.assertIn("go-keyring-base64:", run.call_args.kwargs["input"])


if __name__ == "__main__":
    unittest.main()
