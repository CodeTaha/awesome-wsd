import json
import pdb
import random
import re
import string
from hashlib import md5

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic.base import TemplateView
from rest_framework import permissions, viewsets, status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import detail_route
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from awesomegames import authentication
from awesomegames.permissions import IsGameOwnerOrReadOnly, IsAdminOrIsSelf
from awesomegames.permissions import IsUserOwnerOrReadOnly, IsPlayerOrDenied, IsDeveloperOrDenied
from awesomegames.serializers import *
from wsdproject.settings import sid, secret


class HomeView(TemplateView):
    template_name = '../templates/home.html'


class GameDetailView(TemplateView):
    template_name = '../templates/game-detail.html'


class RegisterView(TemplateView):
    template_name = '../templates/register.html'


class ProfileView(TemplateView):
    template_name = '../templates/profile.html'


class AuthView(APIView):
    authentication_classes = (authentication.QuietBasicAuthentication,)
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        user = authenticate(username=request.data['username'], password=request.data['password'])
        if user is not None and user.is_active:
            login(request, user)
            return redirect('/')
        elif user is not None and not user.is_active:
            return render(request, 'rest_framework/login.html',
                          {'message': 'User is not activated. Please check your email.'})
        elif user is None:
            # todo: render login form with error message
            return render(request, 'rest_framework/login.html', {'message': 'User information not correct'})

    def delete(self, request, *args, **kwargs):
        logout(request)
        return redirect('/')


