import pdb
import json
from django.test import TestCase, Client
from django.db import models
import random, string, unittest
from django.contrib import auth

from rest_framework import status
from rest_framework.test import APIClient

from awesomegames.models import *
from django.contrib.auth.models import User


class ViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get_home(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200, "Testing that a request to home / succeeded")


class UserModelTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # create users
        self.user1 = User.objects.create(username='foo1', password='password', email="foo@example.com", is_active=True)
        self.user1.save()
        self.user2 = User.objects.create(username='foo2', password='password', email="foo@example.com", is_active=False)
        self.user2.save()

    def test_login_success(self):
        response = self.client.post('/login/', {'username': 'foo1', 'password': 'password'}, format='json')
        self.assertEqual(response.status_code, 200)

    def test_login_fail_user_inactive(self):
        response = self.client.post('/login/', {'username': 'foo2', 'password': 'password'}, format='json')
        self.assertEquals(response.status_code, 200)

    def test_login_fail_user_not_exist(self):
        response = self.client.post('/login/', {'username': 'not_exist', 'password': '12345678'}, format='json')
        print(response.content)
        self.assertEquals(response.status_code, 200)

    def test_login_fail_incorrect_password(self):
        response = self.client.post('/login/', {'username': 'foo1', 'password': 'wrong'}, format='json')
        self.assertTrue(response.status_code == 200)

    def test_logout(self):
        # authenticate before logout
        self.client.force_authenticate(user=self.user1)
        response = self.client.post('/logout/')
        self.assertTrue(response.status_code == 200)


class DeveloperModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='foo', password='password', email="foo@example.com", is_active=True)
        self.user.save()
        self.dev1 = Developer.objects.create(user=self.user)
        self.dev1.save()

        self.john = User.objects.create(username='john', password='password', email="john@example.com", is_active=False)
        self.john.save()
        self.dev2 = Developer.objects.create(user=self.john)
        self.dev2.save()

        self.client = APIClient()

    def test_register_developer_success(self):
        response = self.client.post('/api/developers/register',
                                    {'username': 'batman', 'password': 'arkham', 'first_name': 'bruce',
                                     'last_name': 'wayne', 'email': 'foo@example.com'}, format='json',
                                    HTTP_HOST='127.0.0.1:8000')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.get(username='batman').is_active, False)
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(Developer.objects.count(), 3)

    def test_register_developer_duplicate_username(self):
        response = self.client.post('/api/developers/register', {'username': 'foo',
                                                                 'password': 'arkham',
                                                                 'first_name': 'bruce',
                                                                 'last_name': 'wayne',
                                                                 'email': 'foo@example.com'
                                                                 },
                                    format='json',
                                    HTTP_HOST='127.0.0.1:8000')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_activate_developer_incorrect_key(self):
        user = User.objects.get(username='john')
        pk = user.pk
        url = '/api/developers/' + str(pk) + '/activate?key=RANDOM123'
        response = self.client.get(url, follow=True)
        updated_user = User.objects.get(pk=pk)
        self.assertEqual(updated_user.is_active, False)

    def test_activate_developer_success(self):
        user = User.objects.get(username='john')
        pk = user.pk
        dev = Developer.objects.get(pk=pk)
        response = self.client.get('/api/developers/' + str(pk) + '/activate?key=' + dev.activation_key, follow=True)
        updated_user = User.objects.get(pk=pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(updated_user.is_active, True)


class PlayerModelTests(TestCase):

    def setUp(self):
        self.foo = User.objects.create(username='foo', password='password', email="foo@example.com", is_active=True)
        self.foo.save()
        self.p1 = Player.objects.create(user=self.foo)
        self.p1.save()

        self.test = User.objects.create(username='test', password='password', email="foo@example.com", is_active=False)
        self.test.save()
        self.p2 = Player.objects.create(user=self.test)
        self.p2.save()

        self.client = APIClient()

    def test_register_player_success(self):
        response = self.client.post('/api/players/register',
                                    {'username': 'superman', 'password': 'earth', 'first_name': 'clark',
                                     'last_name': 'kent', 'email': 'foo@example.com'}, format='json',
                                    HTTP_HOST='127.0.0.1:8000')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.get(username='superman').is_active, False)
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(Player.objects.count(), 3)

    def test_register_developer_duplicate_username(self):
        response = self.client.post('/api/players/register', {'username': 'foo',
                                                                 'password': 'arkham',
                                                                 'first_name': 'bruce',
                                                                 'last_name': 'wayne',
                                                                 'email': 'foo@example.com'
                                                                 },
                                    format='json',
                                    HTTP_HOST='127.0.0.1:8000')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_activate_developer_incorrect_key(self):
        user = User.objects.get(username='test')
        pk = user.pk
        player = Player.objects.get(pk=pk)
        response = self.client.get('/api/players/' + str(pk) + '/activate?key=ABCDEFG', follow=True)
        updated_user = User.objects.get(pk=pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(updated_user.is_active, False)

    def test_activate_developer_success(self):
        user = User.objects.get(username='test')
        pk = user.pk
        player = Player.objects.get(pk=pk)
        response = self.client.get('/api/players/' + str(pk) + '/activate?key=' + player.activation_key, follow=True)
        updated_user = User.objects.get(pk=pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(updated_user.is_active, True)


class GameTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # create developer
        self.user = User.objects.create(username='foo', password='password', email="foo@example.com", is_active=True)
        self.user.save()
        self.dev1 = Developer.objects.create(user=self.user)
        self.dev1.save()
        # create player
        self.user2 = User.objects.create(username='player1', password='password', email="foo@example.com",
                                         is_active=True)
        self.user2.save()
        self.player1 = Player.objects.create(user=self.user2)
        self.player1.save()
        # create genre and label
        self.genre1 = Genre.objects.create(name="Action")
        self.genre1.save()
        self.label1 = Label.objects.create(name="Top Rated")
        self.label1.save()
        # create game 1
        self.game1 = Game.objects.create(title="Hungry Shark 1",
                                         code="1A2ER2",
                                         game_developer=self.dev1,
                                         price="2.99",
                                         description="test",
                                         image_url="http://moonapk.com/wp-content/uploads/2015/07/Drag-Racing-1.6.31-Apk.jpg",
                                         thumbnail_url="http://moonapk.com/wp-content/uploads/2015/07/Drag-Racing-1.6.31-Apk.jpg",
                                         game_url="http://webcourse.cs.hut.fi/example_game.html")
        self.game1.save()
        self.game1.genres.add(self.genre1.id)
        self.game1.labels.add(self.label1.id)
        # create game 2
        self.game2 = Game.objects.create(title="Hungry Shark 2",
                                         code="1A2ER3",
                                         game_developer=self.dev1,
                                         price="2.99",
                                         description="test",
                                         image_url="http://moonapk.com/wp-content/uploads/2015/07/Drag-Racing-1.6.31-Apk.jpg",
                                         thumbnail_url="http://moonapk.com/wp-content/uploads/2015/07/Drag-Racing-1.6.31-Apk.jpg",
                                         game_url="http://webcourse.cs.hut.fi/example_game.html")
        self.game2.save()
        self.game2.players.add(self.player1)

    def test_get_game_detail_view(self):
        response = self.client.get('/games/1')
        self.assertEqual(response.status_code, 200)

    def test_view_all_games(self):
        response = self.client.get('/api/games/')
        results = json.loads(response.content.decode("utf-8"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(results), 2)

    def test_view_game_1(self):
        response = self.client.get('/api/games/1/')
        result = json.loads(response.content.decode("utf-8"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(result['title'], self.game1.title)

    def test_view_games_published_by_developer(self):
        # authenticate
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/games/my_game_list')
        results = json.loads(response.content.decode("utf-8"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(results), 2)

    def test_view_games_bought_by_player(self):
        # authenticate
        self.client.force_authenticate(user=self.user2)
        response = self.client.get('/api/players/games_owned')
        results = json.loads(response.content.decode("utf-8"))
        print("results ", results)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(results), 1)
        # verify player1 owns game2
        self.assertEqual(results[0]['title'], self.game2.title)

    def test_create_game_success(self):
        # authenticate as developer
        self.client.force_authenticate(self.user)
        data = {'title': 'Flappy Bird',
                'code': '1A2ER4',
                'game_developer': '1',
                'price': '7.99',
                'genres': '[1]', 'labels': '[1]',
                'description': 'test',
                'image_url': 'http://moonapk.com/wp-content/uploads/2015/07/Drag-Racing-1.6.31-Apk.jpg',
                'thumbnail_url': 'http://moonapk.com/wp-content/uploads/2015/07/Drag-Racing-1.6.31-Apk.jpg',
                'game_url': 'http://webcourse.cs.hut.fi/example_game.html'}
        response = self.client.post('/api/games/create_game', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Game.objects.count(), 3)

    def test_create_game_no_permission(self):
        with self.assertRaises(Exception):
            # authenticate as developer
            self.client.force_authenticate(self.user2)
            data = {'title': 'Flappy Bird 2',
                    'code': '1A2ER5',
                    'game_developer': '1',
                    'price': '7.99',
                    'genres': '[1]', 'labels': '[1]',
                    'description': 'test',
                    'image_url': 'http://moonapk.com/wp-content/uploads/2015/07/Drag-Racing-1.6.31-Apk.jpg',
                    'thumbnail_url': 'http://moonapk.com/wp-content/uploads/2015/07/Drag-Racing-1.6.31-Apk.jpg',
                    'game_url': 'http://webcourse.cs.hut.fi/example_game.html'}
            response = self.client.post('/api/games/create_game', data, format='json')

    def test_edit_game_success(self):
        # authenticate as developer
        self.client.force_authenticate(self.user)
        data = {'gameId': '1',
                'title': 'Hungry Shark',
                'code': '1A2ER2',
                'game_developer': '1',
                'price': '10.00',
                'genres': '[1]', 'labels': '[1]',
                'description': 'updated',
                'image_url': 'http://moonapk.com/wp-content/uploads/2015/07/Drag-Racing-1.6.31-Apk.jpg',
                'thumbnail_url': 'http://moonapk.com/wp-content/uploads/2015/07/Drag-Racing-1.6.31-Apk.jpg',
                'game_url': 'http://webcourse.cs.hut.fi/example_game.html'}
        response = self.client.post('/api/games/update', data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Game.objects.get(pk=1).price, float(10))
        self.assertEqual(Game.objects.get(pk=1).description, "updated")

    def test_edit_game_no_permission(self):
        # authenticate as developer
        self.client.force_authenticate(self.user2)
        data = {'gameId': '1',
                'title': 'Hungry Shark',
                'code': '1A2ER2',
                'game_developer': '1',
                'price': '10.00',
                'genres': '[1]', 'labels': '[1]',
                'description': 'updated',
                'image_url': 'http://moonapk.com/wp-content/uploads/2015/07/Drag-Racing-1.6.31-Apk.jpg',
                'thumbnail_url': 'http://moonapk.com/wp-content/uploads/2015/07/Drag-Racing-1.6.31-Apk.jpg',
                'game_url': 'http://webcourse.cs.hut.fi/example_game.html'}
        response = self.client.post('/api/games/update', data)
        self.assertEqual(response.status_code, 400)