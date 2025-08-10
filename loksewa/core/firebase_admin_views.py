from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .firebase_mixin import FirebaseUploadMixin
from .models import Note, GKEntry, Article, Pradesh, ModelSet, TemplateResource, GalleryImage, CurrentEvent, Job, ObjectiveSubject, ObjectiveSet, ObjectiveMCQ, SubjectiveSubject, SubjectiveChapter, SubjectiveQA
from bson import ObjectId
import json
from django.utils import timezone
from datetime import timedelta

class FirebaseAdminView(FirebaseUploadMixin):
    """
    Base class for Firebase-enhanced admin views
    """
    pass

@login_required
def firebase_upload_note(request):
    """
    Upload note with Firebase storage
    """
    if request.method == 'POST':
        try:
            title = request.POST.get('title')
            description = request.POST.get('description')
            file = request.FILES.get('file')
            
            if not title or not file:
                messages.error(request, 'Title and file are required')
                return JsonResponse({'success': False, 'error': 'Missing required fields'})
            
            # Upload file to Firebase
            firebase_url, message = FirebaseAdminView().handle_file_upload(
                file, 'notes', title
            )
            
            if firebase_url:
                # Create note with Firebase URL
                note = Note.objects.create(
                    title=title,
                    description=description,
                    file=firebase_url  # Store Firebase URL instead of local path
                )
                
                messages.success(request, f'Note created successfully! {message}')
                return JsonResponse({
                    'success': True,
                    'message': 'Note uploaded to Firebase successfully!',
                    'url': firebase_url,
                    'note_id': str(note._id)
                })
            else:
                return JsonResponse({'success': False, 'error': message})
                
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return JsonResponse({'success': False, 'error': str(e)})
    
    return render(request, 'admin/firebase_upload_note.html')

@login_required
def firebase_upload_gk(request):
    """
    Upload GK document with Firebase storage
    """
    if request.method == 'POST':
        try:
            title = request.POST.get('title')
            content = request.POST.get('content')
            document = request.FILES.get('document')
            
            if not title or not document:
                messages.error(request, 'Title and document are required')
                return JsonResponse({'success': False, 'error': 'Missing required fields'})
            
            # Upload document to Firebase
            firebase_url, message = FirebaseAdminView().handle_file_upload(
                document, 'gk/docs', title
            )
            
            if firebase_url:
                # Create GK entry with Firebase URL
                gk_entry = GKEntry.objects.create(
                    title=title,
                    content=content,
                    document=firebase_url  # Store Firebase URL instead of local path
                )
                
                messages.success(request, f'GK document uploaded successfully! {message}')
                return JsonResponse({
                    'success': True,
                    'message': 'GK document uploaded to Firebase successfully!',
                    'url': firebase_url,
                    'gk_id': str(gk_entry._id)
                })
            else:
                return JsonResponse({'success': False, 'error': message})
                
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return JsonResponse({'success': False, 'error': str(e)})
    
    return render(request, 'admin/firebase_upload_gk.html')

@login_required
def firebase_upload_article(request):
    """
    Upload article with Firebase storage
    """
    if request.method == 'POST':
        try:
            title = request.POST.get('title')
            content = request.POST.get('content')
            image = request.FILES.get('image')
            
            if not title:
                messages.error(request, 'Title is required')
                return JsonResponse({'success': False, 'error': 'Title is required'})
            
            firebase_url = None
            if image:
                # Upload image to Firebase
                firebase_url, message = FirebaseAdminView().handle_file_upload(
                    image, 'blog', title
                )
            
            # Create article with Firebase URL
            article = Article.objects.create(
                title=title,
                content=content,
                image=firebase_url if firebase_url else None,  # Store Firebase URL
                category='blog'
            )
            
            if firebase_url:
                messages.success(request, f'Article created with Firebase image! {message}')
            else:
                messages.success(request, 'Article created successfully!')
            
            return JsonResponse({
                'success': True,
                'message': 'Article uploaded successfully!',
                'url': firebase_url,
                'article_id': str(article._id)
            })
                
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return JsonResponse({'success': False, 'error': str(e)})
    
    return render(request, 'admin/firebase_upload_article.html')

@login_required
def firebase_upload_template(request):
    """
    Upload template with Firebase storage
    """
    if request.method == 'POST':
        try:
            title = request.POST.get('title')
            description = request.POST.get('description')
            image = request.FILES.get('image')
            file = request.FILES.get('file')
            
            if not title:
                messages.error(request, 'Title is required')
                return JsonResponse({'success': False, 'error': 'Title is required'})
            
            firebase_admin = FirebaseAdminView()
            image_url = None
            file_url = None
            
            if image:
                # Upload image to Firebase
                image_url, message = firebase_admin.handle_file_upload(
                    image, 'templates/images', title
                )
            
            if file:
                # Upload file to Firebase
                file_url, message = firebase_admin.handle_file_upload(
                    file, 'templates/docs', title
                )
            
            # Create template with Firebase URLs
            template = TemplateResource.objects.create(
                title=title,
                description=description,
                image=image_url if image_url else None,  # Store Firebase URL
                file=file_url if file_url else None,     # Store Firebase URL
                category='template'
            )
            
            messages.success(request, 'Template uploaded to Firebase successfully!')
            return JsonResponse({
                'success': True,
                'message': 'Template uploaded successfully!',
                'image_url': image_url,
                'file_url': file_url,
                'template_id': str(template._id)
            })
                
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return JsonResponse({'success': False, 'error': str(e)})
    
    return render(request, 'admin/firebase_upload_template.html')

