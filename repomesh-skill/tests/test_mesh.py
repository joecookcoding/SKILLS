import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / ".agents" / "skills" / "repomesh" / "scripts" / "mesh.py"
spec = importlib.util.spec_from_file_location("mesh", MODULE_PATH)
mesh = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mesh)


class RepoMeshTests(unittest.TestCase):
    def test_slugify(self):
        self.assertEqual(mesh.slugify("Frontend API"), "frontend-api")
        self.assertEqual(mesh.slugify(" Repo / One "), "repo-one")

    def test_parse_name_status(self):
        parsed = mesh.parse_name_status("M\tsrc/a.ts\nR100\told.ts\tnew.ts")
        self.assertEqual(parsed[0]["status"], "M")
        self.assertEqual(parsed[1]["old_path"], "old.ts")
        self.assertEqual(parsed[1]["path"], "new.ts")

    def test_repo_init_is_non_destructive(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "app"
            repo.mkdir()
            subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
            custom = repo / ".repo-map" / "hot.md"
            custom.parent.mkdir(parents=True)
            custom.write_text("human content\n", encoding="utf-8")
            args = type("Args", (), {"path": str(repo)})()
            self.assertEqual(mesh.init_repo(args), 0)
            self.assertEqual(custom.read_text(encoding="utf-8"), "human content\n")
            self.assertTrue((repo / ".repo-map" / "manifest.yaml").exists())
            self.assertTrue((repo / ".agents" / "skills" / "repomesh" / "SKILL.md").exists())

    def test_mesh_init_creates_git_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "mesh"
            args = type("Args", (), {"path": str(target)})()
            self.assertEqual(mesh.init_mesh(args), 0)
            self.assertTrue((target / ".git").exists())
            self.assertTrue((target / "registry").is_dir())
            self.assertTrue((target / "graph" / "interfaces").is_dir())


if __name__ == "__main__":
    unittest.main()