class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsGameOwnerOrReadOnly)

    @detail_route(methods=['put'], permission_classes=[permissions.IsAuthenticated, IsPlayerOrDenied, ])
    def update_players(self, request, pk=None):
        game = get_object_or_404(self.queryset, pk=pk)
        self.check_object_permissions(request, game)
        game.players.add(request.user.id)
        game.save()
        return Response({'status': 'player added'})

    @detail_route(methods=['get'], permission_classes=[permissions.IsAuthenticated, IsDeveloperOrDenied, ])
    def my_game_list(self, request):
        self.check_object_permissions(request, None)
        game_list = self.queryset.filter(game_developer=request.user.id)
        serializer = GameSerializer(game_list, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'], permission_classes=[permissions.AllowAny, ])
    def developer(self, request):
        developer = request.query_params.get("id", None)
        game_list = self.queryset.filter(game_developer=developer)
        serializer = GameSerializer(game_list, many=True)
        return Response(serializer.data)

    @detail_route(methods=['post'],
                  permission_classes=[permissions.IsAuthenticated, IsGameOwnerOrReadOnly, IsDeveloperOrDenied, ])
    def update_game(self, request):

        game = get_object_or_404(self.queryset, pk=request.data['gameId'])
        if game.game_developer_id == request.user.id:

            game.title = request.data['title']
            game.description = request.data['description']

            game.game_url = request.data['game_url']
            game.thumbnail_url = request.data['thumbnail_url']
            game.image_url = request.data['image_url']
            game.code = request.data['code']
            game.price = request.data['price']

            for genre in game.genres.all():
                game.genres.remove(genre)
            postgenre = json.loads(request.data['genres'])
            for genreId in postgenre:
                game.genres.add(genreId)

            game.save()
            serializer = GameSerializer(game)
            result = serializer.data
            result['message'] = "Your changes are save successfully"
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response({"Message": "You Are Not authorized to edit this game"}, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'],
                  permission_classes=[permissions.IsAuthenticated, IsGameOwnerOrReadOnly, IsDeveloperOrDenied, ])
    def create_game(self, request):
        data = request.data
        game = Game.objects.create(title=data['title'], code=data['code'], price=data['price'], )
        game.image_url = data['image_url']
        game.thumbnail_url = data['thumbnail_url']
        game.game_url = data['game_url']
        game.description = data['description']
        postgenre = json.loads(request.data['genres'])
        developer = Developer.objects.get(pk=request.user.id)
        game.game_developer = developer
        for genreId in postgenre:
            game.genres.add(genreId)
        game.save()
        serializer = GameSerializer(game)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (permissions.AllowAny,)

    @detail_route(methods=['get'])
    def games(self, request, pk=None):
        genre = get_object_or_404(self.queryset, pk=pk)
        games = genre.games
        serialized_data = GameSerializer(games, many=True)
        result = {}
        result['genre'] = genre.name
        result['data'] = serialized_data.data
        return Response(result, status=status.HTTP_200_OK)


class LabelViewSet(viewsets.ModelViewSet):
    queryset = Label.objects.all()
    serializer_class = LabelSerializer
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (permissions.AllowAny,)

    @detail_route(methods=['get'])
    def games(self, request, pk=None):
        label = get_object_or_404(self.queryset, pk=pk)
        games = label.games
        serialized_data = GameSerializer(games, many=True)
        return Response(serialized_data.data, status=status.HTTP_200_OK)


class PlayerViewSet(viewsets.ViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (permissions.AllowAny, IsUserOwnerOrReadOnly)

    @detail_route(methods=['get'])
    def games_owned(self, request):
        player = get_object_or_404(self.queryset, pk=request.user.id)
        games_owned = player.games_owned.all()
        serializer = GameSerializer(games_owned, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def isPlayer(self, request):
        player = get_object_or_404(self.queryset, pk=request.user.id)
        serializer = PlayerSerializer(player)
        return Response(serializer.data)

    @detail_route(methods=['post'], permission_classes=[permissions.AllowAny, ])
    def register(self, request):
        VALID_USER_FIELDS = [f.name for f in get_user_model()._meta.fields]
        # generate activation_key from salt and username
        activation_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))

        DEFAULTS = {
            "is_active": False,
            "is_staff": False,
            "is_superuser": False,
        }
        serialized = UserDefaultSerializer(data=request.data)
        if serialized.is_valid():
            user_data = {field: data for (field, data) in request.data.items() if field in VALID_USER_FIELDS}
            user_data.update(DEFAULTS)
            user = get_user_model().objects.create_user(**user_data)
            player = Player(pk=user.pk, activation_key=activation_key)
            player.save()

            # generate verification link and send email
            host_name = request.META['HTTP_HOST']
            verification_link = "http://" + host_name + "/api/players/" + str(
                    user.pk) + "/activate?key=" + activation_key
            email = request.data['email']
            subject = "Welcome to AwesomeGames"
            message = 'Hey ' + user.first_name + "!" \
                                                 '\n\nThank you for registering. Please click the following link to ' \
                                                 'activate your account: ' + verification_link + "\n\nBest,\nAwesome Team"
            send_mail(subject, message, settings.EMAIL_HOST_USER, [email], fail_silently=False)

            return Response(PlayerSerializer(instance=player).data, status=status.HTTP_201_CREATED)
        else:
            return Response(serialized._errors, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'], permission_classes=[permissions.IsAuthenticatedOrReadOnly, ])
    def change_password(self, request):
        # TODO
        pass

    @detail_route(methods=['get'], permission_classes=[permissions.AllowAny, ])
    def activate(self, request, pk=None):
        player = get_object_or_404(Player.objects.all(), pk=pk)
        key = request.query_params['key']
        if key == player.activation_key:
            user = player.user
            user.is_active = True
            user.save()
            messages.add_message(request._request, messages.INFO,
                                 'Account activated successfully. You can login with your username and password now.')
        else:
            messages.add_message(request._request, messages.ERROR, 'Invalid key. Please do not cheat.')

        return redirect('rest_framework:login')

    @detail_route(methods=['get'], permission_classes=[permissions.AllowAny, ])
    def check_username(self, request):
        username = request.data['username']
        if username and User.objects.filter(username=username).exclude(username=username).count():
            return Response({'is_valid': False})
        else:
            return Response({'is_valid': True})

    @detail_route(methods=['get'], permission_classes=[permissions.AllowAny, ])
    def check_email(self, request):
        email = request.query_params['email']
        if email and User.objects.filter(email=email).exclude(email=email).count():
            return Response({'is_valid': False})
        else:
            return Response({'is_valid': True})


class DeveloperViewSet(viewsets.ViewSet):
    queryset = Developer.objects.all()
    serializer_class = DeveloperSerializer
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (permissions.AllowAny,)
    gameset = Game.objects.all()

    @detail_route(methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def isDeveloper(self, request):
        developer = get_object_or_404(self.queryset, pk=request.user.id)
        serializer = DeveloperSerializer(developer)
        return Response(serializer.data)

    @detail_route(methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def get_game_data(self, request):
        game = self.gameset.filter(game_developer=request.user.id, pk=request.query_params['gameId'])
        # games_developed = developer.games.all()
        serializer = GameSerializer(game, many=True)
        if game:
            res = {}
            res['game'] = serializer.data
            payment = Payment.objects.filter(game=game)
            serializer = PaymentSerializer(payment, many=True)
            res['payments'] = serializer.data

            return Response(res)
        else:
            return Response({"Error": "Developer does not own the game"}, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'], permission_classes=[permissions.AllowAny, ])
    def register(self, request):
        VALID_USER_FIELDS = [f.name for f in get_user_model()._meta.fields]
        # generate activation_key from salt and username
        activation_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))

        DEFAULTS = {
            "is_active": False,
            "is_staff": False,
            "is_superuser": False
        }
        serialized = UserDefaultSerializer(data=request.data)
        if serialized.is_valid():
            user_data = {field: data for (field, data) in request.data.items() if field in VALID_USER_FIELDS}
            user_data.update(DEFAULTS)

            user = get_user_model().objects.create_user(**user_data)

            dev = Developer(pk=user.pk, activation_key=activation_key)
            dev.save()

            # generate verification link and send email
            host_name = request.META['HTTP_HOST']
            verification_link = "http://" + host_name + "/api/developers/" + str(
                    user.pk) + "/activate?key=" + activation_key
            email = request.data['email']
            subject = "Welcome to AwesomeGames"
            message = 'Hey ' + user.first_name + "!" \
                                                 '\n\nThank you for registering. Please click the following link to ' \
                                                 'activate your account: ' + verification_link + "\n\nBest,\nAwesome Team"
            send_mail(subject, message, settings.EMAIL_HOST_USER, [email], fail_silently=False)

            return Response(DeveloperSerializer(instance=dev).data, status=status.HTTP_201_CREATED)
        else:
            return Response(serialized._errors, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['get'], permission_classes=[permissions.AllowAny, ])
    def activate(self, request, pk=None):
        dev = get_object_or_404(Developer.objects.all(), pk=pk)
        key = request.query_params['key']
        if key == dev.activation_key:
            user = dev.user
            user.is_active = True
            user.save()
            messages.add_message(request._request, messages.INFO,
                                 'Account activated successfully. You can login with your username and password now.')
        else:
            messages.add_message(request._request, messages.ERROR, 'Invalid key. Please do not cheat.')

        return redirect('rest_framework:login')

    @detail_route(methods=['post'], permission_classes=[permissions.IsAuthenticatedOrReadOnly, IsAdminOrIsSelf])
    def change_password(self, request):
        # TODO
        pass

    @detail_route(methods=['get'], permission_classes=[permissions.AllowAny, ])
    def check_username(self, request):
        username = request.data['username']
        if username and User.objects.filter(username=username).exclude(username=username).count():
            return Response({'is_valid': False})
        else:
            return Response({'is_valid': True})

    @detail_route(methods=['get'], permission_classes=[permissions.AllowAny, ])
    def check_email(self, request):
        email = request.query_params['email']
        if email and User.objects.filter(email=email).exclude(email=email).count():
            return Response({'is_valid': False})
        else:
            return Response({'is_valid': True})

    @detail_route(methods=['get'])
    def statistics(self, request):
        id = request.user.id
        games = Game.objects.all().filter(game_developer=id)
        game_ids = [game.id for game in games]
        sales = []
        for game_id in game_ids:
            sales += Payment.objects.all().filter(game=game_id)
        amounts = [Game.objects.get(pk=sale.game.id).price for sale in sales]
        stats = SalesStatistics(id=id, games_count=len(games), sales_count=len(sales),
                                revenue=sum(amounts), likes=Developer.objects.get(pk=id).likes,
                                profile_image=request.user.developer.profile_image)
        serializer = DeveloperStatisticsSerializer(instance=stats)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SalesStatistics:
    def __init__(self, id, games_count=0, sales_count=0, revenue=0, likes=0, profile_image=''):
        self.id = id
        self.games_count = games_count
        self.sales_count = sales_count
        self.revenue = revenue
        self.likes = likes
        self.profile_image = profile_image


class TransactionViewSet(viewsets.ViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    renderer_classes = [TemplateHTMLRenderer]
    permission_classes = (permissions.IsAuthenticated, IsPlayerOrDenied,)

    @detail_route(methods=['get'])
    def transaction(self, request):
        print("fromgateway", request.query_params)
        payment_id = request.query_params['pid']
        result = request.query_params['result']
        ref = request.query_params['ref']
        checksum = request.query_params['checksum']
        checksum_str = "pid={}&ref={}&result={}&token={}".format(payment_id, ref, result, secret)
        m = md5(checksum_str.encode("ascii"))
        real_checksum = m.hexdigest()
        payment = Payment.objects.get(pk=payment_id)
        # If checksum does not equal, send error
        if checksum == real_checksum:
            game = payment.game
            if result == "success":
                print("Awesome", payment.id, checksum, real_checksum, payment.game_id)
                payment.ref = ref
                payment.status = True
                payment.save()
                # TODO remove the below 2 lines of comments
                game.players.add(payment.player_id)
                game.save()
                serializer = PaymentSerializer(payment)
                res = serializer.data
                res['flag'] = "1"
                return redirect('/games/' + str(payment.game_id))
            elif payment.status:
                # The game has already been bought
                return Response({"Details": "The game is already bought", "flag": "2"})
            # We can give the user a retry
            else:
                serializer = PaymentSerializer(payment)
                res = serializer.data
                res['amount'] = game.price
                checksum_str = "pid={}&sid={}&amount={}&token={}".format(payment.id, sid, game.price, secret)
                # checksum_str is the string concatenated above
                m = md5(checksum_str.encode("ascii"))
                checksum = m.hexdigest()
                res['checksum'] = checksum
                res['sid'] = sid
                res['flag'] = "3"
                return redirect('/games/' + str(payment.game_id))
        else:
            return Response({"ERROR": "Checksums do not match", "flag": "4"})


class PaymentViewSet(viewsets.ViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = (permissions.IsAuthenticated, IsPlayerOrDenied,)

    @detail_route(methods=['post'])
    def create_transaction(self, request):
        host_name = request.META['HTTP_HOST']
        player_id = request.user.id
        player = Player.objects.get(pk=player_id)
        gid = request.data['game']
        game = Game.objects.get(pk=gid)
        print(player)
        print(game, game.price)
        payment = Payment.objects.create(player=player, game=game)
        serializer = PaymentSerializer(payment)
        res = serializer.data
        res['amount'] = str(game.price)
        checksum_str = "pid={}&sid={}&amount={}&token={}".format(payment.id, sid, game.price, secret)
        # checksum_str is the string concatenated above
        m = md5(checksum_str.encode("ascii"))
        checksum = m.hexdigest()
        print("checksum_str", checksum_str, checksum)
        res['checksum'] = checksum
        res['sid'] = sid
        res['redirect_url'] = "http://" + host_name + "/api/payment/transaction"
        # checksum is the value that should be used in the payment request
        return Response(res)


class HighScoreViewSet(viewsets.ViewSet):
    queryset = HighestScore.objects.all()
    serializer_class = HighScoreSerializer
    permission_classes = (permissions.AllowAny,)

    @detail_route(methods=['get'])
    def by_game(self, request):
        scores = self.queryset.filter(game=request.query_params['game_pk'])
        serializer = HighScoreSerializer(scores, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_score(self, request):
        score = self.queryset.filter(player=request.user.id, game=request.query_params['game_pk'])
        if len(score) == 0:
            return Response({})
        else:
            serializer = HighScoreSerializer(score[0])
            return Response(serializer.data)

    @detail_route(methods=['post'], permission_classes=[permissions.IsAuthenticated, ])
    def save(self, request):
        score = self.queryset.filter(player=request.user.id, game=request.data['game'])
        new_score = int(request.data['highest_score'])
        if len(score) == 0:
            # create new and insert
            player = Player.objects.get(pk=request.user.id)
            game = Game.objects.get(pk=request.data['game'])
            new_instance = HighestScore.objects.create(player=player, game=game, highest_score=new_score)
            new_instance.save()
            return Response(HighScoreSerializer(instance=new_instance).data)
        else:
            current = score[0]
            if new_score > current.highest_score:
                # update
                current.highest_score = new_score
                current.save()
            return Response(HighScoreSerializer(instance=current).data)


class GameStateViewSet(viewsets.ViewSet):
    @detail_route(methods=['post'], permission_classes=[permissions.IsAuthenticated, IsPlayerOrDenied])
    def save(self, request):
        player = Player.objects.get(pk=request.user.id)
        game = Game.objects.get(pk=request.data['game'])
        state = re.sub(r"\s+", " ", request.data['state'])
        current_instance = GameState.objects.all().filter(player=player.pk, game=game.pk)

        if len(current_instance) == 0:
            # create new and insert
            new_instance = GameState.objects.create(player=player, game=game, state=state)
            new_instance.save()
            return Response(GameStateSerializer(instance=new_instance).data)
        else:
            current_state = current_instance[0]
            current_state.state = state
            current_state.save()
            return Response(GameStateSerializer(instance=current_state).data)

    @detail_route(methods=['get'], permission_classes=[permissions.IsAuthenticated, IsPlayerOrDenied])
    def load(self, request):
        current_instance = GameState.objects.all().filter(player=request.user.id, game=request.query_params['game_pk'])
        if len(current_instance) == 0:
            return Response({})
        else:
            current_state = current_instance[0]
            current_state.state = re.sub(r"\s+", " ", current_state.state)
            return Response(GameStateSerializer(instance=current_state).data)
