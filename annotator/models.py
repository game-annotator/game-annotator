"""
Models for the game annotation tool
"""
from django.db import models
from django.core.validators import FileExtensionValidator


class Project(models.Model):
    """Represents an annotation project containing multiple videos"""
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    initial_array = models.TextField(default='', blank=True, help_text="Initial game state template")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        """Return the project name as string representation."""
        return self.name
    
    def get_total_videos(self):
        """Get the total count of videos in this project.
        
        Returns:
            int: Number of videos associated with this project.
        """
        return self.videos.count()
    
    def get_annotated_videos(self):
        """Get the count of completed videos in this project.
        
        Returns:
            int: Number of videos with status 'completed'.
        """
        return self.videos.filter(status='completed').count()


class Video(models.Model):
    """Represents a video file to be annotated"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('extracting', 'Extracting Frames'),
        ('ready', 'Ready for Annotation'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='videos')
    name = models.CharField(max_length=255)
    video_file = models.FileField(
        upload_to='videos/',
        validators=[FileExtensionValidator(['mp4', 'avi', 'mov', 'mkv', 'webm'])]
    )
    is_flipped = models.BooleanField(default=False, help_text="Video needs to be rotated")
    rotation_angle = models.IntegerField(default=0, choices=[(0, '0°'), (90, '90°'), (180, '180°'), (270, '270°')])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_frames = models.IntegerField(default=0)
    annotated_frames = models.IntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['uploaded_at']
        unique_together = ['project', 'name']
    
    def __str__(self):
        """Return string representation of video with project and name."""
        return f"{self.project.name} - {self.name}"
    
    def get_progress_percentage(self):
        """Calculate annotation progress as a percentage.
        
        Returns:
            int: Percentage of frames that have been annotated (0-100).
        """
        if self.total_frames == 0:
            return 0
        return int((self.annotated_frames / self.total_frames) * 100)


class Frame(models.Model):
    """Represents an extracted frame from a video"""
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='frames')
    frame_number = models.IntegerField()
    image_path = models.CharField(max_length=500)
    is_annotated = models.BooleanField(default=False)
    annotation_data = models.TextField(null=True, blank=True, help_text="Game state annotation (plain text)")
    created_at = models.DateTimeField(auto_now_add=True)
    annotated_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['frame_number']
        unique_together = ['video', 'frame_number']
    
    def __str__(self):
        """Return string representation of frame with video and frame number."""
        return f"{self.video.name} - Frame {self.frame_number}"
    
    def get_next_frame(self):
        """Get the next frame in sequence"""
        return Frame.objects.filter(
            video=self.video,
            frame_number__gt=self.frame_number
        ).first()
    
    def get_previous_frame(self):
        """Get the previous frame in sequence"""
        return Frame.objects.filter(
            video=self.video,
            frame_number__lt=self.frame_number
        ).last()
    
    def get_next_annotated_frame(self):
        """Get the next annotated frame"""
        return Frame.objects.filter(
            video=self.video,
            frame_number__gt=self.frame_number,
            is_annotated=True
        ).first()
    
    def get_previous_annotated_frame(self):
        """Get the previous annotated frame"""
        return Frame.objects.filter(
            video=self.video,
            frame_number__lt=self.frame_number,
            is_annotated=True
        ).last()
