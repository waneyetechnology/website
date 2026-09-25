"""Run with Python unittest inside the Linux deploy image; no credentials needed."""

import os
from pathlib import Path
import subprocess
import time
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "docker-run.sh"


class SupervisorTests(unittest.TestCase):
    def run_workflow(self, command, deadline="1"):
        return subprocess.run(
            ["bash", str(SCRIPT), *command],
            env={**os.environ, "DEPLOY_TIMEOUT_SECONDS": deadline},
            capture_output=True, text=True, timeout=15,
        )

    def test_success(self):
        self.assertEqual(self.run_workflow(["sh", "-c", "exit 0"]).returncode, 0)

    def test_failure(self):
        self.assertEqual(self.run_workflow(["sh", "-c", "exit 7"]).returncode, 7)

    def test_timeout(self):
        result = self.run_workflow(["sleep", "60"])
        self.assertEqual(result.returncode, 124)
        self.assertIn("TERM", result.stderr)

    def test_kills_unresponsive_workflow(self):
        start = time.monotonic()
        result = self.run_workflow(["sh", "-c", "trap '' TERM; while :; do sleep 1; done"])
        # GNU timeout is killed with its process group during escalation.
        self.assertIn(result.returncode, (-9, 137))
        self.assertLess(time.monotonic() - start, 14)
        self.assertIn("KILL", result.stderr)

    def test_invalid_deadlines(self):
        for deadline in ("0", "-1", "abc", "1.5"):
            with self.subTest(deadline=deadline):
                self.assertEqual(self.run_workflow(["true"], deadline).returncode, 2)


if __name__ == "__main__":
    unittest.main()
