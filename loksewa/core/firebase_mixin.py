from django.contrib import messages
from .firebase_config import firebase_storage
import uuid
import os

class FirebaseUploadMixin:
    """
    Mixin to handle Firebase uploads in admin views
    """
    
    def upload_to_firebase(self, file, folder_path):
        """
        Upload a file to Firebase and return the URL
        """
        try:
            result = firebase_storage.upload_file(file, folder_path)
            
            if result['success']:
                return result['url']
            else:
                messages.error(self.request, f'Firebase upload failed: {result["error"]}')
                return None
                
        except Exception as e:
            messages.error(self.request, f'Firebase upload error: {str(e)}')
            return None
    
    def handle_file_upload(self, file, folder_path, original_filename=None):
        """
        Handle file upload to Firebase
        Returns: (firebase_url, success_message)
        """
        if not file:
            return None, "No file provided"
        
        # Upload to Firebase
        firebase_url = self.upload_to_firebase(file, folder_path)
        
        if firebase_url:
            return firebase_url, f"File uploaded to Firebase successfully! URL: {firebase_url}"
        else:
            return None, "Firebase upload failed"
    
    def get_firebase_folder(self, model_name):
        """
        Get the appropriate Firebase folder based on model
        """
        folder_mapping = {
            'note': 'notes',
            'gkentry': 'gk/docs',
            'article': 'blog',
            'pradesh': 'pradesh/docs',
            'modelset': 'model_sets',
            'templateresource': 'templates',
            'galleryimage': 'gallery',
            'currentevent': 'current_events',
        }
        
        return folder_mapping.get(model_name.lower(), 'uploads') 