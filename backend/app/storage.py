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

# Security limits
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_WHITELIST_ENTRIES = 10000
MAX_TEMPLATES = 1000


def ensure_storage_dir():
    """Ensure storage directory exists"""
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Storage directory ensured at {STORAGE_DIR}")


def load_json_file(filepath: Path, default: Any) -> Any:
    """Load JSON file or return default if not exists. Includes security checks."""
    try:
        if filepath.exists():
            # Check file size
            file_size = filepath.stat().st_size
            if file_size > MAX_FILE_SIZE:
                logger.error(f"File {filepath} exceeds maximum size ({MAX_FILE_SIZE} bytes)")
                return default

            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        return default
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {filepath}: {e}")
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
        entries = load_json_file(WHITELIST_FILE, [])
        # Validate structure
        if not isinstance(entries, list):
            logger.error(f"Invalid whitelist format, expected list")
            return []
        # Limit number of entries for security
        return entries[:MAX_WHITELIST_ENTRIES]

    @staticmethod
    def add(entry: str) -> bool:
        """Add entry to whitelist"""
        whitelist = WhitelistStorage.get_all()
        if len(whitelist) >= MAX_WHITELIST_ENTRIES:
            logger.error(f"Whitelist size limit reached ({MAX_WHITELIST_ENTRIES})")
            return False
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
        if len(entries) > MAX_WHITELIST_ENTRIES:
            logger.error(f"Whitelist size limit exceeded ({MAX_WHITELIST_ENTRIES})")
            return False
        return save_json_file(WHITELIST_FILE, entries)


class TemplateStorage:
    """Manages template persistence"""

    @staticmethod
    def get_all() -> Dict[str, Dict[str, Any]]:
        """Get all templates"""
        templates = load_json_file(TEMPLATES_FILE, {})
        # Validate structure
        if not isinstance(templates, dict):
            logger.error(f"Invalid templates format, expected dict")
            return {}
        # Limit number of templates for security
        if len(templates) > MAX_TEMPLATES:
            logger.warning(f"Templates exceed limit, truncating to {MAX_TEMPLATES}")
            templates = dict(list(templates.items())[:MAX_TEMPLATES])
        return templates

    @staticmethod
    def get(template_id: str) -> Optional[Dict[str, Any]]:
        """Get specific template"""
        templates = TemplateStorage.get_all()
        return templates.get(template_id)

    @staticmethod
    def save(template_id: str, template_data: Dict[str, Any]) -> bool:
        """Save or update template"""
        templates = TemplateStorage.get_all()
        if template_id not in templates and len(templates) >= MAX_TEMPLATES:
            logger.error(f"Template limit reached ({MAX_TEMPLATES})")
            return False
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
        if not isinstance(imported_templates, dict):
            logger.error("Invalid import format, expected dict")
            return False
        templates = TemplateStorage.get_all()
        # Check limit
        total_count = len(templates) + len(imported_templates)
        if total_count > MAX_TEMPLATES:
            logger.error(f"Import would exceed template limit ({MAX_TEMPLATES})")
            return False
        templates.update(imported_templates)
        return save_json_file(TEMPLATES_FILE, templates)


# Initialize storage on module load
ensure_storage_dir()
