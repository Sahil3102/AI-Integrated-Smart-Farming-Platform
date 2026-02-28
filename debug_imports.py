import sys
import os

print("--- sys.path ---")
for p in sys.path:
    print(p)

print("\n--- Current Directory ---")
print(os.getcwd())

print("\n--- Attempting Imports ---")
try:
    import smart_agriculture.ai_models.chatbot_views
    print("SUCCESS: imported smart_agriculture.ai_models.chatbot_views")
except ImportError as e:
    print(f"FAILED: smart_agriculture.ai_models.chatbot_views - {e}")

try:
    # Simulating what happens inside urls.py if run as a module
    sys.path.append(os.path.join(os.getcwd(), 'smart_agriculture'))
    import ai_models.chatbot_views
    print("SUCCESS: imported ai_models.chatbot_views")
except ImportError as e:
    print(f"FAILED: ai_models.chatbot_views - {e}")
