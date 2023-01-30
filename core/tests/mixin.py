from functools import partial

from django.contrib.auth.models import User

from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from model_bakery.recipe import Recipe


class APITestMixin:

    url = ''
    username = 'Mocked user'
    password = '12345678'
    usuario_kwargs = {}

    def get_header_credencial(self, user=None):
        token = Token.objects.create(user=(user if user else self.user))
        return str(token.key)

    def get_client(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.get_header_credencial())
        client.post = partial(client.post, format='json')
        return client

    def set_user_on_client(self, user):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.get_header_credencial(user))

    def setUp(self):
        self.user = Recipe(
            User,
            username=self.username, password=self.password, **self.usuario_kwargs
        ).make()
        self.client = self.get_client()

    @classmethod
    def setUpClass(cls):
        if not isinstance(APITestMixin, cls) and cls.setUp is not APITestMixin.setUp:
            setUp_original = cls.setUp

            def setUpNew(self, *args, **kwargs):
                APITestMixin.setUp(self)
                setUp_original(self, *args, **kwargs)

            cls.setUp = setUpNew
        super().setUpClass()
