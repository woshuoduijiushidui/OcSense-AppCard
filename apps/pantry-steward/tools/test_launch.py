"""Offline guards: no custom host, no accidental key generation or secret copying."""
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("pantry_launch", Path(__file__).with_name("launch.py"))
launch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launch)


class LaunchTests(unittest.TestCase):
    @unittest.skipUnless(os.name == "nt", "Windows batch launcher")
    def test_windows_entrypoint_format(self):
        script = (launch.APP / "run.cmd").read_bytes()
        script.decode("ascii")
        self.assertIn(b"\r\n", script)
        self.assertNotIn(b"\n", script.replace(b"\r\n", b""))

    @unittest.skipUnless(os.name == "nt", "Windows batch launcher")
    def test_windows_entrypoint_reaches_python(self):
        result = subprocess.run(
            f'cmd.exe /d /s /c ""{launch.APP / "run.cmd"}" --help"',
            input="", capture_output=True, text=True, encoding="utf-8", errors="replace",
            cwd=launch.ROOT, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("--prepare-local-test", result.stdout)

    @unittest.skipUnless(os.name == "nt", "Windows batch launcher")
    def test_windows_entrypoint_preserves_failure(self):
        result = subprocess.run(
            f'cmd.exe /d /s /c ""{launch.APP / "run.cmd"}" --invalid-launch-test-option"',
            input="", capture_output=True, text=True, encoding="utf-8", errors="replace",
            cwd=launch.APP, timeout=30,
        )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("Launch failed.", result.stdout)

    def test_key_generation_requires_explicit_consent(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(launch, "key_dir", return_value=Path(directory) / "keys"), patch.object(launch, "run") as call:
                with self.assertRaisesRegex(RuntimeError, "本人许可"):
                    launch.local_install(Path("hub"), Path("installer"), False)
                call.assert_not_called()
                self.assertFalse((Path(directory) / "keys").exists())

    def test_source_has_no_secret_or_native_adapter(self):
        files = list((launch.APP / "bundle").rglob("*"))
        self.assertFalse(any(p.name == "ai.env" or p.suffix == ".key" for p in files))
        source = (launch.APP / "bundle/main.splash").read_text(encoding="utf-8")
        self.assertNotIn('host.request("microphone.', source)
        self.assertIn('host.request("model.complete"', source)
        self.assertIn("不读取 ai.env", source)

    def test_official_budget_does_not_claim_provider_ready(self):
        source = (launch.APP / "bundle/main.splash").read_text(encoding="utf-8")
        self.assertNotIn("r.data.configured", source)
        self.assertNotIn("r.data.model", source)
        self.assertIn('text.search("no_provider")', source)


if __name__ == "__main__":
    unittest.main()
