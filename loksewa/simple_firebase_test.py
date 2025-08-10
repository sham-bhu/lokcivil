import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'loksewa.settings')
django.setup()

try:
    from core.firebase_config import firebase_storage
    print("Firebase config imported successfully")
    
    # Test connection
    if firebase_storage.bucket:
        print("Firebase connection: SUCCESS")
        print(f"Bucket: {firebase_storage.bucket.name}")
    else:
        print("Firebase connection: FAILED")
        
except Exception as e:
    print(f"Firebase test failed: {str(e)}")

print("Test completed") 