@login_required
def firebase_upload_gallery(request):
    """
    Upload gallery image with Firebase storage
    """
    if request.method == 'POST':
        try:
            title = request.POST.get('title')
            description = request.POST.get('description')
            file = request.FILES.get('file')
            
            if not title or not file:
                messages.error(request, 'Title and image are required')
                return JsonResponse({'success': False, 'error': 'Missing required fields'})
            
            # Upload image to Firebase
            firebase_url, message = FirebaseAdminView().handle_file_upload(
                file, 'gallery', title
            )
            
            if firebase_url:
                # Create gallery image with Firebase URL
                gallery_image = GalleryImage.objects.create(
                    title=title,
                    description=description,
                    file=firebase_url  # Store Firebase URL instead of local path
                )
                
                messages.success(request, f'Gallery image uploaded successfully! {message}')
                return JsonResponse({
                    'success': True,
                    'message': 'Gallery image uploaded to Firebase successfully!',
                    'url': firebase_url,
                    'gallery_id': str(gallery_image._id)
                })
            else:
                return JsonResponse({'success': False, 'error': message})
                
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return JsonResponse({'success': False, 'error': str(e)})
    
    return render(request, 'admin/firebase_upload_gallery.html')

@login_required
def firebase_upload_event(request):
    """
    Upload event with Firebase storage
    """
    if request.method == 'POST':
        try:
            title = request.POST.get('title')
            description = request.POST.get('description')
            image = request.FILES.get('image')
            document = request.FILES.get('document')
            
            if not title:
                messages.error(request, 'Title is required')
                return JsonResponse({'success': False, 'error': 'Title is required'})
            
            firebase_admin = FirebaseAdminView()
            image_url = None
            document_url = None
            
            if image:
                # Upload image to Firebase
                image_url, message = firebase_admin.handle_file_upload(
                    image, 'current_events/images', title
                )
            
            if document:
                # Upload document to Firebase
                document_url, message = firebase_admin.handle_file_upload(
                    document, 'current_events/docs', title
                )
            
            # Create event with Firebase URLs
            event = CurrentEvent.objects.create(
                title=title,
                description=description,
                image=image_url if image_url else None,      # Store Firebase URL
                document=document_url if document_url else None  # Store Firebase URL
            )
            
            messages.success(request, 'Event uploaded to Firebase successfully!')
            return JsonResponse({
                'success': True,
                'message': 'Event uploaded successfully!',
                'image_url': image_url,
                'document_url': document_url,
                'event_id': str(event._id)
            })
                
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return JsonResponse({'success': False, 'error': str(e)})
    
    return render(request, 'admin/firebase_upload_event.html')

@login_required
def firebase_upload_pradesh(request):
    """
    Upload Pradesh document with Firebase storage
    """
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            description = request.POST.get('description')
            document = request.FILES.get('document')
            image = request.FILES.get('image')
            
            if not name:
                messages.error(request, 'Name is required')
                return JsonResponse({'success': False, 'error': 'Name is required'})
            
            firebase_admin = FirebaseAdminView()
            document_url = None
            image_url = None
            
            if document:
                # Upload document to Firebase
                document_url, message = firebase_admin.handle_file_upload(
                    document, 'pradesh/docs', name
                )
            
            if image:
                # Upload image to Firebase
                image_url, message = firebase_admin.handle_file_upload(
                    image, 'pradesh/images', name
                )
            
            # Create Pradesh with Firebase URLs
            pradesh = Pradesh.objects.create(
                title=name,
                document=document_url if document_url else None,  # Store Firebase URL
            )
            
            messages.success(request, 'Pradesh uploaded to Firebase successfully!')
            return JsonResponse({
                'success': True,
                'message': 'Pradesh uploaded successfully!',
                'document_url': document_url,
                'image_url': image_url,
                'pradesh_id': str(pradesh._id)
            })
                
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return JsonResponse({'success': False, 'error': str(e)})
    
    return render(request, 'admin/firebase_upload_pradesh.html')

