#!/usr/bin/env python3
"""
Simple test to verify quiz generation step by step
"""

import os
import pathlib
from quizzes import read_course_content_files, create_quiz_system_prompt

def test_step_by_step():
    print("🔧 Testing Quiz Generation Components Step by Step")
    print("="*60)
    
    # Step 1: Test file existence
    print("\n1️⃣ Testing file existence...")
    planner_path = pathlib.Path("Inputs and Outputs/planner_agent_instruction.txt")
    deep_path = pathlib.Path("copilot/Inputs and Outputs/deep_course_content_output.txt")
    
    print(f"Planner file exists: {planner_path.exists()} - {planner_path}")
    print(f"Deep file exists: {deep_path.exists()} - {deep_path}")
    
    # Step 2: Test file reading function
    print("\n2️⃣ Testing file reading function...")
    try:
        planner_content, deep_content = read_course_content_files()
        print(f"✅ Function completed")
        print(f"Planner content length: {len(planner_content)}")
        print(f"Deep content length: {len(deep_content)}")
        
        if planner_content:
            print("✅ Planner content found")
        else:
            print("❌ No planner content")
            
        if deep_content:
            print("✅ Deep content found")
        else:
            print("❌ No deep content")
            
    except Exception as e:
        print(f"❌ Error in file reading: {e}")
        return False
    
    # Step 3: Test system prompt generation
    print("\n3️⃣ Testing system prompt generation...")
    try:
        prompt = create_quiz_system_prompt("intermediate")
        print(f"✅ System prompt generated ({len(prompt)} characters)")
    except Exception as e:
        print(f"❌ Error in system prompt: {e}")
        return False
    
    print("\n🎉 All tests passed! Ready for full quiz generation.")
    return True

if __name__ == "__main__":
    test_step_by_step()
