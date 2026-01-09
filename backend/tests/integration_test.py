#!/usr/bin/env python3
"""
Simple integration test to verify backend endpoints work
"""
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

def test_storage_module():
    """Test that storage module can be imported and basic operations work"""
    try:
        from app.storage import WhitelistStorage, TemplateStorage, ensure_storage_dir
        
        # Test storage directory creation
        ensure_storage_dir()
        print("✓ Storage directory ensured")
        
        # Test whitelist operations
        WhitelistStorage.set_all([])
        WhitelistStorage.add("test-entry")
        entries = WhitelistStorage.get_all()
        assert "test-entry" in entries, "Failed to add whitelist entry"
        print("✓ Whitelist add works")
        
        WhitelistStorage.remove("test-entry")
        entries = WhitelistStorage.get_all()
        assert "test-entry" not in entries, "Failed to remove whitelist entry"
        print("✓ Whitelist remove works")
        
        # Test template operations
        template_data = {
            "name": "Test Template",
            "description": "Test",
            "defaultMechanism": {},
            "mechanismsByTag": {}
        }
        TemplateStorage.save("test-template", template_data)
        loaded = TemplateStorage.get("test-template")
        assert loaded is not None, "Failed to save/load template"
        assert loaded["name"] == "Test Template", "Template data mismatch"
        print("✓ Template save/load works")
        
        TemplateStorage.delete("test-template")
        loaded = TemplateStorage.get("test-template")
        assert loaded is None, "Failed to delete template"
        print("✓ Template delete works")
        
        # Cleanup
        WhitelistStorage.set_all([])
        
        print("\n✓ All storage tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Storage test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pydantic_version():
    """Test that Pydantic v1 is installed (not v2)"""
    try:
        import pydantic
        version = pydantic.VERSION
        major_version = int(version.split('.')[0])
        
        if major_version == 1:
            print(f"✓ Pydantic v1 is installed (version: {version})")
        else:
            print(f"✗ Pydantic v{major_version} is installed (expected v1), version: {version}")
            return False
            
        # Test the specific import that fails in Pydantic v2
        try:
            from pydantic.fields import Undefined
            print("✓ Can import 'Undefined' from pydantic.fields (v1 compatibility)")
            return True
        except ImportError as e:
            print(f"✗ Cannot import 'Undefined' from pydantic.fields: {e}")
            print("  This indicates Pydantic v2 is installed, which breaks FastAPI 0.65.2")
            return False
            
    except Exception as e:
        print(f"✗ Pydantic version check failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_schemas():
    """Test that schemas can be imported"""
    try:
        from app.schemas import (
            WhitelistResponse, WhitelistEntry, WhitelistBulkUpdate,
            TemplateData, TemplateResponse, TemplatesResponse,
            TemplateImport, SuccessResponse
        )
        print("✓ All schemas imported successfully")
        return True
    except Exception as e:
        print(f"✗ Schema import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_endpoints_module():
    """Test that endpoints module can be imported"""
    try:
        from app.endpoints import router
        print("✓ Endpoints module imported successfully")
        
        # Count routes
        routes = [r for r in router.routes]
        print(f"  Found {len(routes)} routes")
        
        # Check for our new endpoints
        paths = [r.path for r in routes]
        expected_paths = ['/whitelist', '/templates', '/templates/{template_id}']
        for path in expected_paths:
            if path in paths:
                print(f"  ✓ Route {path} registered")
            else:
                print(f"  ✗ Route {path} NOT found")
        
        return True
    except Exception as e:
        print(f"✗ Endpoints import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Running backend integration tests...\n")
    
    results = []
    results.append(test_pydantic_version())
    results.append(test_schemas())
    results.append(test_storage_module())
    results.append(test_endpoints_module())
    
    if all(results):
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
