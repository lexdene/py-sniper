import json

from sniper.controllers import ModelController
from sniper.models import Model
from sniper.tests import TestApp, TestCase, TestClient
from sniper.url import resource


class ArticleModel(Model):
    def get_queryset(self):
        return self.app.model_data


class ArticleCtrl(ModelController):
    model_class = ArticleModel


urls = [
    resource('articles', ArticleCtrl),
]


class TestModelController(TestCase):
    def setUp(self):
        self.app = TestApp(urls=urls)
        self.app.model_data = []

        self.client = TestClient(self.app)

    async def test_get_model_retrieve(self):
        self.app.model_data = [
            {
                'id': 123,
                'name': 'article 1',
                'author': 'Peter',
            },
            {
                'id': 124,
                'name': 'article 2',
                'author': 'John',
            },
        ]

        r1 = await self.client.get('/articles/123')
        self.assertEqual(r1.status_code, 200)
        data1 = json.loads(r1.body)
        self.assertEqual(data1['name'], 'article 1')
        self.assertEqual(data1['author'], 'Peter')

        r2 = await self.client.get('/articles/456')
        self.assertEqual(r2.status_code, 404)
