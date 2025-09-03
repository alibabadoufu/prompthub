"""
System test script for PromptFlow Studio.
Tests core functionality without requiring external LLM APIs.
"""
import sys
import traceback
from typing import Dict, Any

def test_imports():
    """Test that all modules can be imported successfully."""
    print("🧪 Testing imports...")
    
    try:
        import data_manager as dm
        print("✅ data_manager imported successfully")
        
        import llm_client as llm
        print("✅ llm_client imported successfully")
        
        import utils
        print("✅ utils imported successfully")
        
        # Test config loading
        config = utils.load_config()
        print("✅ config.yaml loaded successfully")
        print(f"   Found {len(config.get('models', []))} models configured")
        
        return True
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        traceback.print_exc()
        return False


def test_database():
    """Test database operations."""
    print("\n🗄️  Testing database operations...")
    
    try:
        import data_manager as dm
        
        # Test database setup
        dm.db_manager.setup_database()
        print("✅ Database setup successful")
        
        # Test project creation
        try:
            project_id = dm.create_project("TestProject", "Test project for system verification")
            print(f"✅ Project creation successful (ID: {project_id})")
        except ValueError:
            # Project might already exist
            project = dm.get_project_by_name("TestProject")
            project_id = project["id"]
            print(f"✅ Project already exists (ID: {project_id})")
        
        # Test prompt creation
        try:
            prompt_id = dm.create_prompt(project_id, "TestPrompt")
            print(f"✅ Prompt creation successful (ID: {prompt_id})")
        except ValueError:
            # Prompt might already exist
            prompt = dm.get_prompt_by_name(project_id, "TestPrompt")
            prompt_id = prompt["id"]
            print(f"✅ Prompt already exists (ID: {prompt_id})")
        
        # Test version creation
        version_num = dm.save_prompt_version(
            prompt_id=prompt_id,
            template_text="Hello {{name}}, this is a test prompt with temperature {{temp}}.",
            model_name="Test Model",
            temperature=0.7,
            max_tokens=100,
            top_p=1.0,
            changelog="Test version for system verification"
        )
        print(f"✅ Version creation successful (Version: {version_num})")
        
        # Test setting active version
        dm.set_active_version(prompt_id, version_num)
        print(f"✅ Set version {version_num} as active")
        
        # Test API data retrieval
        api_data = dm.get_prompt_details_for_api("TestProject", "TestPrompt", "active")
        if api_data:
            print("✅ API data retrieval successful")
            print(f"   Template: {api_data['prompt_template'][:50]}...")
        else:
            print("❌ API data retrieval failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        traceback.print_exc()
        return False


def test_utils():
    """Test utility functions."""
    print("\n🔧 Testing utility functions...")
    
    try:
        from utils import extract_variables, format_prompt_template, validate_hyperparameters
        
        # Test variable extraction
        template = "Hello {{name}}, your order {{order_id}} is ready. Temperature is {{temperature}}."
        variables = extract_variables(template)
        expected_vars = ["name", "order_id", "temperature"]
        
        if set(variables) == set(expected_vars):
            print("✅ Variable extraction successful")
            print(f"   Found variables: {variables}")
        else:
            print(f"❌ Variable extraction failed. Expected {expected_vars}, got {variables}")
            return False
        
        # Test prompt formatting
        var_values = {"name": "John", "order_id": "12345", "temperature": "0.7"}
        formatted = format_prompt_template(template, var_values)
        expected = "Hello John, your order 12345 is ready. Temperature is 0.7."
        
        if formatted == expected:
            print("✅ Prompt formatting successful")
        else:
            print(f"❌ Prompt formatting failed.\nExpected: {expected}\nGot: {formatted}")
            return False
        
        # Test hyperparameter validation
        try:
            params = validate_hyperparameters(0.7, 256, 1.0)
            print("✅ Hyperparameter validation successful")
        except ValueError as e:
            print(f"❌ Hyperparameter validation failed: {e}")
            return False
        
        # Test invalid hyperparameters
        try:
            validate_hyperparameters(3.0, 256, 1.0)  # Invalid temperature
            print("❌ Hyperparameter validation should have failed for temperature=3.0")
            return False
        except ValueError:
            print("✅ Hyperparameter validation correctly rejected invalid temperature")
        
        return True
        
    except Exception as e:
        print(f"❌ Utils test failed: {e}")
        traceback.print_exc()
        return False


def test_llm_client_structure():
    """Test LLM client structure (without making actual API calls)."""
    print("\n🤖 Testing LLM client structure...")
    
    try:
        import llm_client as llm
        
        # Test client initialization
        client = llm.LLMClient()
        print("✅ LLM client initialization successful")
        
        # Test that methods exist
        if hasattr(client, 'generate_completion'):
            print("✅ generate_completion method exists")
        else:
            print("❌ generate_completion method missing")
            return False
        
        if hasattr(client, 'test_model_connection'):
            print("✅ test_model_connection method exists")
        else:
            print("❌ test_model_connection method missing")
            return False
        
        # Test error handling for non-existent model
        result = client.generate_completion(
            model_name="NonExistentModel",
            prompt_text="Test prompt",
            temperature=0.7,
            max_tokens=50,
            top_p=1.0
        )
        
        if not result["success"] and "error" in result:
            print("✅ Error handling for non-existent model works correctly")
        else:
            print("❌ Error handling for non-existent model failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ LLM client test failed: {e}")
        traceback.print_exc()
        return False


def test_gradio_imports():
    """Test that Gradio and required packages are available."""
    print("\n🌐 Testing Gradio and web dependencies...")
    
    try:
        import gradio as gr
        print("✅ Gradio imported successfully")
        print(f"   Gradio version: {gr.__version__}")
        
        import pandas as pd
        print("✅ Pandas imported successfully")
        
        import yaml
        print("✅ PyYAML imported successfully")
        
        import requests
        print("✅ Requests imported successfully")
        
        import json
        print("✅ JSON module available")
        
        return True
        
    except Exception as e:
        print(f"❌ Web dependencies test failed: {e}")
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all system tests."""
    print("🚀 Starting PromptFlow Studio System Tests")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Database Operations", test_database),
        ("Utility Functions", test_utils),
        ("LLM Client Structure", test_llm_client_structure),
        ("Web Dependencies", test_gradio_imports),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {len(results)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed! PromptFlow Studio is ready to use.")
        print("Run 'python demo_setup.py' to create sample data.")
        print("Then run 'python app.py' to start the application.")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)