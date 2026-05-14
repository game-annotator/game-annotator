"""
Forms for the annotation tool
"""
from django import forms
from .models import Project, Video


class ProjectForm(forms.ModelForm):
    """Form for creating and editing annotation projects.
    
    Fields:
        name: Project name (unique)
        description: Detailed project description
        initial_array_text: Initial game state template as text
    """
    initial_array_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 8,
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm',
            'placeholder': '00000\n00000\n00000'
        }),
        required=False,
        label='Initial Game State',
        help_text='Enter the starting state in any format you prefer'
    )

    class Meta:
        model = Project
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'e.g., Chess Tournament Dataset'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Project description...'
            })
        }

    def __init__(self, *args, **kwargs):
        """Initialize form with instance data if provided."""
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.initial_array:
            self.fields['initial_array_text'].initial = self.instance.initial_array

    def save(self, commit=True):
        """Save form and map initial_array_text to initial_array field.
        
        Args:
            commit (bool): Whether to save to database immediately.
            
        Returns:
            Project: The saved Project instance.
        """
        instance = super().save(commit=False)
        instance.initial_array = self.cleaned_data.get('initial_array_text', '')
        if commit:
            instance.save()
        return instance


class VideoUploadForm(forms.ModelForm):
    """Form for uploading and configuring video files.
    
    Allows users to specify video name, file, rotation, and flip settings.
    """
    class Meta:
        model = Video
        fields = ['name', 'video_file', 'is_flipped', 'rotation_angle']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Video name'
            }),
            'video_file': forms.FileInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'accept': 'video/*'
            }),
            'is_flipped': forms.CheckboxInput(attrs={
                'class': 'rounded border-gray-300 text-blue-600 focus:ring-blue-500'
            }),
            'rotation_angle': forms.Select(attrs={
                'class': 'px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            })
        }


class FrameExtractionForm(forms.Form):
    """Form for configuring frame extraction options from videos.
    
    Supports three algorithms (full, uniform, sampling) with algorithm-specific parameters
    for controlling frame extraction behavior and time range selection.
    """
    ALGORITHM_CHOICES = [
        ('full', 'Full Extraction'),
        ('uniform', 'Uniform Sampling'),
        ('sampling', 'Random Sampling'),
    ]

    algorithm = forms.ChoiceField(
        choices=ALGORITHM_CHOICES,
        initial='full',
        label='Extraction Algorithm',
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'id': 'id_algorithm'
        })
    )

    # --- Full Extraction fields ---
    fps = forms.FloatField(
        initial=1,
        min_value=0.1,
        max_value=60,
        required=False,
        label='Frames Per Second',
        help_text='How many frames to pull per second of video',
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'step': '0.1',
            'id': 'id_fps'
        })
    )

    # --- Uniform / Sampling shared field ---
    target_frames = forms.IntegerField(
        initial=100,
        min_value=1,
        required=False,
        label='Target Frame Count',
        help_text='Total number of frames to extract',
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'id': 'id_target_frames'
        })
    )

    # --- Shared time range ---
    start_time = forms.FloatField(
        initial=0,
        min_value=0,
        required=False,
        label='Start Time (seconds)',
        help_text='Leave at 0 for beginning',
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'step': '0.1',
            'id': 'id_start_time'
        })
    )

    end_time = forms.FloatField(
        required=False,
        min_value=0,
        label='End Time (seconds)',
        help_text='Leave blank to extract until the end',
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'step': '0.1',
            'id': 'id_end_time'
        })
    )

    def clean(self):
        """Apply algorithm-specific default values for missing fields.
        
        Sets default fps=1.0 for full extraction and target_frames=100
        for uniform/sampling algorithms if not provided.
        
        Returns:
            dict: Cleaned form data with defaults applied.
        """
        cleaned = super().clean()
        algo = cleaned.get('algorithm')
        if algo == 'full' and not cleaned.get('fps'):
            cleaned['fps'] = 1.0
        if algo in ('uniform', 'sampling') and not cleaned.get('target_frames'):
            cleaned['target_frames'] = 100
        return cleaned
