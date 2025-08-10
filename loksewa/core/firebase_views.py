from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .firebase_config import firebase_storage
from .models import Note, GKEntry, Article, Pradesh, ModelSet, TemplateResource, GalleryImage, CurrentEvent
from bson import ObjectId

def upload_note_to_firebase(request, note_id):
    """
    Upload a note file to Firebase Storage
    """
    if request.method == 'POST':
        try:
            note = get_object_or_404(Note, _id=ObjectId(note_id))
            
            if 'file' in request.FILES:
                file = request.FILES['file']
                
                # Upload to Firebase
                result = firebase_storage.upload_file(file, 'notes')
                
                if result['success']:
                    # Update the note with Firebase URL
                    note.file = result['url']
                    note.save()
                    
                    messages.success(request, 'File uploaded to Firebase successfully!')
                    return JsonResponse({
                        'success': True,
                        'url': result['url'],
                        'message': 'File uploaded to Firebase successfully!'
                    })
                else:
                    messages.error(request, f'Upload failed: {result["error"]}')
                    return JsonResponse({
                        'success': False,
                        'error': result['error']
                    })
            else:
                messages.error(request, 'No file provided')
                return JsonResponse({
                    'success': False,
                    'error': 'No file provided'
                })
                
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def upload_gk_to_firebase(request, gk_id):
    """
    Upload a GK document to Firebase Storage
    """
    if request.method == 'POST':
        try:
            gk_entry = get_object_or_404(GKEntry, _id=ObjectId(gk_id))
            
            if 'document' in request.FILES:
                file = request.FILES['document']
                
                # Upload to Firebase
                result = firebase_storage.upload_file(file, 'gk/docs')
                
                if result['success']:
                    # Update the GK entry with Firebase URL
                    gk_entry.document = result['url']
                    gk_entry.save()
                    
                    messages.success(request, 'Document uploaded to Firebase successfully!')
                    return JsonResponse({
                        'success': True,
                        'url': result['url'],
                        'message': 'Document uploaded to Firebase successfully!'
                    })
                else:
                    messages.error(request, f'Upload failed: {result["error"]}')
                    return JsonResponse({
                        'success': False,
                        'error': result['error']
                    })
            else:
                messages.error(request, 'No document provided')
                return JsonResponse({
                    'success': False,
                    'error': 'No document provided'
                })
                
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def upload_article_to_firebase(request, article_id):
    """
    Upload an article image to Firebase Storage
    """
    if request.method == 'POST':
        try:
            article = get_object_or_404(Article, _id=ObjectId(article_id))
            
            if 'image' in request.FILES:
                file = request.FILES['image']
                
                # Upload to Firebase
                result = firebase_storage.upload_file(file, 'blog')
                
                if result['success']:
                    # Update the article with Firebase URL
                    article.image = result['url']
                    article.save()
                    
                    messages.success(request, 'Image uploaded to Firebase successfully!')
                    return JsonResponse({
                        'success': True,
                        'url': result['url'],
                        'message': 'Image uploaded to Firebase successfully!'
                    })
                else:
                    messages.error(request, f'Upload failed: {result["error"]}')
                    return JsonResponse({
                        'success': False,
                        'error': result['error']
                    })
            else:
                messages.error(request, 'No image provided')
                return JsonResponse({
                    'success': False,
                    'error': 'No image provided'
                })
                
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def upload_template_to_firebase(request, template_id):
    """
    Upload a template file/image to Firebase Storage
    """
    if request.method == 'POST':
        try:
            template = get_object_or_404(TemplateResource, _id=ObjectId(template_id))
            
            if 'file' in request.FILES:
                file = request.FILES['file']
                
                # Upload to Firebase
                result = firebase_storage.upload_file(file, 'templates/docs')
                
                if result['success']:
                    # Update the template with Firebase URL
                    template.file = result['url']
                    template.save()
                    
                    messages.success(request, 'File uploaded to Firebase successfully!')
                    return JsonResponse({
                        'success': True,
                        'url': result['url'],
                        'message': 'File uploaded to Firebase successfully!'
                    })
                else:
                    messages.error(request, f'Upload failed: {result["error"]}')
                    return JsonResponse({
                        'success': False,
                        'error': result['error']
                    })
            elif 'image' in request.FILES:
                file = request.FILES['image']
                
                # Upload to Firebase
                result = firebase_storage.upload_file(file, 'templates/images')
                
                if result['success']:
                    # Update the template with Firebase URL
                    template.image = result['url']
                    template.save()
                    
                    messages.success(request, 'Image uploaded to Firebase successfully!')
                    return JsonResponse({
                        'success': True,
                        'url': result['url'],
                        'message': 'Image uploaded to Firebase successfully!'
                    })
                else:
                    messages.error(request, f'Upload failed: {result["error"]}')
                    return JsonResponse({
                        'success': False,
                        'error': result['error']
                    })
            else:
                messages.error(request, 'No file or image provided')
                return JsonResponse({
                    'success': False,
                    'error': 'No file or image provided'
                })
                
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def upload_gallery_to_firebase(request, gallery_id):
    """
    Upload a gallery image to Firebase Storage
    """
    if request.method == 'POST':
        try:
            gallery_image = get_object_or_404(GalleryImage, _id=ObjectId(gallery_id))
            
            if 'file' in request.FILES:
                file = request.FILES['file']
                
                # Upload to Firebase
                result = firebase_storage.upload_file(file, 'gallery')
                
                if result['success']:
                    # Update the gallery image with Firebase URL
                    gallery_image.file = result['url']
                    gallery_image.save()
                    
                    messages.success(request, 'Image uploaded to Firebase successfully!')
                    return JsonResponse({
                        'success': True,
                        'url': result['url'],
                        'message': 'Image uploaded to Firebase successfully!'
                    })
                else:
                    messages.error(request, f'Upload failed: {result["error"]}')
                    return JsonResponse({
                        'success': False,
                        'error': result['error']
                    })
            else:
                messages.error(request, 'No image provided')
                return JsonResponse({
                    'success': False,
                    'error': 'No image provided'
                })
                
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def upload_event_to_firebase(request, event_id):
    """
    Upload an event image/document to Firebase Storage
    """
    if request.method == 'POST':
        try:
            event = get_object_or_404(CurrentEvent, _id=ObjectId(event_id))
            
            if 'image' in request.FILES:
                file = request.FILES['image']
                
                # Upload to Firebase
                result = firebase_storage.upload_file(file, 'current_events/images')
                
                if result['success']:
                    # Update the event with Firebase URL
                    event.image = result['url']
                    event.save()
                    
                    messages.success(request, 'Image uploaded to Firebase successfully!')
                    return JsonResponse({
                        'success': True,
                        'url': result['url'],
                        'message': 'Image uploaded to Firebase successfully!'
                    })
                else:
                    messages.error(request, f'Upload failed: {result["error"]}')
                    return JsonResponse({
                        'success': False,
                        'error': result['error']
                    })
            elif 'document' in request.FILES:
                file = request.FILES['document']
                
                # Upload to Firebase
                result = firebase_storage.upload_file(file, 'current_events/docs')
                
                if result['success']:
                    # Update the event with Firebase URL
                    event.document = result['url']
                    event.save()
                    
                    messages.success(request, 'Document uploaded to Firebase successfully!')
                    return JsonResponse({
                        'success': True,
                        'url': result['url'],
                        'message': 'Document uploaded to Firebase successfully!'
                    })
                else:
                    messages.error(request, f'Upload failed: {result["error"]}')
                    return JsonResponse({
                        'success': False,
                        'error': result['error']
                    })
            else:
                messages.error(request, 'No image or document provided')
                return JsonResponse({
                    'success': False,
                    'error': 'No image or document provided'
                })
                
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}) 