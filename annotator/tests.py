"""
Tests for the game annotation tool.

Covers models, forms, and all view endpoints.
"""
import json
import io
import zipfile

from django.test import TestCase
from django.urls import reverse

from .models import Project, Video, Frame
from .forms import ProjectForm, FrameExtractionForm


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_project(**kwargs):
    defaults = {'name': 'Test Project', 'description': 'A test project'}
    defaults.update(kwargs)
    return Project.objects.create(**defaults)


def make_video(project, **kwargs):
    defaults = {
        'name': 'Test Video',
        'video_file': 'videos/test.mp4',
        'status': 'ready',
        'total_frames': 0,
        'annotated_frames': 0,
    }
    defaults.update(kwargs)
    return Video.objects.create(project=project, **defaults)


def make_frame(video, frame_number, annotated=False, annotation=''):
    return Frame.objects.create(
        video=video,
        frame_number=frame_number,
        image_path=f'/media/frames/{video.project.id}/{video.id}/frame_{frame_number:06d}.jpg',
        is_annotated=annotated,
        annotation_data=annotation if annotated else None,
    )


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------

class ProjectModelTest(TestCase):
    def setUp(self):
        self.project = make_project()

    def test_str(self):
        self.assertEqual(str(self.project), 'Test Project')

    def test_get_total_videos_empty(self):
        self.assertEqual(self.project.get_total_videos(), 0)

    def test_get_total_videos(self):
        make_video(self.project)
        make_video(self.project, name='Video 2')
        self.assertEqual(self.project.get_total_videos(), 2)

    def test_get_annotated_videos_none_completed(self):
        make_video(self.project, status='in_progress')
        self.assertEqual(self.project.get_annotated_videos(), 0)

    def test_get_annotated_videos_counts_completed(self):
        make_video(self.project, status='completed')
        make_video(self.project, name='V2', status='in_progress')
        self.assertEqual(self.project.get_annotated_videos(), 1)


class VideoModelTest(TestCase):
    def setUp(self):
        project = make_project()
        self.video = make_video(project, total_frames=10, annotated_frames=0)

    def test_str(self):
        self.assertIn('Test Video', str(self.video))

    def test_progress_zero_when_no_frames(self):
        self.video.total_frames = 0
        self.assertEqual(self.video.get_progress_percentage(), 0)

    def test_progress_percentage(self):
        self.video.total_frames = 10
        self.video.annotated_frames = 5
        self.assertEqual(self.video.get_progress_percentage(), 50)

    def test_progress_percentage_complete(self):
        self.video.total_frames = 4
        self.video.annotated_frames = 4
        self.assertEqual(self.video.get_progress_percentage(), 100)


class FrameModelTest(TestCase):
    def setUp(self):
        project = make_project()
        self.video = make_video(project, total_frames=5)
        self.frames = [make_frame(self.video, i) for i in range(5)]

    def test_str(self):
        self.assertIn('Frame 0', str(self.frames[0]))

    def test_get_next_frame(self):
        self.assertEqual(self.frames[0].get_next_frame(), self.frames[1])

    def test_get_next_frame_at_end(self):
        self.assertIsNone(self.frames[4].get_next_frame())

    def test_get_previous_frame(self):
        self.assertEqual(self.frames[2].get_previous_frame(), self.frames[1])

    def test_get_previous_frame_at_start(self):
        self.assertIsNone(self.frames[0].get_previous_frame())

    def test_get_next_annotated_frame(self):
        self.frames[3].is_annotated = True
        self.frames[3].save()
        self.assertEqual(self.frames[1].get_next_annotated_frame(), self.frames[3])

    def test_get_next_annotated_frame_none(self):
        self.assertIsNone(self.frames[0].get_next_annotated_frame())

    def test_get_previous_annotated_frame(self):
        self.frames[1].is_annotated = True
        self.frames[1].save()
        self.assertEqual(self.frames[3].get_previous_annotated_frame(), self.frames[1])

    def test_get_previous_annotated_frame_none(self):
        self.assertIsNone(self.frames[0].get_previous_annotated_frame())


# ---------------------------------------------------------------------------
# Form tests
# ---------------------------------------------------------------------------

class ProjectFormTest(TestCase):
    def test_valid_form(self):
        form = ProjectForm(data={'name': 'Chess', 'description': 'desc', 'initial_array_text': ''})
        self.assertTrue(form.is_valid())

    def test_name_required(self):
        form = ProjectForm(data={'name': '', 'description': 'desc'})
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_save_maps_initial_array_text(self):
        form = ProjectForm(data={
            'name': 'My Project',
            'description': '',
            'initial_array_text': '[[1,2],[3,4]]',
        })
        self.assertTrue(form.is_valid())
        project = form.save()
        self.assertEqual(project.initial_array, '[[1,2],[3,4]]')

    def test_duplicate_name_invalid(self):
        make_project(name='Taken')
        form = ProjectForm(data={'name': 'Taken', 'description': ''})
        self.assertFalse(form.is_valid())


