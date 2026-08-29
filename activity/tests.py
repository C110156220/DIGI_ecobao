"""活動 / 最新消息 API 測試。"""

from django.test import TestCase
from rest_framework.test import APIClient

from activity.serializers import Activity_serializers
from ecobao.testutils import create_activity


class ActivityAPITests(TestCase):
    """/news/ — 公開的活動公告端點。"""

    def setUp(self):
        self.client = APIClient()
        self.published = create_activity(
            actid='ACT00001', title='一起減少剩食', status=True)
        self.unpublished = create_activity(
            actid='ACT00002', title='尚未上架的草稿', status=False)

    def test_all_returns_only_published_activities(self):
        """下架（status=False）的文章不得出現在列表中。"""
        response = self.client.get('/news/all/')

        self.assertEqual(response.status_code, 200)
        actids = [item['actid'] for item in response.json()]
        self.assertEqual(actids, ['ACT00001'])
        self.assertNotIn('ACT00002', actids)

    def test_all_is_public(self):
        self.assertEqual(self.client.get('/news/all/').status_code, 200)

    def test_one_returns_the_requested_activity(self):
        response = self.client.get('/news/one/', {'actid': 'ACT00001'})

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body), 1)
        self.assertEqual(body[0]['title'], '一起減少剩食')

    def test_one_without_param_returns_404(self):
        self.assertEqual(self.client.get('/news/one/').status_code, 404)

    def test_one_with_unknown_actid_returns_404(self):
        response = self.client.get('/news/one/', {'actid': 'ACT99999'})

        self.assertEqual(response.status_code, 404)


class ActivityModelTests(TestCase):
    def test_str_includes_title_and_upload_date(self):
        activity = create_activity(title='一起減少剩食')

        self.assertIn('一起減少剩食', str(activity))
        self.assertIn('2023-10-01', str(activity))

    def test_serializer_exposes_all_public_fields(self):
        activity = create_activity()

        data = Activity_serializers(activity).data

        for field in ('actid', 'title', 'author', 'upload_date',
                      'down_date', 'content', 'status'):
            self.assertIn(field, data)
