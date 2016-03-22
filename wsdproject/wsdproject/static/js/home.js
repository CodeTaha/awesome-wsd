var user_data = null;
// For underscore
_.templateSettings = {
    interpolate: /\{\{(.+?)\}\}/g
};
$(document).ready(function () {
    loadGenres();
    loadLabels();
    $('.menu').on('click', '.prevent_default a', function (event) {
        event.preventDefault();
        var router_url = $(this).attr('href').split('/').slice(1);

        switch (router_url[0]) {
            case 'games':
                Games.initialize(router_url);
                break;
            case 'genre':
                Genre.initialize(router_url[1]);
                break;
            case 'label':
                Label.initialize(router_url[1]);
                break;
        }
    });
});
var check_url = function () {
    if (QueryString.type !== undefined) {
        switch (QueryString.type) {
            case "games":
            {
                Games.initialize([1]);
            }
                break;
            case "genre":
            {
                Genre.initialize([QueryString.genreid]);
            }
                break;
        }
    } else {
        $.get('api/games', function (data) {
            Games.render(data);
        });
    }
};

var Label = {
    initialize: function () {
        switch (arguments.length) {
            case 1:
            {
                this.fetchLabel(arguments[0]);
            }
                break;
        }
    },
    fetchLabel: function (label_id) {
        $.get('/api/label/' + label_id + '/games', function (data) {
            $("#pageTitle").html(data.label);
            Games.render(data);
        });
    }
};

var Genre = {
    initialize: function () {
        switch (arguments.length) {
            case 1:
            {
                this.fetchGenre(arguments[0]);
            }
                break;
        }
    },
    fetchGenre: function (genre_id) {
        if (genre_id === 0) {
            $.get('/api/games/', function (data) {
                $("#pageTitle").html(data.genre);
                Games.render(data);
            });
        } else {
            $.get('/api/genre/' + genre_id + '/games', function (data) {
                //console.log(data);
                $("#pageTitle").html(data.genre);
                Games.render(data.data);
            });
        }
    }
};

var Games = {
    initialize: function (router) {
        if (user_data.user_type === "player") {
            switch (router.length) {
                case 1:
                {
                    this.purchasedGames();
                }
                    break;
            }
        } else {
            switch (router.length) {
                case 1:
                {
                    this.developedGames();
                }
                    break;
            }
        }
    },
    render: function (data) {
        $('#gameList').removeClass('visible').empty();
        $('#gameList').empty();
        data.forEach(function (game) {
            var genres = '';
            game.genres.forEach(function (genre) {
                genres += '<span class="badge normal-text" onclick="Genre.initialize(' + genre.id + ')">' + genre.name + '</span>';
            });
            $('#gameList').append(
                game_template({
                    game: game,
                    genres: genres
                })
            );
        });
        $('#gameList').addClass('visible');
    },
    purchasedGames: function () {
        $(".banner").height(50);
        var self = this;
        $("#pageTitle").html("Games Purchased");
        $.get('/api/players/games_owned', function (data) {
            self.render(data);
        });
    },
    developedGames: function () {
        $(".banner").height(50);
        var self = this;
        $("#pageTitle").html("Games Published");
        $.get('/api/games/my_game_list', function (data) {
            self.render(data);
        });
    },
    fetchGame: function (game_id, cb) {
        var self = this;

        $.get('/api/games/' + game_id, function (data) {
            cb(data);
        });
    }

};

var game_template = _.template(
    '<div class="col-md-4 col-xs-12">' +
    '<div class="panel panel-awe">' +
    '<div class="panel-body">' +
    '<a href="./games/{{game.id}}"><div class="img-wrap"><img class="img-responsive" src="{{game.thumbnail_url}}" alt=""></div></a>' +
    '<h5>{{game.title}}</h5>' +
    '<p>by {{game.game_developer.username}}</p>' +
    '<p class="pull-right">{{genres}}</p>' +
    '<div>' +
    '<div>' +
    '</div>'
);
var QueryString = function () {
    var query_string = {};
    var query = window.location.search.substring(1);
    var vars = query.split("&");
    for (var i = 0; i < vars.length; i++) {
        var pair = vars[i].split("=");
        // If first entry with this name
        if (typeof query_string[pair[0]] === "undefined") {
            query_string[pair[0]] = decodeURIComponent(pair[1]);
            // If second entry with this name
        } else if (typeof query_string[pair[0]] === "string") {
            var arr = [query_string[pair[0]], decodeURIComponent(pair[1])];
            query_string[pair[0]] = arr;
            // If third or later entry with this name
        } else {
            query_string[pair[0]].push(decodeURIComponent(pair[1]));
        }
    }
    return query_string;
}();