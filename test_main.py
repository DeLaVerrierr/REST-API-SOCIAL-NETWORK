import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


@pytest.fixture(scope="module")
def auth_headers():
    client = TestClient(app)

    register = client.post("/api/v1/social-network/auth/register",
                           json={"name": "TEST", "surname": "TEST", "mail": "test00@gmail.com",
                                 "password": "test123654"})

    login = client.post("/api/v1/social-network/auth/login",
                        json={"mail": "test00@gmail.com",
                              "password": "test123654"})

    response_data = login.json()

    token = response_data["token"]

    headers = {"Authorization": f"Bearer {token}"}

    return headers


class TestUser:
    def setup_class(cls):
        """
        pass
        """
        cls.client = TestClient(app)

    def test_profile_user(self, auth_headers):
        """
        pass
        """
        response = self.client.get("/api/v1/social-network/user/profile", headers=auth_headers)
        print('Профиль пользователя')
        assert response.status_code == 200

    def test_create_post(self, auth_headers):
        response = self.client.post("/api/v1/social-network/user/post/create", headers=auth_headers,
                                    json={'text': 'first post'})
        print('Создание поста')
        assert response.status_code == 200

    def test_change_text_post(self, auth_headers):
        response = self.client.put("http://127.0.0.1:8000/api/v1/social-network/user/post/change-post/2",
                                   headers=auth_headers, json={'new_text': "change first post"})
        print('Изменение текста поста по id')
        assert response.status_code == 200

    def test_view_mypost(self, auth_headers):
        response = self.client.get("/api/v1/social-network/user/post/mypost", headers=auth_headers)
        print('Просмотр своих постов')
        assert response.status_code == 200
        # response_data = response.json()
        # print(response_data)

    def test_view_post_id(self, auth_headers):
        response = self.client.get("/api/v1/social-network/user/post/all-post/1", headers=auth_headers)
        print('Просмотр постов по id user')
        assert response.status_code == 200

    def test_view_comment_post(self, auth_headers):
        response = self.client.get("/api/v1/social-network/user/post/1/comment", headers=auth_headers)
        print('Просмотр комментариев к посту по id')
        assert response.status_code == 200

    def test_view_feed(self, auth_headers):
        response = self.client.get("/api/v1/social-network/feed", headers=auth_headers)
        print('Просмотр ленты постов')
        assert response.status_code == 200

    def test_send_friend_requests(self, auth_headers):
        response = self.client.post('/api/v1/social-network/user/friend/friend-requests/1', headers=auth_headers)
        print('Отправка предложение о дружбе')
        assert response.status_code == 200

    def test_view_received_friend_requests(self,auth_headers):
        response = self.client.get('/api/v1/social-network/user/friend/friend-requests/received',headers=auth_headers)
        print('Просмотр полученных запросов на дружбу')
        assert response.status_code == 200
