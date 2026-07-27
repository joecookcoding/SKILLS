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
            self.assertTrue((repo / ".repo-map" / "generated" / "architecture.json").exists())
            self.assertTrue((repo / ".repo-map" / "generated" / "architecture.html").exists())
            self.assertTrue((repo / ".agents" / "skills" / "repomesh" / "SKILL.md").exists())

    def test_mesh_init_creates_git_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "mesh"
            args = type("Args", (), {"path": str(target)})()
            self.assertEqual(mesh.init_mesh(args), 0)
            self.assertTrue((target / ".git").exists())
            self.assertTrue((target / "registry").is_dir())
            self.assertTrue((target / "graph" / "interfaces").is_dir())
            self.assertTrue((target / "graph" / "architecture.json").exists())
            self.assertTrue((target / "graph" / "architecture.html").exists())
            self.assertTrue((target / "graph" / "cross-repo.json").exists())

    def test_architecture_validation_and_render(self):
        data = {
            "schema_version": 1,
            "status": "verified-current",
            "project": {"id": "app", "name": "App", "source_commit": "abc", "generated_at": "2026-07-26T00:00:00Z"},
            "nodes": [
                {"id": "ui", "label": "UI", "type": "interface", "group": "Frontend", "path": "src/ui.ts"},
                {"id": "api", "label": "API", "type": "service", "group": "Backend", "path": "src/api.ts"},
            ],
            "edges": [{"id": "ui-api", "source": "ui", "target": "api", "label": "calls"}],
            "flows": [{"id": "request", "name": "Request", "steps": [{"nodeId": "ui"}, {"nodeId": "api"}]}],
        }
        errors, _ = mesh.validate_architecture_data(data)
        self.assertEqual(errors, [])
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "architecture.html"
            mesh.render_architecture_html(data, output)
            html = output.read_text(encoding="utf-8")
            self.assertIn("https://cdn.tailwindcss.com", html)
            self.assertIn("Interactive application architecture diagram", html)
            self.assertIn('"id": "request"', html)

    def test_architecture_validation_rejects_unknown_nodes(self):
        data = {
            "nodes": [{"id": "a", "label": "A", "path": "a.ts"}],
            "edges": [{"id": "bad", "source": "a", "target": "missing"}],
            "flows": [],
        }
        errors, _ = mesh.validate_architecture_data(data)
        self.assertTrue(any("unknown target" in error for error in errors))

    def test_context_plan_traverses_both_directions_and_complete_flow(self):
        data = {
            "nodes": [
                {"id": "auth", "label": "Auth", "path": "src/auth.ts", "concerns": ["auth"]},
                {"id": "hook", "label": "Auth Hook", "path": "src/use-auth.ts", "concerns": ["hooks"]},
                {"id": "page", "label": "Profile Page", "path": "src/profile.tsx"},
                {"id": "db", "label": "User DB", "path": "src/user-model.ts"},
            ],
            "edges": [
                {"id": "hook-auth", "source": "hook", "target": "auth", "context": "required"},
                {"id": "page-hook", "source": "page", "target": "hook", "context": "relevant"},
                {"id": "auth-db", "source": "auth", "target": "db", "context": "relevant"},
            ],
            "flows": [{
                "id": "profile-auth", "name": "Profile auth",
                "steps": [{"nodeId": "page"}, {"nodeId": "hook"}, {"nodeId": "auth"}, {"nodeId": "db"}],
                "edgeIds": ["page-hook", "hook-auth", "auth-db"],
            }],
        }
        plan = mesh.build_context_plan(data, [], task="change profile auth")
        self.assertEqual({node["id"] for node in plan["nodes"]}, {"auth", "hook", "page", "db"})
        self.assertEqual({flow["id"] for flow in plan["flows"]}, {"profile-auth"})
        self.assertIsNone(plan["hard_token_cap"])

    def test_context_plan_skips_reference_edges_unless_deep(self):
        data = {
            "nodes": [
                {"id": "page", "label": "Profile Page", "path": "src/profile.tsx"},
                {"id": "analytics", "label": "Analytics", "path": "src/analytics.ts"},
            ],
            "edges": [
                {"id": "page-analytics", "source": "page", "target": "analytics", "context": "reference"},
            ],
            "flows": [],
        }
        normal = mesh.build_context_plan(data, [], task="profile page")
        deep = mesh.build_context_plan(data, [], task="profile page", deep=True)
        self.assertEqual({node["id"] for node in normal["nodes"]}, {"page"})
        self.assertEqual({node["id"] for node in deep["nodes"]}, {"page", "analytics"})


if __name__ == "__main__":
    unittest.main()
