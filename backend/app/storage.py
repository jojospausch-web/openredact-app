"""
Storage module for persisting whitelist and templates.
Uses JSON file-based storage for simplicity and Docker compatibility.
"""
import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Storage directory - can be mounted as Docker volume
STORAGE_DIR = Path(os.getenv("OPENREDACT_STORAGE_DIR", "/app/storage"))
WHITELIST_FILE = STORAGE_DIR / "whitelist.json"
TEMPLATES_FILE = STORAGE_DIR / "templates.json"


def ensure_storage_dir():
    """Ensure storage directory exists"""
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Storage directory ensured at {STORAGE_DIR}")


def load_json_file(filepath: Path, default: Any) -> Any:
    """Load JSON file or return default if not exists"""
    try:
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        return default
    except Exception as e:
        logger.error(f"Error loading {filepath}: {e}")
        return default


def save_json_file(filepath: Path, data: Any) -> bool:
    """Save data to JSON file"""
    try:
        ensure_storage_dir()
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving {filepath}: {e}")
        return False


class WhitelistStorage:
    """Manages whitelist persistence"""

    @staticmethod
    def get_all() -> List[str]:
        """Get all whitelist entries"""
        return load_json_file(WHITELIST_FILE, [])

    @staticmethod
    def add(entry: str) -> bool:
        """Add entry to whitelist"""
        whitelist = WhitelistStorage.get_all()
        if entry not in whitelist:
            whitelist.append(entry)
            return save_json_file(WHITELIST_FILE, whitelist)
        return True

    @staticmethod
    def remove(entry: str) -> bool:
        """Remove entry from whitelist"""
        whitelist = WhitelistStorage.get_all()
        if entry in whitelist:
            whitelist.remove(entry)
            return save_json_file(WHITELIST_FILE, whitelist)
        return True

    @staticmethod
    def set_all(entries: List[str]) -> bool:
        """Replace entire whitelist"""
        return save_json_file(WHITELIST_FILE, entries)


class TemplateStorage:
    """Manages template persistence"""

    @staticmethod
    def get_all() -> Dict[str, Dict[str, Any]]:
        """Get all templates"""
        return load_json_file(TEMPLATES_FILE, {})

    @staticmethod
    def get(template_id: str) -> Optional[Dict[str, Any]]:
        """Get specific template"""
        templates = TemplateStorage.get_all()
        return templates.get(template_id)

    @staticmethod
    def save(template_id: str, template_data: Dict[str, Any]) -> bool:
        """Save or update template"""
        templates = TemplateStorage.get_all()
        templates[template_id] = template_data
        return save_json_file(TEMPLATES_FILE, templates)

    @staticmethod
    def delete(template_id: str) -> bool:
        """Delete template"""
        templates = TemplateStorage.get_all()
        if template_id in templates:
            del templates[template_id]
            return save_json_file(TEMPLATES_FILE, templates)
        return True

    @staticmethod
    def import_templates(imported_templates: Dict[str, Dict[str, Any]]) -> bool:
        """Import templates (merge with existing)"""
        templates = TemplateStorage.get_all()
        templates.update(imported_templates)
        return save_json_file(TEMPLATES_FILE, templates)


# Initialize storage on module load
ensure_storage_dir()
