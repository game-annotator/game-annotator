"""
Views for the game annotation tool
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q
from django.conf import settings
from .models import Project, Video, Frame
from .forms import ProjectForm, VideoUploadForm, FrameExtractionForm
import csv
import json
import os


def dashboard(request):
    """Display the main dashboard with all projects and statistics.
    
    Shows a list of all projects with annotation progress metrics including
    total videos and completed videos per project.
    
    Args:
        request: HTTP request object
        
    Returns:
        HttpResponse: Rendered dashboard template with project list.
    """
    projects = Project.objects.annotate(
        video_count=Count('videos'),
        completed_count=Count('videos', filter=Q(videos__status='completed'))
    )
    return render(request, 'annotator/dashboard.html', {'projects': projects})


def project_create(request):
    """Create a new annotation project.
    
    Displays a form for creating a new project. On POST, validates and saves
    the project, then redirects to the project detail view.
    
    Args:
        request: HTTP request object
        
    Returns:
        HttpResponse: Rendered form or redirect to project detail on success.
    """
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            messages.success(request, f'Project "{project.name}" created successfully!')
            return redirect('project_detail', project_id=project.id)
    else:
        form = ProjectForm()
    
    return render(request, 'annotator/project_form.html', {'form': form, 'title': 'Create Project'})


def project_detail(request, project_id):
    """Display project details and manage videos.
    
    Shows all videos in a project with their annotation status. Provides
    a form for uploading new videos to the project.
    
    Args:
        request: HTTP request object
        project_id: ID of the project to display
        
    Returns:
        HttpResponse: Rendered project detail template.
    """
    project = get_object_or_404(Project, id=project_id)
    videos = project.videos.all()
    
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            video.project = project
            video.save()
            messages.success(request, f'Video "{video.name}" uploaded successfully!')
            return redirect('project_detail', project_id=project.id)
    else:
        form = VideoUploadForm()
    
    return render(request, 'annotator/project_detail.html', {
        'project': project,
        'videos': videos,
        'form': form,
        'completed_count': videos.filter(status='completed').count(),
        'in_progress_count': videos.filter(status='in_progress').count(),
    })


def project_edit(request, project_id):
    """Edit project information.
    
    Allows updating project name and description. On POST, saves changes
    and redirects back to project detail.
    
    Args:
        request: HTTP request object
        project_id: ID of the project to edit
        
    Returns:
        HttpResponse: Rendered form or redirect on success.
    """
    project = get_object_or_404(Project, id=project_id)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project updated successfully!')
            return redirect('project_detail', project_id=project.id)
    else:
        form = ProjectForm(instance=project)
    
    return render(request, 'annotator/project_form.html', {
        'form': form,
        'title': 'Edit Project',
        'project': project
    })


def video_extract_frames(request, video_id):
    """Extract frames from video using selected algorithm.
    
    Displays frame extraction options and processes the extraction request.
    On POST, calls the extract_frames management command with specified parameters.
    
    Args:
        request: HTTP request object
        video_id: ID of the video to extract frames from
        
    Returns:
        HttpResponse: Rendered extraction form or redirect on completion.
    """
    video = get_object_or_404(Video, id=video_id)
    
    if request.method == 'POST':
        form = FrameExtractionForm(request.POST)
        if form.is_valid():
            from django.core.management import call_command
            try:
                call_command(
                    'extract_frames',
                    video_id=video.id,
                    algorithm=form.cleaned_data.get('algorithm', 'full'),
                    fps=form.cleaned_data.get('fps') or 1,
                    target_frames=form.cleaned_data.get('target_frames') or 100,
                    start_time=form.cleaned_data.get('start_time') or 0,
                    end_time=form.cleaned_data.get('end_time')
                )
                messages.success(request, 'Frames extracted successfully!')
                return redirect('video_annotate', video_id=video.id)
            except Exception as e:
                messages.error(request, f'Error extracting frames: {str(e)}')
    else:
        form = FrameExtractionForm()
    
    return render(request, 'annotator/frame_extraction.html', {
        'video': video,
        'form': form
    })


def video_annotate(request, video_id):
    """Display the main annotation interface for a video.
    
    Shows the current frame to be annotated along with the previously annotated frame
    for reference. Starts with the first unannotated frame or the first frame if all
    are annotated.
    
    Args:
        request: HTTP request object
        video_id: ID of the video to annotate
        
    Returns:
        HttpResponse: Rendered annotation interface, or redirect if no frames available.
    """
    video = get_object_or_404(Video, id=video_id)
    
    # Get first unannotated frame or first frame
    current_frame = Frame.objects.filter(
        video=video,
        is_annotated=False
    ).first() or video.frames.first()
    
    if not current_frame:
        messages.warning(request, 'No frames available. Please extract frames first.')
        return redirect('video_extract_frames', video_id=video.id)
    
    # Get last annotated frame for reference
    last_annotated = Frame.objects.filter(
        video=video,
        is_annotated=True,
        frame_number__lt=current_frame.frame_number
    ).order_by('-frame_number').first()
    return render(request, 'annotator/annotate.html', {
        'video': video,
        'project': video.project,
        'current_frame': current_frame,
        'last_annotated': last_annotated,
        'total_frames': video.frames.count(),
        'annotated_count': video.frames.filter(is_annotated=True).count()
    })


@require_http_methods(["POST"])
def frame_save_annotation(request, frame_id):
    """Save plain text annotation for a frame.
    
    Accepts POST request with annotation text and saves it to the frame.
    Updates video status to 'in_progress' or 'completed' based on progress.
    
    Args:
        request: HTTP POST request with JSON body containing 'annotation' key
        frame_id: ID of the frame to annotate
        
    Returns:
        JsonResponse: Success status and updated frame count, or error message.
    """
    frame = get_object_or_404(Frame, id=frame_id)
    
    try:
        data = json.loads(request.body)
        annotation_text = data.get('annotation', '')
        
        frame.annotation_data = annotation_text
        frame.is_annotated = True
        frame.annotated_at = timezone.now()
        frame.save()
        
        # Update video stats
        video = frame.video
        video.annotated_frames = video.frames.filter(is_annotated=True).count()
        if video.annotated_frames == video.total_frames:
            video.status = 'completed'
            video.completed_at = timezone.now()
        else:
            video.status = 'in_progress'
        video.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Annotation saved successfully',
            'annotated_count': video.annotated_frames
        })
    
    except Exception:
        return JsonResponse({'error': 'Failed to save annotation'}, status=500)


@require_http_methods(["GET"])
def frame_get_data(request, frame_id):
    """Retrieve frame data including image path and annotation.
    
    Returns frame metadata and reference to the previously annotated frame
    for context during annotation.
    
    Args:
        request: HTTP GET request
        frame_id: ID of the frame to retrieve
        
    Returns:
        JsonResponse: Frame data including image URL, annotation text, and navigation info.
    """
    frame = get_object_or_404(Frame, id=frame_id)

    # Get previous annotated relative to THIS frame
    previous_annotated = frame.get_previous_annotated_frame()

    return JsonResponse({
        'id': frame.id,
        'frame_number': frame.frame_number,
        'image_url': frame.image_path,
        'is_annotated': frame.is_annotated,
        'annotation': frame.annotation_data if frame.annotation_data else '',
        'has_next': frame.get_next_frame() is not None,
        'has_previous': frame.get_previous_frame() is not None,

        # Previous annotated frame for reference
        'previous_annotated_id': previous_annotated.id if previous_annotated else None
    })


@require_http_methods(["GET"])
def frame_navigate(request, frame_id, direction):
    """Navigate to next/previous frame or skip by a specified count.
    
    Supports navigation: 'next', 'previous', or 'skip_N' where N is frame count.
    Returns the new frame ID and previous annotated frame for reference.
    
    Args:
        request: HTTP GET request
        frame_id: ID of current frame
        direction: Navigation direction ('next', 'previous', or 'skip_N')
        
    Returns:
        JsonResponse: New frame ID and previous annotated frame, or 404 if unavailable.
    """
    frame = get_object_or_404(Frame, id=frame_id)
    
    target_frame = None

    if direction == 'next':
        target_frame = frame.get_next_frame()

    elif direction == 'previous':
        target_frame = frame.get_previous_frame()

    elif direction.startswith('skip_'):
        try:
            skip_count = int(direction.split('_')[1])
        except (ValueError, IndexError):
            return JsonResponse({'error': 'Invalid direction'}, status=400)
        target_frame = Frame.objects.filter(
            video=frame.video,
            frame_number=frame.frame_number + skip_count
        ).first()

    if target_frame:
        # Compute previous annotated relative to TARGET frame
        previous_annotated = Frame.objects.filter(
            video=frame.video,
            is_annotated=True,
            frame_number__lt=target_frame.frame_number
        ).order_by('-frame_number').first()

        return JsonResponse({
            'frame_id': target_frame.id,
            'previous_annotated_id': previous_annotated.id if previous_annotated else None
        })

    return JsonResponse({'error': 'No frame found'}, status=404)

@require_http_methods(["GET"])
def video_toggle_annotated_view(request, video_id):
    """Get list of all annotated frames in a video.
    
    Returns frame IDs and frame numbers for frames that have been annotated.
    Useful for displaying a summary or navigation list.
    
    Args:
        request: HTTP GET request
        video_id: ID of the video
        
    Returns:
        JsonResponse: List of annotated frame IDs and numbers.
    """
    video = get_object_or_404(Video, id=video_id)
    annotated_frames = Frame.objects.filter(
        video=video,
        is_annotated=True
    ).values('id', 'frame_number')
    
    return JsonResponse({
        'frames': list(annotated_frames)
    })


@require_http_methods(["GET"])
def video_export(request, video_id):
    """Export a video's annotated frames as a direct download.

    Supports three formats via ?format= query param:
      - json  (default): JSON array of {frame_number, image_path, annotation}
      - csv            : CSV with header row
      - coco           : COCO Captions-style JSON
    """
    video = get_object_or_404(Video, id=video_id)
    fmt = request.GET.get('format', 'json')
    frames = video.frames.filter(is_annotated=True).order_by('frame_number')
    safe_name = video.name.replace(' ', '_')

    if fmt == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{safe_name}_annotations.csv"'
        writer = csv.writer(response)
        writer.writerow(['frame_number', 'image_path', 'annotation'])
        for frame in frames:
            writer.writerow([frame.frame_number, frame.image_path, frame.annotation_data or ''])
        return response

    if fmt == 'coco':
        coco_data = _build_coco_data(video, frames)
        response = HttpResponse(json.dumps(coco_data, indent=2), content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="{safe_name}_coco.json"'
        return response

    # default: json
    frames_data = [
        {'frame_number': f.frame_number, 'image_path': f.image_path, 'annotation': f.annotation_data or ''}
        for f in frames
    ]
    response = HttpResponse(json.dumps(frames_data, indent=2), content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="{safe_name}_annotations.json"'
    return response


def _build_coco_data(video, frames):
    """Build a COCO Captions-style dict for a video's annotated frames."""
    images = []
    annotations = []
    for frame in frames:
        img_id = frame.frame_number
        images.append({
            'id': img_id,
            'file_name': os.path.basename(frame.image_path),
            'frame_number': frame.frame_number,
        })
        annotations.append({
            'id': img_id,
            'image_id': img_id,
            'caption': frame.annotation_data or '',
        })
    return {
        'info': {
            'description': f'{video.project.name} — {video.name}',
            'version': '1.0',
            'year': timezone.now().year,
        },
        'images': images,
        'annotations': annotations,
        'categories': [],
    }


