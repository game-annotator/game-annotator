GameAnnotator Documentation
============================

**GameAnnotator** is a Django web application for annotating board game videos
frame-by-frame. Upload a video, extract frames at a configurable rate, annotate
each frame with a structured game state, and export the dataset in JSON, CSV, or
COCO format.

.. code-block:: text

   Create project → Upload video → Extract frames → Annotate → Export

Features
--------

- **Project management** — organise multiple annotation projects independently
- **Video upload** — supports MP4, AVI, MOV, MKV, WebM
- **Frame extraction** — three algorithms: full FPS, uniform sampling, random sampling
- **Dual-pane annotation UI** — previous annotated frame shown alongside the current one
- **Keyboard shortcuts** — ``←``/``→`` navigate, ``Ctrl+S`` saves and advances, ``Ctrl+→`` skips 5, ``Shift+→`` skips 10
- **Annotated-only view** — toggle to review only annotated frames
- **Multi-format export** — JSON, CSV, and COCO Captions per video; full dataset ZIP per project

.. toctree::
   :maxdepth: 2
   :caption: Contents

   installation
   usage
   api

Indices
-------

* :ref:`genindex`
* :ref:`modindex`