class FrameExtractionFormTest(TestCase):
    def _form(self, **kwargs):
        data = {'algorithm': 'full', 'fps': 1, 'target_frames': '', 'start_time': 0, 'end_time': ''}
        data.update(kwargs)
        return FrameExtractionForm(data=data)

    def test_valid_full_algorithm(self):
        self.assertTrue(self._form().is_valid())

    def test_defaults_fps_for_full_when_blank(self):
        form = self._form(fps='')
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['fps'], 1.0)

    def test_defaults_target_frames_for_uniform(self):
        form = self._form(algorithm='uniform', fps='', target_frames='')
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['target_frames'], 100)

    def test_defaults_target_frames_for_sampling(self):
        form = self._form(algorithm='sampling', fps='', target_frames='')
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['target_frames'], 100)

    def test_invalid_algorithm(self):
        form = self._form(algorithm='bad')
        self.assertFalse(form.is_valid())


# ---------------------------------------------------------------------------
# View tests
# ---------------------------------------------------------------------------

class DashboardViewTest(TestCase):
    def test_get(self):
        resp = self.client.get(reverse('dashboard'))
        self.assertEqual(resp.status_code, 200)

    def test_lists_projects(self):
        make_project(name='Alpha')
        make_project(name='Beta')
        resp = self.client.get(reverse('dashboard'))
        self.assertContains(resp, 'Alpha')
        self.assertContains(resp, 'Beta')


class ProjectCreateViewTest(TestCase):
    def test_get_renders_form(self):
        resp = self.client.get(reverse('project_create'))
        self.assertEqual(resp.status_code, 200)

    def test_post_creates_project_and_redirects(self):
        resp = self.client.post(reverse('project_create'), {
            'name': 'New Project',
            'description': 'desc',
            'initial_array_text': '',
        })
        project = Project.objects.get(name='New Project')
        self.assertRedirects(resp, reverse('project_detail', args=[project.id]))

    def test_post_invalid_shows_form(self):
        resp = self.client.post(reverse('project_create'), {'name': '', 'description': ''})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Project.objects.count(), 0)


