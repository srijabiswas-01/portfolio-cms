from django.conf import settings
from django.core.exceptions import RequestDataTooBig
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, SimpleTestCase, override_settings


class BlogUploadLimitTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.content = '<p>Article</p><img src="data:image/png;base64,' + 'A' * (3 * 1024 * 1024) + '">'

    @override_settings(DATA_UPLOAD_MAX_MEMORY_SIZE=2621440)
    def test_inline_images_exceeded_previous_limit(self):
        request = self.factory.post('/admin/blogs/new/', {'content': self.content})
        with self.assertRaises(RequestDataTooBig):
            request.POST

    def test_inline_images_and_separate_cover_are_accepted(self):
        cover = SimpleUploadedFile('cover.jpg', b'x' * (5 * 1024 * 1024), 'image/jpeg')
        request = self.factory.post('/admin/blogs/new/', {
            'title': 'Article', 'content': self.content, 'cover_image': cover,
        })
        self.assertEqual(request.POST['content'], self.content)
        self.assertEqual(request.FILES['cover_image'].size, cover.size)
        request.close()

    def test_request_limit_remains_bounded(self):
        self.assertEqual(settings.DATA_UPLOAD_MAX_MEMORY_SIZE, 8 * 1024 * 1024)
        request = self.factory.post('/admin/blogs/new/', {
            'content': 'A' * (settings.DATA_UPLOAD_MAX_MEMORY_SIZE + 1),
        })
        with self.assertRaises(RequestDataTooBig):
            request.POST