@require_http_methods(["POST"])
def video_delete(request, video_id):
    """Delete a video and all its extracted frames and annotations.
    
    Removes extracted frame images from disk and the uploaded video file,
    then deletes the video record and cascading Frame records.
    
    Args:
        request: HTTP POST request
        video_id: ID of the video to delete
        
    Returns:
        HttpResponse: Redirect to project detail with success message.
    """
    video = get_object_or_404(Video, id=video_id)
    project_id = video.project.id

    # 1. delete extracted frame images from disk
    frames_dir = os.path.join(settings.MEDIA_ROOT, 'frames', str(video.project.id), str(video.id))
    if os.path.isdir(frames_dir):
        import shutil
        shutil.rmtree(frames_dir)

    # 2. delete the uploaded video file from disk
    if video.video_file and os.path.isfile(video.video_file.path):
        os.remove(video.video_file.path)

    # 3. delete DB row (cascades to Frame)
    video_name = video.name
    video.delete()

    messages.success(request, f'Video "{video_name}" and all its frames have been deleted.')
    return redirect('project_detail', project_id=project_id)


@require_http_methods(["POST"])
def frame_unmark(request, frame_id):
    """Remove annotation from a frame and update video statistics.
    
    Clears the annotation text, resets annotation flag, and updates
    video progress and status accordingly.
    
    Args:
        request: HTTP POST request
        frame_id: ID of the frame to unmark
        
    Returns:
        JsonResponse: Success status and updated frame count.
    """
    frame = get_object_or_404(Frame, id=frame_id)

    frame.annotation_data = None
    frame.is_annotated = False
    frame.annotated_at = None
    frame.save()

    # recalculate video stats
    video = frame.video
    video.annotated_frames = video.frames.filter(is_annotated=True).count()
    if video.status == 'completed':
        video.status = 'in_progress'
    video.save()

    return JsonResponse({
        'success': True,
        'annotated_count': video.annotated_frames
    })


