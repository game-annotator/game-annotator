API Reference
=============

This page documents all public Python modules: models, views, forms, management
commands, and admin configuration. Source links (``[source]``) open the
corresponding file in the repository.

Models
------

The data layer consists of three models. ``Project`` owns many ``Video``
objects; each ``Video`` owns many ``Frame`` objects.

.. autoclass:: annotator.models.Project
   :members:
   :special-members: __str__

.. autoclass:: annotator.models.Video
   :members:
   :special-members: __str__

.. autoclass:: annotator.models.Frame
   :members:
   :special-members: __str__

Views
-----

All views are plain Django function-based views. API endpoints return
``JsonResponse``; page views return rendered HTML templates.

.. rubric:: Page views

.. autofunction:: annotator.views.dashboard
.. autofunction:: annotator.views.project_create
.. autofunction:: annotator.views.project_detail
.. autofunction:: annotator.views.project_edit
.. autofunction:: annotator.views.video_extract_frames
.. autofunction:: annotator.views.video_annotate
.. autofunction:: annotator.views.video_delete

.. rubric:: API endpoints

.. autofunction:: annotator.views.frame_save_annotation
.. autofunction:: annotator.views.frame_get_data
.. autofunction:: annotator.views.frame_navigate
.. autofunction:: annotator.views.frame_unmark
.. autofunction:: annotator.views.video_export
.. autofunction:: annotator.views.video_toggle_annotated_view
.. autofunction:: annotator.views.project_export_dataset

Forms
-----

.. autoclass:: annotator.forms.ProjectForm
   :members:

.. autoclass:: annotator.forms.VideoUploadForm
   :members:

.. autoclass:: annotator.forms.FrameExtractionForm
   :members:

Management Commands
-------------------

Frame extraction is implemented as a Django management command so it can also
be run directly from the CLI:

.. code-block:: bash

   python manage.py extract_frames --video_id=1 --algorithm=uniform --target_frames=50

.. autoclass:: annotator.management.commands.extract_frames.Command
   :members: handle, add_arguments

Admin
-----

.. autoclass:: annotator.admin.ProjectAdmin
.. autoclass:: annotator.admin.VideoAdmin
.. autoclass:: annotator.admin.FrameAdmin
