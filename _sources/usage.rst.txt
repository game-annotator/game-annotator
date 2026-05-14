Usage Guide
===========

Annotation Workflow
-------------------

The typical workflow is:

.. code-block:: text

   1. Create a project
   2. Upload one or more videos
   3. Extract frames
   4. Annotate each frame
   5. Export the dataset

Step 1 — Create a Project
--------------------------

Click **+ New Project** on the dashboard. Fill in:

- **Name** — unique identifier for the project
- **Description** — optional free-text description
- **Initial Game State** — template annotation pre-filled into every new frame
  so you only need to edit what changed. **Any text format works** — JSON,
  plain text, FEN notation, CSV, or any custom scheme your project uses.

Example initial state for chess (JSON — but not required):

.. code-block:: json

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

Step 2 — Upload a Video
------------------------

From the project detail page, use the upload form. Supported formats:
``mp4``, ``avi``, ``mov``, ``mkv``, ``webm``.

If the video was recorded on a mobile device and is rotated, check
**Video needs rotation** and set the **Rotation Angle**.

Step 3 — Extract Frames
------------------------

Click **Extract Frames** on the video row. Three algorithms are available:

====================  =========================================================
Algorithm             Description
====================  =========================================================
**Full**              Extracts every N-th frame to achieve the target FPS.
                      Use for dense annotation of fast-changing games.
**Uniform**           Picks exactly *N* frames evenly spaced across the video.
                      Good for capturing representative states.
**Random Sampling**   Picks exactly *N* frames at random positions.
                      Useful for creating varied training sets.
====================  =========================================================

You can also restrict extraction to a time range using **Start Time** and
**End Time** (in seconds).

Step 4 — Annotate
-----------------

Click **Annotate** to open the annotation interface.

The screen is split into two panes:

- **Left pane** — the most recently annotated frame (reference)
- **Right pane** — the current frame with an editable text area

Edit the text area to describe the game state, then save.
The annotation field is **plain text** — use any format you like (JSON, FEN,
a simple string, a custom array). The tool stores and exports exactly what
you type, without parsing or validating the content.

Layout Modes
~~~~~~~~~~~~

The toolbar at the top of the annotation interface has a three-button mode
switcher. Each mode changes how the panes are arranged:

==============  ===============================================================
Mode            Layout
==============  ===============================================================
**Compare**     Reference frame on the left, current frame + annotation on the
                right, separated by a draggable vertical divider.  Best when
                you need to compare game states side-by-side.
**Focus**       Reference pane hidden. Current frame on the left, annotation
                editor on the right, separated by a draggable vertical divider.
                Best for fast annotation without distraction.
**Immersive**   Reference pane hidden. Current frame on top, annotation editor
                on the bottom, separated by a draggable horizontal divider.
                Best on wide or portrait-oriented frames.
==============  ===============================================================

The divider in every mode is draggable — grab and drag it to resize the
image and editor areas to suit your screen. Each mode remembers its own
split ratio between sessions (stored in browser ``localStorage``).

Adjustable Features
~~~~~~~~~~~~~~~~~~~

**Font size**
  Both the annotation editor and the reference annotation viewer have
  **A−** / **A+** buttons to decrease or increase the font size independently.
  You can also use ``Ctrl+−`` and ``Ctrl+=`` to adjust the editor font size
  from the keyboard. Font sizes are saved in ``localStorage`` and restored on
  the next visit.

**Image zoom**
  Click any frame image (or press ``Z``) to open a full-screen zoom overlay.
  Inside the overlay:

  - **+** / **−** buttons zoom in and out.
  - Click and drag the zoomed image to pan.
  - Press ``Escape`` or click the **×** button to close.

Keyboard Shortcuts
~~~~~~~~~~~~~~~~~~

====================  =========================================================
Shortcut              Action
====================  =========================================================
``←`` / ``→``         Previous / next frame
``Ctrl+S``            Save annotation and advance to next frame
``Ctrl+→``            Skip forward 5 frames
``Shift+→``           Skip forward 10 frames
``Ctrl+G``            Jump a custom number of frames
``Ctrl+Z``            Undo last annotation edit
``Ctrl+=``            Increase annotation font size
``Ctrl+−``            Decrease annotation font size
``Z``                 Open image zoom overlay
``Escape``            Close zoom overlay
====================  =========================================================

Annotated-Only View
~~~~~~~~~~~~~~~~~~~

Click **Show Annotated Only** to display only frames that have been annotated.
Useful for verification. Click again to return to the full frame list.

Step 5 — Export
---------------

Per-video export
~~~~~~~~~~~~~~~~

On the project page, click **Export** next to a video and choose a format:

- **JSON** — array of ``{frame_number, image_path, annotation}`` objects
- **CSV** — spreadsheet with header row
- **COCO JSON** — COCO Captions-style format with ``images`` and ``annotations`` arrays

The file downloads directly to your browser.

Full project export (ZIP)
~~~~~~~~~~~~~~~~~~~~~~~~~

Use the **Export Dataset** button at the top of the project page.
Choose a format and download a ZIP containing one folder per video:

.. code-block:: text

   dataset/
       1/
           frame_000000.jpg
           frame_000000.txt   ← txt format (one sidecar per image)
       2/
           frame_000001.jpg
           annotations.csv    ← csv format
           annotations_coco.json  ← coco format