@require_http_methods(["POST"])
def project_export_dataset(request, project_id):
    """Export entire project as a structured ZIP dataset.

    Supports three annotation formats via POST field 'format':
      - txt   (default): one .txt sidecar per frame image
      - csv            : one annotations.csv per video folder
      - coco           : one annotations_coco.json per video folder

    ZIP structure (same for all formats):
        dataset/
            1/        <- video in upload order
                frame_000000.jpg
                frame_000000.txt  (or .csv / coco JSON)
                ...
            2/
                ...
    """
    import shutil
    import zipfile

    project = get_object_or_404(Project, id=project_id)
    fmt = request.POST.get('format', 'txt')
    if fmt not in ('txt', 'csv', 'coco'):
        fmt = 'txt'

    base_tmp = os.path.join(settings.MEDIA_ROOT, '_tmp_export', str(project.id))
    dataset_dir = os.path.join(base_tmp, 'dataset')

    if os.path.isdir(base_tmp):
        shutil.rmtree(base_tmp)
    os.makedirs(dataset_dir, exist_ok=True)

    video_index = 0
    for video in project.videos.order_by('uploaded_at'):
        annotated = list(video.frames.filter(is_annotated=True).order_by('frame_number'))
        if not annotated:
            continue

        video_index += 1
        video_folder = os.path.join(dataset_dir, str(video_index))
        os.makedirs(video_folder, exist_ok=True)

        # copy frame images
        for frame in annotated:
            src_img = frame.image_path.lstrip('/')
            if os.path.isfile(src_img):
                shutil.copy2(src_img, os.path.join(video_folder, os.path.basename(src_img)))

        # write annotation sidecar(s) based on format
        if fmt == 'csv':
            csv_path = os.path.join(video_folder, 'annotations.csv')
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['frame_number', 'image_path', 'annotation'])
                for frame in annotated:
                    writer.writerow([frame.frame_number, frame.image_path, frame.annotation_data or ''])

        elif fmt == 'coco':
            coco_data = _build_coco_data(video, annotated)
            coco_path = os.path.join(video_folder, 'annotations_coco.json')
            with open(coco_path, 'w', encoding='utf-8') as f:
                json.dump(coco_data, f, indent=2)

        else:  # txt — one sidecar .txt per image
            for frame in annotated:
                src_img = frame.image_path.lstrip('/')
                stem = os.path.splitext(os.path.basename(src_img))[0]
                txt_path = os.path.join(video_folder, stem + '.txt')
                with open(txt_path, 'w', encoding='utf-8') as f:
                    f.write(frame.annotation_data or '')

    zip_path = os.path.join(base_tmp, f'{project.name}_dataset.zip')
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(dataset_dir):
            for file in files:
                full = os.path.join(root, file)
                arcname = os.path.relpath(full, base_tmp)
                zf.write(full, arcname)

    with open(zip_path, 'rb') as f:
        zip_bytes = f.read()
    shutil.rmtree(base_tmp)

    response = HttpResponse(zip_bytes, content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{project.name}_dataset.zip"'
    return response
