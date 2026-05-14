# GameAnnotator

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE.md)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/django-5.1+-green.svg)](https://www.djangoproject.com/)
[![codecov](https://codecov.io/gh/game-annotator/game-annotator/branch/main/graph/badge.svg)](https://codecov.io/gh/game-annotator/game-annotator)
[![Documentation](https://img.shields.io/badge/docs-online-blue.svg)](https://game-annotator.github.io/game-annotator/)

A Django web application for annotating board game videos frame-by-frame.


## Features

### ✨ Core Functionality

- **Project Management**: Create and organize multiple annotation projects
- **Video Upload**: Support for MP4, AVI, MOV, MKV, and WebM formats
- **Video Rotation**: Handle mobile videos that need rotation (90°, 180°, 270°)
- **Frame Extraction**: Extract frames at custom FPS with start/end time control
- **Dual-Pane Annotation Interface**: 
  - Left pane: Shows last annotated frame for reference
  - Right pane: Current frame with editable JSON annotation
- **Keyboard Shortcuts**: 
  - `←` / `→` : Navigate between frames
  - `Ctrl+S` : Save annotation
  - `Ctrl+→` : Skip 5 frames
  - `Shift+→` : Skip 10 frames
  - `Ctrl+G` : Custom skip amount
- **Annotated-Only View**: Toggle to view only annotated frames for verification
- **Progress Tracking**: Real-time progress indicators and statistics
- **Export Options**: Export annotations as JSON, CSV, or COCO JSON per video; full dataset ZIP per project

### 🎮 Game State Annotation

- Initial game state array configurable per project
- **Free-text annotation** — any format works: JSON, plain text, FEN, custom notation
- Automatic loading of initial state for new frames
- Reference to previous annotation visible while working

## Installation

### Prerequisites

- Python 3.8+
- Django 5.1+
- OpenCV (for frame extraction)
- Pillow (for image handling)

### Setup

1. **Install Dependencies**

```bash
pip install -r requirements.txt
```

2. **Configure Environment**

```bash
cp .env.example .env
```

Open `.env` and set a secret key (generate one with the command below):

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

3. **Navigate to Project Directory**

```bash
cd game_annotator
```

4. **Run Migrations**

```bash
python manage.py migrate
```

5. **Create Superuser (Optional)**

```bash
python manage.py createsuperuser
```

6. **Run Development Server**

```bash
python manage.py runserver
```

7. **Access Application**

Open your browser to: `http://localhost:8000`

## Usage Guide

### 1. Create a Project

1. Click "New Project" in the navigation bar
2. Enter project name and description
3. Optionally define an initial game state template (any format — plain text, JSON, FEN, custom notation). This is pre-filled into every new frame so you only need to edit what changed.
4. Click "Create Project"

**Example initial state (JSON — but any text works):**
```json
{
  "board": [
    [0, 0, 0],
    [0, 0, 0],
    [0, 0, 0]
  ],
  "current_player": 1,
  "score": [0, 0]
}
```

### 2. Upload Videos

1. Open your project
2. Fill in the video upload form:
   - Enter a descriptive name
   - Select video file
   - Check "Video needs rotation" if mobile video is sideways
   - Select rotation angle if needed
3. Click "Upload Video"

### 3. Extract Frames

1. Click "Extract Frames" on a video
2. Configure extraction settings:
   - **FPS**: Frames per second (1 = 1 frame/second)
   - **Start Time**: Optional start point in seconds
   - **End Time**: Optional end point in seconds
3. Click "Extract Frames"
4. Wait for extraction to complete

### 4. Annotate Frames

1. Click "Annotate" on a video with extracted frames
2. The annotation interface shows:
   - **Left Pane**: Last annotated frame for reference
   - **Right Pane**: Current frame to annotate
3. Edit the annotation text (any format — JSON, plain text, FEN, custom notation)
4. Click "Save Annotation" or press `Ctrl+S`
5. Navigate using:
   - Arrow buttons or keyboard shortcuts
   - Skip buttons for faster navigation
   - Custom skip for large jumps

### 5. Verify Annotations

1. Click "Show Annotated Only" button
2. Review only frames with annotations
3. Use navigation to check your work
4. Click "Show All Frames" to return to normal mode

### 6. Export Data

1. Once video is completed, click **Export** next to a video and choose a format: **JSON**, **CSV**, or **COCO JSON**. The file downloads directly to your browser.
2. To export the full project as a ZIP, use the **Export Dataset** button at the top of the project page.

## Project Structure

```
game_annotator/
├── game_annotator/          # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── annotator/               # Main application
│   ├── models.py           # Database models
│   ├── views.py            # View logic
│   ├── forms.py            # Form definitions
│   ├── urls.py             # URL routing
│   ├── admin.py            # Admin interface
│   ├── templates/          # HTML templates
│   │   └── annotator/
│   │       ├── base.html
│   │       ├── dashboard.html
│   │       ├── project_form.html
│   │       ├── project_detail.html
│   │       ├── frame_extraction.html
│   │       └── annotate.html
│   └── management/
│       └── commands/
│           └── extract_frames.py
├── media/                   # User uploads (gitignored)
│   ├── videos/             # Uploaded videos
│   └── frames/             # Extracted frames
├── manage.py
└── requirements.txt
```

## Database Models

### Project
- Name, description
- Initial game state array (JSON/TXT)
- Timestamps

### Video
- Foreign key to Project
- Video file, name
- Rotation settings
- Status (pending, extracting, ready, in_progress, completed)
- Frame counts and progress

### Frame
- Foreign key to Video
- Frame number, image path
- Annotation data (JSON/TXT)
- Annotation status and timestamp

## Keyboard Shortcuts Reference

| Shortcut | Action |
|----------|--------|
| `←` / `→` | Previous / next frame |
| `Ctrl+S` | Save annotation and advance |
| `Ctrl+→` | Skip 5 frames forward |
| `Shift+→` | Skip 10 frames forward |
| `Ctrl+G` | Custom skip amount |
| `Ctrl+=` | Increase annotation font size |
| `Ctrl+-` | Decrease annotation font size |
| `Z` | Open image zoom overlay |
| `Escape` | Close zoom overlay |

## Tips and Best Practices

### Frame Extraction
- Use 1 FPS for slower games (chess, turn-based)
- Use 2-5 FPS for medium-paced games
- Use higher FPS (5-10) for fast action games
- Extract only relevant portions using start/end time
- Consider disk space: 10 min @ 1 FPS = ~600 frames

### Annotation
- Keep annotation format consistent across all frames in a project
- Use the reference pane to maintain continuity
- Save frequently (Ctrl+S)
- Use skip features to avoid annotating redundant frames
- Verify work using "Show Annotated Only" mode

### JSON Format Examples

**Chess:**
```json
{
  "board": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR",
  "turn": "white",
  "castling": "KQkq",
  "enPassant": "-"
}
```

**Tic-Tac-Toe:**
```json
{
  "board": [
    ["X", "O", " "],
    [" ", "X", " "],
    [" ", " ", "O"]
  ],
  "current_player": "X",
  "winner": null
}
```

**Card Game:**
```json
{
  "player_hands": [
    ["AH", "KD", "QS"],
    ["2C", "3H", "4D"]
  ],
  "table_cards": ["5S", "6H"],
  "current_player": 0,
  "phase": "betting"
}
```

## Troubleshooting

### Frame Extraction Issues
- **Error: Could not open video file**
  - Check video format is supported
  - Try re-encoding video with VLC or FFmpeg
  
- **Frames are sideways**
  - Enable rotation and select appropriate angle
  - Test with one frame extraction first

### Annotation Issues
- **JSON validation error**
  - Check for missing brackets, commas, or quotes
  - Use a JSON validator online
  
- **Slow performance**
  - Reduce frame extraction FPS
  - Use skip features instead of annotating every frame

## Future Enhancements

- Collaborative annotation (multi-user)
- AI-assisted annotation suggestions
- Video playback with annotations overlay
- Batch operations across frames
- Advanced search and filtering

## License

Released under the [GNU General Public License v3.0](LICENSE.md).
© 2026 Pankaj Kumar G, Arun Kumar M N, Anitha M L

## Support

For issues or questions:
1. Check the documentation above
2. Review the example annotation formats
3. Verify your JSON syntax
4. Check the Django logs for errors

---

**Happy Annotating! 🎮📊**
