"""
URL configuration for annotator app
The `urlpatterns` list routes URLs to views.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Project management
    path('project/create/', views.project_create, name='project_create'),
    path('project/<int:project_id>/', views.project_detail, name='project_detail'),
    path('project/<int:project_id>/edit/', views.project_edit, name='project_edit'),
    path('project/<int:project_id>/export-dataset/', views.project_export_dataset, name='project_export_dataset'),
    
    # Video management 
    path('video/<int:video_id>/extract/', views.video_extract_frames, name='video_extract_frames'),
    path('video/<int:video_id>/annotate/', views.video_annotate, name='video_annotate'),
    path('video/<int:video_id>/export/', views.video_export, name='video_export'),
    path('video/<int:video_id>/delete/', views.video_delete, name='video_delete'),
    path('video/<int:video_id>/annotated-frames/', views.video_toggle_annotated_view, name='video_toggle_annotated'),
    
    # Frame operations (API endpoints)
    path('frame/<int:frame_id>/data/', views.frame_get_data, name='frame_get_data'),
    path('frame/<int:frame_id>/save/', views.frame_save_annotation, name='frame_save_annotation'),
    path('frame/<int:frame_id>/unmark/', views.frame_unmark, name='frame_unmark'),
    path('frame/<int:frame_id>/navigate/<str:direction>/', views.frame_navigate, name='frame_navigate'),
]
