"""
Admin configuration for annotation models
"""
from django.contrib import admin
from .models import Project, Video, Frame


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Admin configuration for Project model.
    
    Displays project name, creation time, and statistics about annotated videos.
    Allows filtering by creation date and searching by name or description.
    """
    list_display = ['name', 'created_at', 'get_total_videos', 'get_annotated_videos']
    search_fields = ['name', 'description']
    list_filter = ['created_at']
    date_hierarchy = 'created_at'


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """Admin configuration for Video model.
    
    Displays video name, associated project, extraction/annotation status,
    frame counts, and upload timestamp. Filterable by status and project.
    """
    list_display = ['name', 'project', 'status', 'total_frames', 'annotated_frames', 'uploaded_at']
    list_filter = ['status', 'project', 'uploaded_at']
    search_fields = ['name', 'project__name']
    date_hierarchy = 'uploaded_at'


@admin.register(Frame)
class FrameAdmin(admin.ModelAdmin):
    """Admin configuration for Frame model.
    
    Displays frame information including video reference, frame number,
    annotation status, and creation time. Filterable by annotation status and project.
    """
    list_display = ['video', 'frame_number', 'is_annotated', 'created_at']
    list_filter = ['is_annotated', 'video__project']
    search_fields = ['video__name']
    date_hierarchy = 'created_at'

