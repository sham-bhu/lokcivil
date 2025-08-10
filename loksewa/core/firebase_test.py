import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'loksewa.settings')
django.setup()

from core.firebase_config import firebase_storage

def test_firebase_connection():
    """
    Test Firebase connection
    """
    try:
        # Test if Firebase is initialized
        print("Testing Firebase connection...")
        
        # Try to access the bucket
        bucket = firebase_storage.bucket
        print(f"✅ Firebase connected successfully!")
        print(f"Bucket: {bucket.name}")
        
        # Test listing files (should work even if empty)
        blobs = list(bucket.list_blobs(max_results=5))
        print(f"✅ Bucket access successful. Found {len(blobs)} files.")
        
        return True
        
    except Exception as e:
        print(f"❌ Firebase connection failed: {str(e)}")
        return False

def test_firebase_upload():
    """
    Test Firebase upload functionality
    """
    try:
        print("\nTesting Firebase upload...")
        
        # Create a simple test file
        test_content = "This is a test file for Firebase upload"
        test_filename = "test_file.txt"
        
        # Create a mock file object
        class MockFile:
            def __init__(self, content, name):
                self.content = content
                self.name = name
                self.content_type = 'text/plain'
            
            def read(self):
                return self.content.encode('utf-8')
        
        mock_file = MockFile(test_content, test_filename)
        
        # Test upload
        result = firebase_storage.upload_file(mock_file, 'test')
        
        if result['success']:
            print(f"✅ Upload successful!")
            print(f"URL: {result['url']}")
            print(f"Path: {result['path']}")
            return True
        else:
            print(f"❌ Upload failed: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Upload test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Firebase Integration Test ===\n")
    
    # Test connection
    connection_ok = test_firebase_connection()
    
    if connection_ok:
        # Test upload
        upload_ok = test_firebase_upload()
        
        if upload_ok:
            print("\n🎉 All Firebase tests passed!")
            print("Firebase integration is working correctly.")
        else:
            print("\n⚠️ Upload test failed, but connection works.")
    else:
        print("\n❌ Firebase connection failed. Check configuration.")
    
    print("\n=== Test Complete ===") 