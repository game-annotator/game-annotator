"""
Management command to extract frames from videos.

Three algorithms:
  full      – walks the video at a fixed FPS interval (dense extraction).
  uniform   – picks exactly N frames spaced evenly across the time range.
  sampling  – picks exactly N frames at random positions across the time range.
"""
import random
from django.core.management.base import BaseCommand
from annotator.models import Video, Frame
import cv2
from pathlib import Path


class Command(BaseCommand):
    """Django management command for extracting frames from video files.
    
    Supports three extraction algorithms:
        - full: Extract frames at a fixed FPS interval (dense extraction)
        - uniform: Pick exactly N frames evenly spaced across the video
        - sampling: Pick exactly N frames at random positions
    
    Handles video rotation, frame numbering, and database record creation.
    """
    help = 'Extract frames from a video using full / uniform / sampling algorithms'

    def add_arguments(self, parser):
        """Define command-line arguments for frame extraction.
        
        Args:
            parser: Django argument parser
            
        Options:
            --video_id: ID of the video to process (required)
            --algorithm: Extraction algorithm (full/uniform/sampling, default: full)
            --fps: Frames per second for full extraction (default: 1)
            --target_frames: Target frame count for uniform/sampling (default: 100)
            --start_time: Start time in seconds (default: 0)
            --end_time: End time in seconds (default: end of video)
        """
        parser.add_argument('--video_id', type=int, required=True)
        parser.add_argument('--algorithm', type=str, default='full',
                            choices=['full', 'uniform', 'sampling'])
        parser.add_argument('--fps', type=float, default=1)
        parser.add_argument('--target_frames', type=int, default=100)
        parser.add_argument('--start_time', type=float, default=0)
        parser.add_argument('--end_time', type=float, default=None)

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _rotate(img, angle):
        """Rotate an image by the specified angle.
        
        Args:
            img: OpenCV image array
            angle: Rotation angle in degrees (0, 90, 180, or 270)
            
        Returns:
            Rotated image array, or original if angle is 0.
        """
        if angle == 90:
            return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        if angle == 180:
            return cv2.rotate(img, cv2.ROTATE_180)
        if angle == 270:
            return cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        return img

    def _save_frame(self, cap, video, output_dir, frame_index, seq):
        """Seek to frame_index, read, rotate, write to disk, create DB row.
        
        Args:
            cap: OpenCV VideoCapture object
            video: Video model instance
            output_dir: Directory path to save frame images
            frame_index: Frame index to seek to in video
            seq: Sequence number for naming the output frame
            
        Returns:
            bool: True if frame was successfully saved, False otherwise.
        """
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ret, img = cap.read()
        if not ret:
            return False
        img = self._rotate(img, video.rotation_angle if video.is_flipped else 0)
        filename = f'frame_{seq:06d}.jpg'
        cv2.imwrite(str(output_dir / filename), img)
        Frame.objects.create(
            video=video,
            frame_number=seq,
            image_path=f'/media/frames/{video.project.id}/{video.id}/{filename}'
        )
        return True

    # ------------------------------------------------------------------
    # algorithms
    # ------------------------------------------------------------------
    def _extract_full(self, cap, video, output_dir, video_fps, start_frame, end_frame):
        """Extract frames at fixed FPS interval (dense extraction).
        
        Walks through every frame in the specified range and keeps one frame
        every (video_fps / target_fps) frames based on the configured fps parameter.
        
        Args:
            cap: OpenCV VideoCapture object
            video: Video model instance
            output_dir: Directory path to save frame images
            video_fps: Original video FPS
            start_frame: Starting frame index
            end_frame: Ending frame index
            
        Returns:
            int: Number of frames extracted.
        """
        interval = max(1, int(video_fps / self._fps))
        seq = 0
        idx = start_frame
        while idx < end_frame:
            if self._save_frame(cap, video, output_dir, idx, seq):
                seq += 1
                if seq % 100 == 0:
                    self.stdout.write(f'  extracted {seq} frames …')
            idx += interval
        return seq

    def _extract_uniform(self, cap, video, output_dir, video_fps, start_frame, end_frame):
        """Extract frames uniformly spaced across the video duration.
        
        Picks exactly target_frames positions spread evenly across the specified range,
        including both start and end frames in the distribution.
        
        Args:
            cap: OpenCV VideoCapture object
            video: Video model instance
            output_dir: Directory path to save frame images
            video_fps: Original video FPS
            start_frame: Starting frame index
            end_frame: Ending frame index
            
        Returns:
            int: Number of frames extracted.
        """
        total_range = end_frame - start_frame
        if total_range <= 0:
            return 0
        count = min(self._target_frames, total_range)
        # linspace-style: evenly spaced indices including both ends
        if count == 1:
            positions = [start_frame]
        else:
            step = (total_range - 1) / (count - 1)
            positions = [int(start_frame + i * step) for i in range(count)]
        seq = 0
        for idx in positions:
            if self._save_frame(cap, video, output_dir, idx, seq):
                seq += 1
        return seq

    def _extract_sampling(self, cap, video, output_dir, video_fps, start_frame, end_frame):
        """Extract frames at random positions across the video duration.
        
        Picks exactly target_frames positions at random across the specified range.
        Frames are extracted in chronological order despite random selection.
        
        Args:
            cap: OpenCV VideoCapture object
            video: Video model instance
            output_dir: Directory path to save frame images
            video_fps: Original video FPS
            start_frame: Starting frame index
            end_frame: Ending frame index
            
        Returns:
            int: Number of frames extracted.
        """
        total_range = end_frame - start_frame
        if total_range <= 0:
            return 0
        count = min(self._target_frames, total_range)
        positions = sorted(random.sample(range(start_frame, end_frame), count))
        seq = 0
        for idx in positions:
            if self._save_frame(cap, video, output_dir, idx, seq):
                seq += 1
        return seq

    # ------------------------------------------------------------------
    # main
    # ------------------------------------------------------------------
    def handle(self, *args, **options):
        """Main command handler for frame extraction.
        
        Orchestrates the frame extraction process:
        1. Retrieves video from database
        2. Opens video file with OpenCV
        3. Applies selected extraction algorithm
        4. Updates video status and frame count in database
        
        Args:
            options: Command-line options dictionary
            
        Raises:
            Exception: If video file cannot be opened or extraction fails.
        """
        video_id      = options['video_id']
        algorithm     = options['algorithm']
        self._fps     = options['fps']
        self._target_frames = options['target_frames']
        start_time    = options['start_time'] or 0
        end_time      = options['end_time']

        try:
            video = Video.objects.get(id=video_id)
        except Video.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Video {video_id} not found'))
            return

        video.status = 'extracting'
        video.save()

        output_dir = Path('media') / 'frames' / str(video.project.id) / str(video.id)
        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            cap = cv2.VideoCapture(video.video_file.path)
            if not cap.isOpened():
                raise Exception('Could not open video file')

            video_fps        = cap.get(cv2.CAP_PROP_FPS)
            total_vid_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            start_frame = int(start_time * video_fps)
            end_frame   = int(end_time * video_fps) if end_time else total_vid_frames
            end_frame   = min(end_frame, total_vid_frames)

            # clear previous extraction
            Frame.objects.filter(video=video).delete()

            self.stdout.write(
                f'Algorithm: {algorithm} | range: frame {start_frame}–{end_frame} '
                f'| video fps: {video_fps}'
            )

            if algorithm == 'full':
                extracted = self._extract_full(cap, video, output_dir, video_fps, start_frame, end_frame)
            elif algorithm == 'uniform':
                extracted = self._extract_uniform(cap, video, output_dir, video_fps, start_frame, end_frame)
            else:  # sampling
                extracted = self._extract_sampling(cap, video, output_dir, video_fps, start_frame, end_frame)

            cap.release()

            video.total_frames = extracted
            video.status = 'ready'
            video.save()

            self.stdout.write(self.style.SUCCESS(
                f'Done — extracted {extracted} frames ({algorithm})'
            ))

        except Exception as e:
            video.status = 'pending'
            video.save()
            self.stdout.write(self.style.ERROR(f'Extraction failed: {e}'))
            raise
