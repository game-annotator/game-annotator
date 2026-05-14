# Quick Start Guide

## Installation (5 minutes)

### 1. Install Python Dependencies

```bash
cd game_annotator
pip install -r requirements.txt
```

Or manually:
```bash
pip install django pillow opencv-python
```

### 2. Initialize Database

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create Admin User (Optional)

```bash
python manage.py createsuperuser
```

Follow prompts to create username and password.

### 4. Start Server

```bash
python manage.py runserver
```

### 5. Open Browser

Navigate to: **http://localhost:8000**

---

## First Annotation Project (10 minutes)

### Step 1: Create Project

1. Click **"+ New Project"** in top right
2. Fill in:
   - **Name**: "Chess Game Analysis"
   - **Description**: "Annotating chess tournament videos"
   - **Initial Game State**:
   ```json
   {
     "board": [
       ["r","n","b","q","k","b","n","r"],
       ["p","p","p","p","p","p","p","p"],
       [" "," "," "," "," "," "," "," "],
       [" "," "," "," "," "," "," "," "],
       [" "," "," "," "," "," "," "," "],
       [" "," "," "," "," "," "," "," "],
       ["P","P","P","P","P","P","P","P"],
       ["R","N","B","Q","K","B","N","R"]
     ],
     "turn": "white"
   }
   ```
3. Click **"Create Project"**

### Step 2: Upload Video

1. In project page, fill upload form:
   - **Name**: "Game 1 - Player vs Player"
   - **Video File**: Select your video
   - **Rotation**: Check if needed (for mobile videos)
2. Click **"Upload Video"**

### Step 3: Extract Frames

1. Click **"Extract Frames"** button
2. Configure:
   - **FPS**: 1 (one frame per second)
   - **Start Time**: Leave blank (or specify)
   - **End Time**: Leave blank (or specify)
3. Click **"Extract Frames"**
4. Wait for completion (30 seconds - 2 minutes depending on video length)

### Step 4: Annotate

1. Click **"Annotate"** button
2. You'll see:
   - **Left side**: Last annotated frame (reference)
   - **Right side**: Current frame to annotate

3. Edit the JSON to match the game state:
   ```json
   {
     "board": [
       ["r","n","b","q","k","b","n","r"],
       ["p","p","p","p"," ","p","p","p"],
       [" "," "," "," "," "," "," "," "],
       [" "," "," "," ","p"," "," "," "],
       [" "," "," "," ","P"," "," "," "],
       [" "," "," "," "," "," "," "," "],
       ["P","P","P","P"," ","P","P","P"],
       ["R","N","B","Q","K","B","N","R"]
     ],
     "turn": "black"
   }
   ```

4. Press **Ctrl+S** to save and advance to next frame

5. Continue annotating or use:
   - **→** : Next frame
   - **Ctrl+→** : Skip 5 frames
   - **Shift+→** : Skip 10 frames

### Step 5: Verify

1. Click **"Show Annotated Only"** button
2. Navigate through only your annotated frames
3. Verify accuracy
4. Return to normal view

### Step 6: Export

1. Return to project page
2. Click **"Export"** on completed video
3. The file downloads directly to your browser's default download folder.

---

## Common Workflows

### Workflow 1: Quick Annotation (Skip Redundant Frames)

Best for videos where game state doesn't change every frame.

1. Extract at 1 FPS
2. Annotate first frame
3. Use **Shift+→** to skip 10 frames
4. Check if state changed
5. If changed, annotate; if not, skip more
6. Repeat

**Keyboard Sequence**:
```
Ctrl+S (save) → Shift+→ (skip 10) → Edit → Ctrl+S → Shift+→ ...
```

### Workflow 2: Detailed Annotation

Best for detailed move-by-move analysis.

1. Extract at 2-5 FPS
2. Annotate every frame where state changes
3. Use **→** for normal navigation
4. Use **Ctrl+G** for custom skips in slow sections

### Workflow 3: Batch Processing Multiple Videos

1. Upload all videos first
2. Extract frames for all (one at a time)
3. Annotate in sequence
4. Export all when done

---

## Keyboard Shortcuts Cheat Sheet

Print this out for easy reference:

```
┌─────────────────────────────────────────────┐
│         ANNOTATION SHORTCUTS                │
├─────────────────────────────────────────────┤
│  ←              Previous frame              │
│  →              Next frame                  │
│  Ctrl+S         Save annotation             │
│  Ctrl+→         Skip 5 frames forward       │
│  Shift+→        Skip 10 frames forward      │
│  Ctrl+G         Custom skip amount          │
└─────────────────────────────────────────────┘
```

---

## Tips for Efficient Annotation

### 1. Frame Extraction
- Start with 1 FPS for initial tests
- Adjust based on game pace
- Use start/end time to skip intros/outros

### 2. JSON Editing
- Copy initial state as template
- Keep a text editor open with common patterns
- Use find-replace for bulk similar changes

### 3. Workflow Optimization
- Annotate in short sessions (20-30 min)
- Take breaks to maintain accuracy
- Use reference pane to catch mistakes

### 4. Quality Control
- Periodically check with "Annotated Only" view
- Verify first and last frames carefully
- Spot-check middle frames

---

## Example: Simple Tic-Tac-Toe Annotation

### Initial State
```json
{
  "board": [[" "," "," "],[" "," "," "],[" "," "," "]],
  "player": "X",
  "winner": null
}
```

### After First Move
```json
{
  "board": [["X"," "," "],[" "," "," "],[" "," "," "]],
  "player": "O",
  "winner": null
}
```

### After Game End
```json
{
  "board": [["X","X","X"],["O","O"," "],[" "," "," "]],
  "player": null,
  "winner": "X"
}
```

---

## Troubleshooting Quick Fixes

### Problem: Frame extraction fails
**Solution**: Check video codec. Re-encode with:
```bash
ffmpeg -i input.mov -c:v libx264 -c:a aac output.mp4
```

### Problem: JSON validation error
**Solution**: Use [jsonlint.com](https://jsonlint.com) to validate syntax

### Problem: Images sideways
**Solution**: Check rotation checkbox and select 90° or 270°

### Problem: Too many frames
**Solution**: Use higher skip values or reduce extraction FPS

---

## Next Steps

1. ✅ Complete first test project
2. ✅ Familiarize with keyboard shortcuts
3. ✅ Develop consistent JSON schema for your game
4. ✅ Process full video dataset
5. ✅ Export and use annotations for analysis

**Need help?** Check the full README.md for detailed documentation.

---

**Happy Annotating! 🎮**
