"""Verify isolated global installs preserve existing instructions and settings."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
if sys.version_info >= (3, 11):
    import install_codex


@unittest.skipIf(
    sys.version_info < (3, 11), "Standalone installer requires Python 3.11+"
)
class CodexInstallTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name).resolve()
        self.root = self.base / "maintenance checkout"
        self.home = self.base / "user"
        self.codex = self.home / ".codex"
        self.codex.mkdir(parents=True)
        self.agents = self.codex / "AGENTS.md"
        self.agents.write_bytes("保留原全局指令。\n".encode())
        self.config = self.codex / "config.toml"
        self.raw = b'model = "existing-model"\n\n[features]\nhooks = true\n'
        self.config.write_bytes(self.raw)
        for name in ("alpha", "beta"):
            folder = self.root / ".agents/skills" / name
            folder.mkdir(parents=True)
            (folder / "SKILL.md").write_text("skill instructions")
        profile = self.root / ".agents/profiles/personal.md"
        profile.parent.mkdir()
        profile.write_text("collaboration preferences")
        reference = self.root / ".agents/references/shared.md"
        reference.parent.mkdir()
        reference.write_text("shared reference")
        (self.root / "AGENTS.md").write_text("Repository-only instructions.\n")

    def call(self, check=False):
        return install_codex.install(self.root, self.home, self.codex, check)

    def test_live_links_config_and_existing_agents_are_preserved(self):
        agents = self.agents.read_bytes()
        repo_agents = (self.root / "AGENTS.md").read_bytes()
        self.call()
        link = self.home / ".agents/skills/alpha"
        self.assertTrue(link.is_symlink())
        self.assertEqual(link.resolve(), self.root / ".agents/skills/alpha")
        self.assertTrue(self.config.read_bytes().endswith(self.raw))
        self.assertEqual(self.agents.read_bytes(), agents)
        self.assertEqual((self.root / "AGENTS.md").read_bytes(), repo_agents)
        self.assertFalse((self.codex / "AGENTS.override.md").exists())
        self.assertEqual(
            (link / "../../references/shared.md").read_text(), "shared reference"
        )
        (self.root / ".agents/skills/alpha/SKILL.md").write_text("updated at source")
        self.assertEqual((link / "SKILL.md").read_text(), "updated at source")

    def test_repeated_install_and_check_do_not_rewrite_config(self):
        self.call()
        before = self.config.read_bytes()
        self.call()
        self.call(check=True)
        self.assertEqual(self.config.read_bytes(), before)
        parsed = install_codex.tomllib.loads(before.decode())
        self.assertEqual(parsed["model"], "existing-model")
        self.assertTrue(parsed["features"]["hooks"])
        self.assertIn(
            str(self.root / ".agents/profiles/personal.md"),
            parsed["developer_instructions"],
        )

    def test_foreign_skill_conflict_has_no_partial_install(self):
        foreign = self.home / ".agents/skills/beta"
        foreign.mkdir(parents=True)
        (foreign / "SKILL.md").write_text("unrelated")
        with self.assertRaisesRegex(ValueError, "拒绝覆盖"):
            self.call()
        self.assertFalse((foreign.parent / "alpha").exists())
        self.assertEqual((foreign / "SKILL.md").read_text(), "unrelated")
        self.assertEqual(self.config.read_bytes(), self.raw)

    def test_foreign_developer_instructions_or_disabled_skill_are_preserved(self):
        variants = [
            b'developer_instructions = "keep this"\n' + self.raw,
            self.raw + b'\n[[skills.config]]\nname = "alpha"\nenabled = false\n',
        ]
        for raw in variants:
            with self.subTest(config=json.dumps(raw.decode())):
                self.config.write_bytes(raw)
                with self.assertRaises(ValueError):
                    self.call()
                self.assertEqual(self.config.read_bytes(), raw)
                self.assertFalse((self.home / ".agents/skills/alpha").exists())

    def test_check_is_read_only_and_detects_missing_link(self):
        with self.assertRaises(ValueError):
            self.call(check=True)
        self.assertFalse((self.home / ".agents").exists())
        self.assertEqual(self.config.read_bytes(), self.raw)
        self.call()
        link = self.home / ".agents/skills/alpha"
        link.unlink()
        with self.assertRaises(ValueError):
            self.call(check=True)
        self.assertFalse(link.exists())


if __name__ == "__main__":
    unittest.main()