@login_required
def firebase_upload_modelset(request):
    """
    Upload Model Set with Firebase storage
    """
    if request.method == 'POST':
        try:
            title = request.POST.get('title')
            description = request.POST.get('description')
            file = request.FILES.get('file')
            
            if not title or not file:
                messages.error(request, 'Title and file are required')
                return JsonResponse({'success': False, 'error': 'Missing required fields'})
            
            # Upload file to Firebase
            firebase_url, message = FirebaseAdminView().handle_file_upload(
                file, 'model_sets', title
            )
            
            if firebase_url:
                # Create Model Set with Firebase URL
                modelset = ModelSet.objects.create(
                    title=title,
                    description=description,
                    file=firebase_url  # Store Firebase URL instead of local path
                )
                
                messages.success(request, f'Model Set uploaded successfully! {message}')
                return JsonResponse({
                    'success': True,
                    'message': 'Model Set uploaded to Firebase successfully!',
                    'url': firebase_url,
                    'modelset_id': str(modelset._id)
                })
            else:
                return JsonResponse({'success': False, 'error': message})
                
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return JsonResponse({'success': False, 'error': str(e)})
    
    return render(request, 'admin/firebase_upload_modelset.html')

@login_required
def firebase_upload_job(request):
    """
    Upload Job with Firebase storage (for job documents/attachments)
    """
    if request.method == 'POST':
        try:
            title = request.POST.get('title')
            company = request.POST.get('company')
            location = request.POST.get('location')
            description = request.POST.get('description')
            document = request.FILES.get('document')  # Optional job document
            
            if not title or not company:
                messages.error(request, 'Title and company are required')
                return JsonResponse({'success': False, 'error': 'Missing required fields'})
            
            document_url = None
            if document:
                # Upload document to Firebase
                firebase_url, message = FirebaseAdminView().handle_file_upload(
                    document, 'jobs', title
                )
                document_url = firebase_url
            
            # Create Job with Firebase URL (if document provided)
            # Note: Job model doesn't have a document field, so we'll store the URL in more_details
            job = Job.objects.create(
                title=title,
                position=company,  # Using company as position
                location=location,
                opening_date=timezone.now().date(),
                application_deadline=timezone.now().date() + timedelta(days=30),
                more_details=document_url if document_url else '',  # Store Firebase URL
                job_type='job'
            )
            
            if document_url:
                messages.success(request, f'Job posted with document! {message}')
            else:
                messages.success(request, 'Job posted successfully!')
            
            return JsonResponse({
                'success': True,
                'message': 'Job posted successfully!',
                'document_url': document_url,
                'job_id': str(job._id)
            })
                
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return JsonResponse({'success': False, 'error': str(e)})
    
    return render(request, 'admin/firebase_upload_job.html')

@login_required
def firebase_upload_objective(request):
    """
    Upload Objective with Firebase storage (for objective documents)
    """
    if request.method == 'POST':
        try:
            subject_name = request.POST.get('subject_name')
            description = request.POST.get('description')
            document = request.FILES.get('document')  # Optional objective document
            
            if not subject_name:
                messages.error(request, 'Subject name is required')
                return JsonResponse({'success': False, 'error': 'Subject name is required'})
            
            document_url = None
            if document:
                # Upload document to Firebase
                firebase_url, message = FirebaseAdminView().handle_file_upload(
                    document, 'objectives', subject_name
                )
                document_url = firebase_url
            
            # Create Objective Subject with Firebase URL (if document provided)
            # Note: ObjectiveSubject doesn't have a document field, but we can store the URL in description
            objective_subject = ObjectiveSubject.objects.create(
                name=subject_name,
                description=f"{description}\n\nDocument URL: {document_url}" if document_url else description
            )
            
            if document_url:
                messages.success(request, f'Objective created with document! {message}')
            else:
                messages.success(request, 'Objective created successfully!')
            
            return JsonResponse({
                'success': True,
                'message': 'Objective created successfully!',
                'document_url': document_url
            })
                
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return JsonResponse({'success': False, 'error': str(e)})
    
    return render(request, 'admin/firebase_upload_objective.html')

@login_required
def firebase_upload_subjective(request):
    """
    Upload Subjective with Firebase storage (for subjective documents)
    """
    if request.method == 'POST':
        try:
            subject_name = request.POST.get('subject_name')
            description = request.POST.get('description')
            document = request.FILES.get('document')  # Optional subjective document
            
            if not subject_name:
                messages.error(request, 'Subject name is required')
                return JsonResponse({'success': False, 'error': 'Subject name is required'})
            
            document_url = None
            if document:
                # Upload document to Firebase
                firebase_url, message = FirebaseAdminView().handle_file_upload(
                    document, 'subjectives', subject_name
                )
                document_url = firebase_url
            
            # Create Subjective Subject with Firebase URL (if document provided)
            # Note: SubjectiveSubject doesn't have a document field, but we can store the URL in a custom field
            # For now, we'll just create the subject without document storage
            subjective_subject = SubjectiveSubject.objects.create(
                name=subject_name
            )
            
            if document_url:
                messages.success(request, f'Subjective created with document! {message}')
            else:
                messages.success(request, 'Subjective created successfully!')
            
            return JsonResponse({
                'success': True,
                'message': 'Subjective created successfully!',
                'document_url': document_url
            })
                
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return JsonResponse({'success': False, 'error': str(e)})
    
    return render(request, 'admin/firebase_upload_subjective.html') 