class ProjectDetailViewTest(TestCase):
    def setUp(self):
        self.project = make_project()

    def test_get(self):
        resp = self.client.get(reverse('project_detail', args=[self.project.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, self.project.name)

    def test_404_for_missing_project(self):
        resp = self.client.get(reverse('project_detail', args=[9999]))
        self.assertEqual(resp.status_code, 404)

    def test_context_counts(self):
        make_video(self.project, name='V1', status='completed')
        make_video(self.project, name='V2', status='in_progress')
        resp = self.client.get(reverse('project_detail', args=[self.project.id]))
        self.assertEqual(resp.context['completed_count'], 1)
        self.assertEqual(resp.context['in_progress_count'], 1)


class ProjectEditViewTest(TestCase):
    def setUp(self):
        self.project = make_project()

    def test_get(self):
        resp = self.client.get(reverse('project_edit', args=[self.project.id]))
        self.assertEqual(resp.status_code, 200)

    def test_post_updates_project(self):
        self.client.post(reverse('project_edit', args=[self.project.id]), {
            'name': 'Updated Name',
            'description': 'Updated desc',
            'initial_array_text': '',
        })
        self.project.refresh_from_db()
        self.assertEqual(self.project.name, 'Updated Name')

    def test_post_redirects_to_project_detail(self):
        resp = self.client.post(reverse('project_edit', args=[self.project.id]), {
            'name': 'X',
            'description': '',
            'initial_array_text': '',
        })
        self.assertRedirects(resp, reverse('project_detail', args=[self.project.id]))


class VideoAnnotateViewTest(TestCase):
    def setUp(self):
        project = make_project()
        self.video = make_video(project)

    def test_redirects_when_no_frames(self):
        resp = self.client.get(reverse('video_annotate', args=[self.video.id]))
        self.assertRedirects(resp, reverse('video_extract_frames', args=[self.video.id]))

    def test_renders_first_unannotated_frame(self):
        make_frame(self.video, 0)
        make_frame(self.video, 1)
        resp = self.client.get(reverse('video_annotate', args=[self.video.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['current_frame'].frame_number, 0)

    def test_starts_at_first_unannotated(self):
        make_frame(self.video, 0, annotated=True, annotation='done')
        make_frame(self.video, 1)
        resp = self.client.get(reverse('video_annotate', args=[self.video.id]))
        self.assertEqual(resp.context['current_frame'].frame_number, 1)

    def test_context_includes_counts(self):
        make_frame(self.video, 0, annotated=True, annotation='x')
        make_frame(self.video, 1)
        resp = self.client.get(reverse('video_annotate', args=[self.video.id]))
        self.assertEqual(resp.context['annotated_count'], 1)
        self.assertEqual(resp.context['total_frames'], 2)


class FrameSaveAnnotationViewTest(TestCase):
    def setUp(self):
        project = make_project()
        self.video = make_video(project, total_frames=3)
        self.frame = make_frame(self.video, 0)

    def _post(self, frame, annotation='{"board": []}'):
        return self.client.post(
            reverse('frame_save_annotation', args=[frame.id]),
            data=json.dumps({'annotation': annotation}),
            content_type='application/json',
        )

    def test_saves_annotation(self):
        self._post(self.frame, '{"x": 1}')
        self.frame.refresh_from_db()
        self.assertTrue(self.frame.is_annotated)
        self.assertEqual(self.frame.annotation_data, '{"x": 1}')

    def test_returns_success_and_count(self):
        resp = self._post(self.frame)
        data = json.loads(resp.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['annotated_count'], 1)

    def test_video_status_in_progress(self):
        self._post(self.frame)
        self.video.refresh_from_db()
        self.assertEqual(self.video.status, 'in_progress')

    def test_video_status_completed_when_all_annotated(self):
        self.video.total_frames = 1
        self.video.save()
        self._post(self.frame)
        self.video.refresh_from_db()
        self.assertEqual(self.video.status, 'completed')

    def test_get_not_allowed(self):
        resp = self.client.get(reverse('frame_save_annotation', args=[self.frame.id]))
        self.assertEqual(resp.status_code, 405)


class FrameGetDataViewTest(TestCase):
    def setUp(self):
        project = make_project()
        video = make_video(project)
        self.frame = make_frame(video, 5, annotated=True, annotation='hello')

    def test_returns_frame_data(self):
        resp = self.client.get(reverse('frame_get_data', args=[self.frame.id]))
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(data['frame_number'], 5)
        self.assertEqual(data['annotation'], 'hello')
        self.assertTrue(data['is_annotated'])

    def test_post_not_allowed(self):
        resp = self.client.post(reverse('frame_get_data', args=[self.frame.id]))
        self.assertEqual(resp.status_code, 405)


class FrameNavigateViewTest(TestCase):
    def setUp(self):
        project = make_project()
        self.video = make_video(project)
        self.f0 = make_frame(self.video, 0)
        self.f1 = make_frame(self.video, 1)
        self.f2 = make_frame(self.video, 2)

    def _get(self, frame, direction):
        return self.client.get(reverse('frame_navigate', args=[frame.id, direction]))

    def test_navigate_next(self):
        data = json.loads(self._get(self.f0, 'next').content)
        self.assertEqual(data['frame_id'], self.f1.id)

    def test_navigate_previous(self):
        data = json.loads(self._get(self.f2, 'previous').content)
        self.assertEqual(data['frame_id'], self.f1.id)

    def test_navigate_skip(self):
        data = json.loads(self._get(self.f0, 'skip_2').content)
        self.assertEqual(data['frame_id'], self.f2.id)

    def test_navigate_next_at_end_returns_404(self):
        self.assertEqual(self._get(self.f2, 'next').status_code, 404)

    def test_navigate_previous_at_start_returns_404(self):
        self.assertEqual(self._get(self.f0, 'previous').status_code, 404)

    def test_invalid_skip_direction_returns_400(self):
        self.assertEqual(self._get(self.f0, 'skip_abc').status_code, 400)

    def test_previous_annotated_included_in_response(self):
        self.f0.is_annotated = True
        self.f0.save()
        data = json.loads(self._get(self.f0, 'next').content)
        self.assertEqual(data['previous_annotated_id'], self.f0.id)


class VideoToggleAnnotatedViewTest(TestCase):
    def setUp(self):
        project = make_project()
        self.video = make_video(project)
        make_frame(self.video, 0, annotated=True, annotation='a')
        make_frame(self.video, 1)
        make_frame(self.video, 2, annotated=True, annotation='b')

    def test_returns_only_annotated_frames(self):
        resp = self.client.get(reverse('video_toggle_annotated', args=[self.video.id]))
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(len(data['frames']), 2)
        numbers = [f['frame_number'] for f in data['frames']]
        self.assertIn(0, numbers)
        self.assertIn(2, numbers)
        self.assertNotIn(1, numbers)


class FrameUnmarkViewTest(TestCase):
    def setUp(self):
        project = make_project()
        self.video = make_video(project, status='completed', annotated_frames=1)
        self.frame = make_frame(self.video, 0, annotated=True, annotation='done')

    def test_clears_annotation(self):
        self.client.post(reverse('frame_unmark', args=[self.frame.id]))
        self.frame.refresh_from_db()
        self.assertFalse(self.frame.is_annotated)
        self.assertIsNone(self.frame.annotation_data)

    def test_reverts_completed_video_to_in_progress(self):
        self.client.post(reverse('frame_unmark', args=[self.frame.id]))
        self.video.refresh_from_db()
        self.assertEqual(self.video.status, 'in_progress')

    def test_returns_updated_count(self):
        resp = self.client.post(reverse('frame_unmark', args=[self.frame.id]))
        data = json.loads(resp.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['annotated_count'], 0)


class VideoExportViewTest(TestCase):
    def setUp(self):
        project = make_project()
        self.video = make_video(project)
        make_frame(self.video, 0, annotated=True, annotation='{"x":1}')
        make_frame(self.video, 1, annotated=True, annotation='{"x":2}')
        make_frame(self.video, 2)  # unannotated — must not appear in exports

    def test_json_export_status(self):
        resp = self.client.get(reverse('video_export', args=[self.video.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('application/json', resp['Content-Type'])

    def test_json_export_only_annotated(self):
        resp = self.client.get(reverse('video_export', args=[self.video.id]))
        data = json.loads(resp.content)
        self.assertEqual(len(data), 2)
        frame_numbers = [f['frame_number'] for f in data]
        self.assertNotIn(2, frame_numbers)

    def test_csv_export(self):
        resp = self.client.get(reverse('video_export', args=[self.video.id]) + '?format=csv')
        self.assertIn('text/csv', resp['Content-Type'])
        content = resp.content.decode()
        self.assertIn('frame_number', content)
        self.assertIn('frame_000000', content)

    def test_coco_export(self):
        resp = self.client.get(reverse('video_export', args=[self.video.id]) + '?format=coco')
        data = json.loads(resp.content)
        self.assertIn('images', data)
        self.assertIn('annotations', data)
        self.assertEqual(len(data['images']), 2)


class VideoExtractFramesViewTest(TestCase):
    def setUp(self):
        project = make_project()
        self.video = make_video(project)

    def test_get_renders_form(self):
        resp = self.client.get(reverse('video_extract_frames', args=[self.video.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('form', resp.context)

    def test_get_404_for_missing_video(self):
        resp = self.client.get(reverse('video_extract_frames', args=[9999]))
        self.assertEqual(resp.status_code, 404)

    def test_post_invalid_form_shows_errors(self):
        resp = self.client.post(reverse('video_extract_frames', args=[self.video.id]), {
            'algorithm': 'bad_value',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.context['form'].is_valid())


class VideoDeleteViewTest(TestCase):
    def setUp(self):
        self.project = make_project()
        self.video = make_video(self.project)
        make_frame(self.video, 0)

    def test_deletes_video_and_frames(self):
        video_id = self.video.id
        self.client.post(reverse('video_delete', args=[video_id]))
        self.assertFalse(Video.objects.filter(id=video_id).exists())
        self.assertEqual(Frame.objects.filter(video_id=video_id).count(), 0)

    def test_redirects_to_project_detail(self):
        resp = self.client.post(reverse('video_delete', args=[self.video.id]))
        self.assertRedirects(resp, reverse('project_detail', args=[self.project.id]))

    def test_get_not_allowed(self):
        resp = self.client.get(reverse('video_delete', args=[self.video.id]))
        self.assertEqual(resp.status_code, 405)


class ProjectExportDatasetViewTest(TestCase):
    def setUp(self):
        self.project = make_project(name='ExportProj')
        video = make_video(self.project)
        make_frame(video, 0, annotated=True, annotation='state A')
        make_frame(video, 1, annotated=True, annotation='state B')

    def _post(self, fmt='txt'):
        return self.client.post(
            reverse('project_export_dataset', args=[self.project.id]),
            data={'format': fmt},
        )

    def _zip_names(self, resp):
        return zipfile.ZipFile(io.BytesIO(resp.content)).namelist()

    def test_returns_zip(self):
        resp = self._post()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'application/zip')

    def test_txt_format_has_sidecar_files(self):
        names = self._zip_names(self._post('txt'))
        self.assertTrue(any(n.endswith('.txt') for n in names))

    def test_csv_format_has_csv_file(self):
        names = self._zip_names(self._post('csv'))
        self.assertTrue(any(n.endswith('.csv') for n in names))

    def test_coco_format_has_json_file(self):
        names = self._zip_names(self._post('coco'))
        self.assertTrue(any(n.endswith('.json') for n in names))

    def test_invalid_format_falls_back_to_txt(self):
        resp = self._post('invalid')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'application/zip')

    def test_get_not_allowed(self):
        resp = self.client.get(reverse('project_export_dataset', args=[self.project.id]))
        self.assertEqual(resp.status_code, 405)
