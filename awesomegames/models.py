from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime, date

# Create your models here.


class Developer(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    likes = models.IntegerField(default=0)
    activation_key = models.CharField(max_length=40, default='12345678QWERTY')
    profile_image = models.URLField(blank=True, null=True)


class Player(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    activation_key = models.CharField(max_length=40, default='12345678QWERTY')
    profile_image = models.URLField(blank=True, null=True)

    def __str__(self):
        return str(self.user)


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Label(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Game(models.Model):
    title = models.CharField(max_length=200)
    code = models.CharField(max_length=512, unique=True)
    game_developer = models.ForeignKey(Developer, on_delete=models.CASCADE, related_name="games", blank=True, null=True)
    players = models.ManyToManyField(Player, related_name="games_owned", blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(max_length=1000)
    genres = models.ManyToManyField(Genre, related_name="games")
    labels = models.ManyToManyField(Label, related_name="games")
    pub_date = models.DateTimeField(auto_now_add=True)
    image_url = models.URLField(blank=True, null=True)
    thumbnail_url = models.URLField(blank=True,null=True)
    game_url = models.URLField(blank=True,null=True)
    likes = models.IntegerField(default=0)

    def __str__(self):
        return self.title + " - " + self.code

    def recently_published(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=7)


class HighestScore(models.Model):
    highest_score = models.PositiveIntegerField(default=0)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.highest_score)


class Review(models.Model):
    content = models.TextField(max_length=1000)
    rating = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    pub_date = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField()
    author = models.ForeignKey(Player, related_name="reviews")
    game = models.ForeignKey(Game, related_name="reviews")

    def __str__(self):
        return self.content


class Wishlist(models.Model):
    pass


class Favorite(models.Model):
    pass


class Payment(models.Model):
    player = models.ForeignKey(Player, related_name="payment")
    game = models.ForeignKey(Game)
    status = models.BooleanField(default=False)
    ref = models.CharField(max_length=10, default="")
    pub_date = models.DateField(default=date.today, blank=True)

    def __str__(self):
        return str(self.id) + "-" + str(self.player_id) + "-" + str(self.game_id)

    class Meta:
        ordering = ["id"]


class GameState(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    state = models.TextField(default="")

    def __str__(self):
        return str(self.state)
