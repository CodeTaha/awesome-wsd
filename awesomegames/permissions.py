from rest_framework import permissions
from awesomegames.models import Developer, Player
from django.core.exceptions import ObjectDoesNotExist


class IsGameOwnerOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        # only developer can edit own game
        else:
            return obj.game_developer.user.id == request.user.id


class OwnedGameOrDenied(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        # only developer can edit own game
        return request.user in obj.players


class IsUserOwnerOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.user.id == request.user.id


class IsDeveloperOrDenied(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        dev = Developer.objects.all().get(pk=request.user.id)
        if dev is not None:
            return True


class IsPlayerOrDenied(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        try:
            player = Player.objects.all().get(pk=request.user.id)
        except ObjectDoesNotExist:
            player = None
        if player is not None:
            return True
        else:
            return False


class IsDeveloperOrDenied(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        try:
            dev = Developer.objects.all().get(pk=request.user.id)
        except ObjectDoesNotExist:
            dev = None
        if dev is not None:
            return True
        else:
            return False


class IsAdminOrIsSelf(permissions.BasePermission):
    # TODO
    pass
