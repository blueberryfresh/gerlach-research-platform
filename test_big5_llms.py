#!/usr/bin/env python3
"""
Test script for Big5 Personality LLMs
Run this to verify the installation and basic functionality
"""

import sys
import traceback
from big5_personality_llms import Big5LLMManager, OpennessLLM
from personality_evaluation import PersonalityEvaluator


def test_individual_model():
    """Test individual personality model"""
    print("🧪 Testing individual model (Openness)...")
    try:
        model = OpennessLLM()
        response = model.generate_response("What do you think about art?")
        print(f"✅ Openness model response: {response[:100]}...")
        return True
    except Exception as e:
        print(f"❌ Individual model test failed: {e}")
        traceback.print_exc()
        return False


def test_manager():
    """Test Big5LLMManager"""
    print("\n🧪 Testing Big5LLMManager...")
    try:
        manager = Big5LLMManager()
        
        # Test single response
        response = manager.get_response("conscientiousness", "How do you organize your day?")
        print(f"✅ Manager single response: {response[:100]}...")
        
        # Test all responses
        responses = manager.get_all_responses("What motivates you?")
        print(f"✅ Manager got responses from {len(responses)} personalities")
        
        return True
    except Exception as e:
        print(f"❌ Manager test failed: {e}")
        traceback.print_exc()
        return False


def test_evaluation():
    """Test evaluation framework"""
    print("\n🧪 Testing evaluation framework...")
    try:
        manager = Big5LLMManager()
        evaluator = PersonalityEvaluator(manager)
        
        # Run a quick evaluation with fewer prompts
        test_prompts = ["How do you solve problems?", "What's your approach to learning?"]
        results = evaluator.run_comprehensive_evaluation(test_prompts)
        
        print(f"✅ Evaluation completed with {len(results)} metrics")
        print("Consistency scores:", {k: f"{v:.3f}" for k, v in results["consistency"].items()})
        
        return True
    except Exception as e:
        print(f"❌ Evaluation test failed: {e}")
        traceback.print_exc()
        return False


def test_personality_differences():
    """Test that different personalities give different responses"""
    print("\n🧪 Testing personality differences...")
    try:
        manager = Big5LLMManager()
        prompt = "How do you handle challenges?"
        
        responses = manager.get_all_responses(prompt)
        
        # Check that we got different responses
        response_texts = list(responses.values())
        unique_responses = len(set(response_texts))
        
        print(f"✅ Got {unique_responses} unique responses out of {len(response_texts)} personalities")
        
        # Show sample responses
        for personality, response in list(responses.items())[:2]:
            print(f"  {personality}: {response[:80]}...")
        
        return unique_responses > 1
    except Exception as e:
        print(f"❌ Personality differences test failed: {e}")
        traceback.print_exc()
        return False


def check_dependencies():
    """Check if all required dependencies are available"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        "torch", "transformers", "numpy", "pandas", 
        "scikit-learn", "tqdm"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    return True


def main():
    """Run all tests"""
    print("🚀 Big5 Personality LLMs Test Suite")
    print("=" * 50)
    
    tests = [
        ("Dependencies", check_dependencies),
        ("Individual Model", test_individual_model),
        ("Manager", test_manager),
        ("Personality Differences", test_personality_differences),
        ("Evaluation Framework", test_evaluation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Your Big5 LLMs are ready to use.")
        print("\nNext steps:")
        print("- Run: streamlit run demo_interface.py")
        print("- Or: python demo_interface.py --cli")
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
    
    return passed == len(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
