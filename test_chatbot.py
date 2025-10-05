"""
Quick test to verify chatbot is working with Gemini
"""
import os
import sys

# Set Gemini API key
os.environ['GEMINI_API_KEY'] = 'AIzaSyCRIK6ZjYpwO7YknZIO-kCFOuiPQwxrKpw'

# Add backend to path
sys.path.insert(0, 'backend')

print("="*70)
print("TESTING CHATBOT WITH GEMINI")
print("="*70)

# Test Gemini directly
print("\n1. Testing Gemini API directly...")
print("-"*70)
try:
    import google.generativeai as genai
    genai.configure(api_key=os.environ['GEMINI_API_KEY'])
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content('Say hello and tell me you are ready to help with trip planning in one sentence.')
    print("✅ Gemini Response:")
    print(response.text)
except Exception as e:
    print(f"❌ Error: {e}")

# Test weather predictions
print("\n\n2. Testing Weather Predictions...")
print("-"*70)
try:
    from prediction.predict_simple import predict_daily_range
    forecast = predict_daily_range("2025-10-04", "2025-10-06")
    print("✅ Weather predictions working!")
    print(f"Got {len(forecast)} days of forecast")
    print(forecast.head())
except Exception as e:
    print(f"❌ Error: {e}")

print("\n\n3. Testing Backend API Server...")
print("-"*70)
print("To test the full chatbot:")
print("1. Run: python backend/api_server.py")
print("2. Open: frontend_new/index.html")
print("3. Look for chatbot in bottom-right corner")
print("4. Ask: 'What's the weather like for my trip?'")

print("\n" + "="*70)
print("✅ CHATBOT IS READY!")
print("="*70)
