#!/usr/bin/env python3
"""
Direct test of AI client generation to see the exact error
"""
import sys
import os
sys.path.append('../backend')

from dotenv import load_dotenv
load_dotenv('../.env')

from ai_client import get_ai_client

def test_ai_generation():
    try:
        ai_client = get_ai_client()
        print(f"AI client available: {ai_client.is_available()}")
        
        if ai_client.is_available():
            status = ai_client.get_status()
            print(f"AI client status: {status}")
            
            # Test simple generation
            print("\n=== Testing AI Generation ===")
            
            system_prompt = """You are an expert HR consultant with deep knowledge of candidate assessment. 
Your responses should be:
- Conversational and engaging
- Specific about why each candidate fits the role
- Professional yet personable"""

            user_prompt = """User Query: "I need someone experienced with machine learning for a healthcare project"

Candidate Information:
Candidate 1: Dr. Sarah Chen
Experience: 6 years | Match Score: 1.54 | Status: available
Technical Skills: Python, TensorFlow, PyTorch, ML
Key Projects: Medical Diagnosis Platform, X-ray Analysis
Why they're a great fit: Has required skill: ML • Has healthcare domain experience • Currently available
Confidence Level: 73%

Please provide a brief response about this candidate."""

            try:
                response = ai_client.generate_response(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    max_tokens=300,
                    temperature=0.7
                )
                print(f"✅ AI Response: {response}")
                
            except Exception as ai_error:
                print(f"❌ AI Generation Error: {ai_error}")
                print(f"Error type: {type(ai_error)}")
                import traceback
                print(f"Full traceback:")
                traceback.print_exc()
        else:
            print("❌ AI client not available")
            
    except Exception as e:
        print(f"❌ Setup Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ai_generation()
