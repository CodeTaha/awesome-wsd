"""wsdproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from rest_framework import routers

from awesomegames.views import DeveloperViewSet, PaymentViewSet, GameDetailView, HighScoreViewSet, RegisterView, \
    ProfileView
from awesomegames.views import GameViewSet, PlayerViewSet, HomeView, GenreViewSet, \
    LabelViewSet, TransactionViewSet, GameStateViewSet

router = routers.DefaultRouter()
router.register(r'api/games', GameViewSet, base_name='game-list')
router.register(r'api/players', PlayerViewSet, base_name='player-list')
router.register(r'api/developers', DeveloperViewSet, base_name='developer-list')
router.register(r'api/payment', PaymentViewSet, base_name='payment-list')
router.register(r'api/genre', GenreViewSet, base_name='genre-list')
router.register(r'api/label', LabelViewSet, base_name='label-list')
router.register(r'api/score', HighScoreViewSet, base_name='score-list')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    # admin
    url(r'^admin', include(admin.site.urls)),

    ###############
    # Front Pages #
    ###############
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^register$', RegisterView.as_view(), name='register'),
    url(r'^games/(\d+)', GameDetailView.as_view()),
    url(r'^games$', HomeView.as_view()),
    url(r'^profile$', ProfileView.as_view(), name='profile'),

    ###############
    # Backend API #
    ###############
    # game
    url(r'^api/genre/<?P<pk>[^/]+$/games', GenreViewSet.as_view({'get': 'games'})),
    url(r'^api/label/<?P<pk>[^/]+$/games', LabelViewSet.as_view({'get': 'games'})),
    url(r'^api/games/<?P<pk>[^/]+$', GameViewSet.as_view({'put': 'update'})),
    url(r'^api/games/<?P<pk>[^/]+/update_players$', GameViewSet.as_view({'put': 'update_players'})),
    url(r'^api/games/my_game_list$', GameViewSet.as_view({'get': 'my_game_list'})),
    url(r'^api/games/developer$', GameViewSet.as_view({'get': 'developer'})),
    url(r'^api/games/update$', GameViewSet.as_view({'post': 'update_game'})),
    url(r'^api/games/create_game$', GameViewSet.as_view({'post': 'create_game'})),
    # developer
    url(r'^api/developers/isDeveloper$', DeveloperViewSet.as_view({'get': 'isDeveloper'})),
    url(r'^api/developers/register$', DeveloperViewSet.as_view({'post': 'register'}), name='register_developer'),
    url(r'^api/developers/<?P<pk>[^/]+/activate', DeveloperViewSet.as_view({'get': 'activate'})),
    url(r'^api/developers/game$', DeveloperViewSet.as_view({'get': 'get_game_data'})),
    url(r'^api/developers/statistics$', DeveloperViewSet.as_view({'get': 'statistics'})),

    # player
    url(r'^api/players/games_owned$', PlayerViewSet.as_view({'get': 'games_owned'})),
    url(r'^api/players/isPlayer$', PlayerViewSet.as_view({'get': 'isPlayer'})),
    url(r'^api/players/register$', PlayerViewSet.as_view({'post': 'register'}), name='register_player'),
    url(r'^api/players/<?P<pk>[^/]+/activate', PlayerViewSet.as_view({'get': 'activate'})),
    # payment
    url(r'^api/payment$', PaymentViewSet.as_view({'post': 'create_transaction'})),
    url(r'^api/payment/transaction$', TransactionViewSet.as_view({'get': 'transaction'})),
    # highscore
    url(r'^api/score/game$', HighScoreViewSet.as_view({'get': 'by_game'})),
    url(r'^api/score/my_score$', HighScoreViewSet.as_view({'get': 'my_score'})),
    url(r'^api/score/save$', HighScoreViewSet.as_view({'post': 'save'}), name='save_score'),
    # game sate
    url(r'^api/state/save$', GameStateViewSet.as_view({'post': 'save'})),
    url(r'^api/state/load$', GameStateViewSet.as_view({'get': 'load'})),
    # router registered routes
    url(r'^', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^', include(router.urls))
]
