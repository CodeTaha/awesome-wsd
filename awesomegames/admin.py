from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Developer)
admin.site.register(Player)
admin.site.register(Game)
admin.site.register(Genre)
admin.site.register(Label)
admin.site.register(Review)
admin.site.register(Payment)
admin.site.register(HighestScore)
admin.site.register(GameState)
