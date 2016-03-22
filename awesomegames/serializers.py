from .models import Developer, Player, Game, Label, Genre, Payment, HighestScore, GameState
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name")


class UserDefaultSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()


class DeveloperSerializer (serializers.ModelSerializer):
    """Serializing all developers"""
    # owner = serializers.ReadOnlyField(source='user.username')
    # games = serializers.HyperlinkedIdentityField('games', view_name='devgames-list', lookup_field='username')
    games = serializers.StringRelatedField(many=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Developer
        fields = ('likes', 'games', 'user')


class DeveloperBasicSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    id = serializers.PrimaryKeyRelatedField(source='user.id', read_only=True)
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')

    class Meta:
        model = Developer
        fields = ('id', 'username', 'first_name', 'last_name')


class PlayerBasicSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    id = serializers.PrimaryKeyRelatedField(source='user.id', read_only=True)
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')

    class Meta:
        model = Player
        fields = ('id', 'username', 'first_name', 'last_name')


class PlayerSerializer(serializers.ModelSerializer):
    # games = serializers.HyperlinkedIdentityField('games', view_name='ownedgames-list', lookup_field='username')
    games_owned = serializers.StringRelatedField(many=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Player
        fields = ('games_owned', 'user')


class LabelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Label
        fields = ('id', 'name')


class GamesByLabelSerializer(serializers.ModelSerializer):
    games = serializers.StringRelatedField(many=True)

    class Meta:
        model = Label
        fields = ('id', 'name', 'games')


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('id', 'name')


class GamesByGenreSerializer(serializers.ModelSerializer):
    games = serializers.StringRelatedField(many=True)

    class Meta:
        model = Label
        fields = ('id', 'name', 'games')


class GameSerializer(serializers.ModelSerializer):
    labels = LabelSerializer(many=True)
    genres = GenreSerializer(many=True)
    game_developer = DeveloperBasicSerializer()
    players = PlayerBasicSerializer(many=True)

    class Meta:
        model = Game
        fields = ('id', 'title', 'code', 'price', 'description', 'pub_date', 'image_url', 'thumbnail_url',
                  'game_url', 'genres', 'labels', 'game_developer', 'players')


class GameBasicSerializer(serializers.ModelSerializer):

    class Meta:
        model = Game
        fields = ('id', 'title')


class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = ('id', 'player', 'game', 'status', 'ref', 'pub_date')


class HighScoreSerializer(serializers.ModelSerializer):
    game = GameBasicSerializer()
    player = PlayerBasicSerializer()

    class Meta:
        model = HighestScore
        fields = ('id', 'player', 'game', 'highest_score')


class GamePublicDataSerializer(serializers.ModelSerializer):
    labels = LabelSerializer(many=True)
    genres = GenreSerializer(many=True)
    game_developer = DeveloperBasicSerializer()
    players = PlayerBasicSerializer(many=True, )

    class Meta:
        model = Game
        fields = ('id', 'title', 'code', 'price', 'description', 'pub_date', 'image_url', 'thumbnail_url',
                  'genres', 'labels', 'game_developer', 'players')


class GameStateSerializer(serializers.ModelSerializer):
    game = GameBasicSerializer()
    player = PlayerBasicSerializer()

    class Meta:
        model = GameState
        fields = ('id', 'player', 'game', 'state')


class DeveloperStatisticsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    likes = serializers.IntegerField()
    games_count = serializers.IntegerField()
    sales_count = serializers.IntegerField()
    revenue = serializers.FloatField()
    profile_image = serializers.URLField()