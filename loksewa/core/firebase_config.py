import firebase_admin
from firebase_admin import credentials, storage
import os
from django.conf import settings
import uuid
from datetime import datetime

class FirebaseStorage:
    def __init__(self):
        # Initialize Firebase if not already initialized
        if not firebase_admin._apps:
            cred = credentials.Certificate('lokcivil-35588-firebase-adminsdk-fbsvc-6135679462.json')
            firebase_admin.initialize_app(cred, {
                'storageBucket': 'lokcivil-35588.firebasestorage.app'  # Updated bucket name
            })
        
        self.bucket = storage.bucket()
    
    def upload_file(self, file, folder_path):
        """
        Upload a file to Firebase Storage
        Returns: Firebase URL
        """
        try:
            # Generate unique filename
            file_extension = os.path.splitext(file.name)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Create full path
            firebase_path = f"{folder_path}/{unique_filename}"
            
            # Upload to Firebase
            blob = self.bucket.blob(firebase_path)
            blob.upload_from_file(file, content_type=file.content_type)
            
            # Make public and get URL
            blob.make_public()
            firebase_url = blob.public_url
            
            return {
                'success': True,
                'url': firebase_url,
                'path': firebase_path,
                'filename': unique_filename
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_file(self, firebase_path):
        """
        Delete a file from Firebase Storage
        """
        try:
            blob = self.bucket.blob(firebase_path)
            blob.delete()
            return {'success': True}
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_file_url(self, firebase_path):
        """
        Get public URL for a file
        """
        try:
            blob = self.bucket.blob(firebase_path)
            return blob.public_url
        except Exception as e:
            return None

# Global Firebase instance
firebase_storage = FirebaseStorage() 