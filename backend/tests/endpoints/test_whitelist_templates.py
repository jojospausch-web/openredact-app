"""
Tests for whitelist and template endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.storage import WhitelistStorage, TemplateStorage, WHITELIST_FILE, TEMPLATES_FILE
import json

client = TestClient(app)


@pytest.fixture(autouse=True)
def cleanup_storage():
    """Clean up storage before and after each test"""
    # Clear before test
    WhitelistStorage.set_all([])
    TemplateStorage.save("_test_cleanup", {})
    TemplateStorage.delete("_test_cleanup")
    yield
    # Clear after test
    WhitelistStorage.set_all([])
    TemplateStorage.save("_test_cleanup", {})
    TemplateStorage.delete("_test_cleanup")


class TestWhitelistEndpoints:
    def test_get_empty_whitelist(self):
        response = client.get("/api/whitelist")
        assert response.status_code == 200
        data = response.json()
        assert "entries" in data
        assert isinstance(data["entries"], list)

    def test_add_whitelist_entry(self):
        response = client.post("/api/whitelist", json={"entry": "Test Entry"})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        # Verify it was added
        response = client.get("/api/whitelist")
        assert "Test Entry" in response.json()["entries"]

    def test_add_empty_whitelist_entry(self):
        response = client.post("/api/whitelist", json={"entry": ""})
        assert response.status_code == 400

    def test_remove_whitelist_entry(self):
        # Add entry first
        client.post("/api/whitelist", json={"entry": "To Remove"})

        # Remove it
        response = client.delete("/api/whitelist", json={"entry": "To Remove"})
        assert response.status_code == 200

        # Verify it was removed
        response = client.get("/api/whitelist")
        assert "To Remove" not in response.json()["entries"]

    def test_bulk_update_whitelist(self):
        entries = ["Entry 1", "Entry 2", "Entry 3"]
        response = client.put("/api/whitelist", json={"entries": entries})
        assert response.status_code == 200

        # Verify update
        response = client.get("/api/whitelist")
        assert response.json()["entries"] == entries


class TestTemplateEndpoints:
    def test_get_empty_templates(self):
        response = client.get("/api/templates")
        assert response.status_code == 200
        data = response.json()
        assert "templates" in data
        assert isinstance(data["templates"], dict)

    def test_save_and_get_template(self):
        template_data = {
            "name": "Medical Template",
            "description": "For medical documents",
            "defaultMechanism": {"mechanism": "suppression", "config": {"suppressionChar": "X"}},
            "mechanismsByTag": {"PER": {"mechanism": "pseudonymization", "config": {}}},
        }

        # Save template
        response = client.post("/api/templates/medical-1", json=template_data)
        assert response.status_code == 200

        # Get specific template
        response = client.get("/api/templates/medical-1")
        assert response.status_code == 200
        data = response.json()
        assert data["templateId"] == "medical-1"
        assert data["template"]["name"] == "Medical Template"

    def test_get_nonexistent_template(self):
        response = client.get("/api/templates/nonexistent")
        assert response.status_code == 404

    def test_delete_template(self):
        # Create template first
        template_data = {
            "name": "To Delete",
            "description": "",
            "defaultMechanism": {"mechanism": "suppression", "config": {}},
            "mechanismsByTag": {},
        }
        client.post("/api/templates/delete-me", json=template_data)

        # Delete it
        response = client.delete("/api/templates/delete-me")
        assert response.status_code == 200

        # Verify deletion
        response = client.get("/api/templates/delete-me")
        assert response.status_code == 404

    def test_import_templates(self):
        templates = {
            "template1": {
                "name": "Template 1",
                "description": "First template",
                "defaultMechanism": {"mechanism": "suppression", "config": {}},
                "mechanismsByTag": {},
            },
            "template2": {
                "name": "Template 2",
                "description": "Second template",
                "defaultMechanism": {"mechanism": "pseudonymization", "config": {}},
                "mechanismsByTag": {},
            },
        }

        response = client.post("/api/templates/import", json={"templates": templates})
        assert response.status_code == 200
        assert "2 template(s)" in response.json()["message"]

        # Verify import
        response = client.get("/api/templates")
        data = response.json()["templates"]
        assert "template1" in data
        assert "template2" in data

    def test_export_templates(self):
        # Create some templates
        template_data = {
            "name": "Export Test",
            "description": "",
            "defaultMechanism": {"mechanism": "suppression", "config": {}},
            "mechanismsByTag": {},
        }
        client.post("/api/templates/export-test", json=template_data)

        # Export
        response = client.get("/api/templates/export/all")
        assert response.status_code == 200
        data = response.json()
        assert "templates" in data
        assert "export-test" in data["templates"]
