function showMessage(content) {
    $('#message-wrap').removeClass('visible');
    $('#message-wrap').addClass('visible');
    $('#message-wrap .message').html(content);
}

function showMessageInPopup(content) {
    $('#popup-message-wrap').removeClass('visible');
    $('#popup-message-wrap').addClass('visible');
    $('#popup-message-wrap .message').html(content);
}

function validateGame(game) {
    var message = '';

    if (game.code === '') {
        message += 'Please enter game code<br>';
    }

    if (game.title === '') {
        message += 'Please enter game title<br>';
    }

    if (game.description === '') {
        message += 'Please enter game description<br>';
    }

    if (game.game_url === '') {
        message += 'Please enter game url <br>';
    }

    if (game.price === '') {
        message += 'Please enter game price <br>';
    } else if (isNaN(game.price)) {
        message += 'Game price must be a decimal number <br>';
    }

    if (!message) {
        return {success: true}
    }

    return {success: false, message: message};
}

function show404() {
    $('body').append('<div class="page-not-found"><div class="center-block">The page you are trying to access does not exist. We will lead you back home.</div></div>');
}

function loadGenres() {
    $.get('/api/genre', function(data) {
        $('.menu#genres').empty();
        data.forEach(function(genre) {
            $('.menu#genres').append('<li class="prevent_default"><a href="/genre/'+ genre.id +'">' + genre.name + '</a></li>');
        });
    });
}

function loadLabels() {
    $.get('/api/label', function(data) {
        $('.menu#labels').empty();
        data.forEach(function(label) {
            $('.menu#labels').append('<li class="prevent_default"><a href="/label/'+ label.id +'">' + label.name + '</a></li>');
        });
    });
}

var userType = function (cb) {
    $.ajax({
        url: '/api/players/isPlayer',
        type: 'GET',
        success: function (data) {
            data.user_type = "player";
            user_data = data;
            cb();
        },
        error: function (data) {
            $.ajax({
                url: '/api/developers/isDeveloper',
                type: 'GET',
                success: function (data) {
                    data.user_type = "developer";
                    user_data = data;
                    cb();
                },
                error: function (data) {
                    cb();
                    //alert('woops!'); //or whatever
                }
            });
        }
    });
};