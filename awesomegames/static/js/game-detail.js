var gameId;
var generalErrorMsg;
var gamedata;

$(function () {
    init();
});

var init = function () {
    gameId = window.location.pathname.split('/').pop();
    generalErrorMsg = 'Error occurred. Please contact administrators.';
    userType(function(){
            //console.log("user_data", user_data);
            loadGame();
    });

};

var loadGame = function () {
    loadRelatedGames();
    var isPurchased=false;
    $.get('/api/games/' + gameId, function (data) {
        // common stuffs
        var user;
        if(user_data!==null) {
            user = user_data.user.username;
            isPurchased = _.some(data.players, function (player) {
                return player.username == user;
            });
            // stuff needs authentication
            if (isPurchased) {
                $('#price').hide();
                $('#btnBuy').html('Purchased').attr('disabled', 'disabled');
                $('#gameScreen').attr('src', data.game_url);
                $('#gamePlaceholder').hide();

                $.get('/api/score/my_score?game_pk=' + gameId, function (result) {
                    $('#my_highscore').html(result.highest_score);
                });
            } else {
                $('#price').html('€ ' + data.price);
                $('#gameScreen').hide();
                // TODO: replace blank game screen with something else
                $('#gamePlaceholder').attr('src', data.image_url).click(function () {
                    // todo: prompt user to buy the game when click the placeholder
                    showMessage('You seem like this game. <a href="#">Buy and enjoy it</a>');
                });
            }

            // facebook meta tags
            $("meta[property='og\\:url']").attr("content", 'http://awesome-wsd.herokuapp.com/games/' + gameId);
            $("meta[property='og\\:title']").attr("content", data.title);
            $("meta[property='og\\:description']").attr("content", data.description);
            $("meta[property='og\\:image']").attr("content", data.thumbnail_url);

            if(user_data.user_type=="developer"){
                loadDeveloper();
            } else { // set event listener for player
                $("#btnBuy").click(function(){buyGame();});
            }
        } else {
            $('#price').html('€ ' + data.price);
            $('#gameScreen').hide();
            $('#btnBuy').html('Login to Buy').attr('disabled', 'disabled');
            // TODO: replace blank game screen with something else
            $('#gamePlaceholder').attr('src', data.image_url).click(function () {
                // todo: prompt user to buy the game when click the placeholder
                showMessage('You seem like this game. <a href="#">Buy and enjoy it</a>');
            });
        }
        //console.log(data, user);
        gamedata = data;
        $('#title').html(data.title);
        $('#developer').html(data.game_developer.username);

        var pubDate = new Date(data.pub_date);
        $('#releasedDate').html(pubDate.format('dd/mm/yyyy'));

        $('#description').html(data.description);

        $('#thumbnail').attr('src', data.thumbnail_url);


        data.genres.forEach(function(genre) {
            $('#genreList').append('<span class="badge normal-text"><a href="/games?type=genre&genreid=' + genre.id + '">' + genre.name + '</a></span>');
        });

        data.labels.forEach(function (label) {
            $('#labelList').append('<span class="badge normal-text"><a href="/label/' + label.id + '">' + label.name + '</a></span>');
        });

        loadHighscore();
    });
};

var loadHighscore = function() {
    $('#highscores').empty();
    $.get('/api/score/game?game_pk=' + gameId, function (scores) {
        _.sortBy(scores, 'highest_score').reverse().forEach(function (score) {
            $('#highscores').append('<li>' + score.player.username + '<span class="pull-right"> ' + score.highest_score + '</span></li>');
        });
    });
};

// load related games
var loadRelatedGames = function () {
    $.get('/api/games', function (data) {
        _.shuffle(data).slice(0, 3).forEach(function (game) {
            $('.game-related').append('<a class="color-white" href="/games/' + game.id + '">' +
                '<div class="row">' +
                '<div class="col-xs-3">' +
                '<img src="' + game.thumbnail_url + '">' +
                '</div>' +
                '<div class="col-xs-9">' +
                '<h5><b>' + game.title + '</b></h5>' +
                '<p>€' + game.price + '</p>' +
                '</div>' +
                '</div>' +
                '</a><hr>');
        });
    });
};

// listen to in-game message
function listener(event) {
    $('#message-wrap').removeClass('visible');
    if (event.data.messageType !== undefined) {
        switch (event.data.messageType) {
            case 'SCORE':
                $('#id_score').val(event.data.score);
                var data = {
                    'game': gameId,
                    'highest_score': event.data.score,
                    'csrfmiddlewaretoken': $('[name="csrfmiddlewaretoken"]').val()
                };
                $.ajax({
                    type: "POST",
                    url: $('#save_score_form').attr('action'),
                    data: data,
                    success: function (result) {
                        if (event.data.score === result.highest_score) {
                            $('#my_highscore').html(result.highest_score);
                            showMessage('Congrats. You got new highscore.');
                            loadHighscore();
                        } else {
                            showMessage('Too close. Better luck next time');
                        }
                    }
                });
                break;
            case 'SAVE':
                // todo: save current gameState of player to database
                data = {
                    'game': gameId,
                    'state': JSON.stringify(event.data.gameState),
                    'csrfmiddlewaretoken': $('[name="csrfmiddlewaretoken"]').val()
                };
                $.ajax({
                    type: "POST",
                    url: '/api/state/save',
                    data: data,
                    success: function (result) {
                        showMessage('Game saved successfully');
                    },
                    error: function (xhr) {
                        var message = _.values(xhr.responseJSON);
                        showMessage(message);
                    },
                    complete: function () {
                        showMessage('Save complete');
                    }
                });
                break;
            case 'LOAD_REQUEST':
                // todo: request gameState of the player in the game to the API
                $.ajax({
                    type: "GET",
                    url: '/api/state/load?game_pk=' + gameId,
                    success: function (result) {
                        var message = {
                            messageType: "LOAD",
                            gameState: JSON.parse(result.state)
                        };
                        document.getElementById('gameScreen').contentWindow.postMessage(message, "*");
                        showMessage('Game loaded successfully');
                    }
                });
                break;
            case 'ERROR':
                // todo: send error message to the game iframe
                showMessage('No saved state found');
                break;
            case 'SETTING':
                break;
        }
    } else {
        // todo: inform invalid game
        //showMessage(generalErrorMsg);
        //console.log('Message without messageType are not supported.');
    }
}

if (window.addEventListener) {
    addEventListener('message', listener, false);
} else {
    attachEvent('onmessage', listener);
}

var buyGame = function () {
    $.ajax({
            url: '/api/payment',
            type: 'POST',
            data: {"game":gameId, "csrfmiddlewaretoken": csrf},
            success: function(data){
                bootbox.dialog({
                    title: "Buy Game",
                    message: '<div id="purchase_modal" class="row">  ' +
                        '</div>',
                    buttons: {
                        success: {
                            label: "Accept payment",
                            className: "btn-awe pull-right btn-save",
                            callback: function () {
                                $('#formPurchase').submit();
                            }
                        },
                        close: {
                            label: "Close",
                            className: "btn-awe",
                            callback: function () {
                            }
                        }
                    }
                });

            $("#purchase_modal").append(purchase_template({
                id: data.id,
                sid: data.sid,
                redirect_url: data.redirect_url,
                checksum: data.checksum,
                amount: data.amount
            }));
        },
        error: function (xhr) {
            showMessage(generalErrorMsg);
            console.log(xhr.responseJSON);
        }
    });
    //var data = {"id":32,"player":5,"game":2,"status":false,"ref":"","amount":7.99,"checksum":"7e1675d049e6492ca0e8ddb6851d8953","sid":"awesomewsd","redirect_url": "http://127.0.0.1:8000/api/payment/transaction"};
    //console.log("buygame", data)
};

var editGame = function(){
    $.get("/api/genre/", function(genres){
        bootbox.dialog({
                    title: "Edit This Game",
                    message: '<div id="purchase_modal" class="row">  ' +
                        '</div>',
                    buttons: {
                        success: {
                            label: "Save",
                            className: "btn-success",
                            callback: function () {
                                var multipleValues = $( "#fgenre" ).val() || [];
                                for(var i=0; i<multipleValues.length; i++){
                                    multipleValues[i] = parseInt(multipleValues[i]);
                                }
                                var result= {"gameId":gameId, "csrfmiddlewaretoken": csrf};
                                result.code = $( "#fcode" ).val();
                                result.title = $( "#ftitle" ).val();
                                result.description = $( "#fdescription" ).val();
                                result.game_url = $( "#fgame_url" ).val();
                                result.thumbnail_url = $( "#fthumbnail_url" ).val();
                                result.image_url = $( "#fimage_url" ).val();
                                result.price = $( "#fprice" ).val();
                                result.genres = JSON.stringify(multipleValues);
                                //console.log("selected", JSON.stringify(result));
                                $.ajax({
                                    url: '/api/games/update',
                                    type: 'POST',
                                    data: result,
                                    success: function(data){
                                        //console.log(data);
                                        bootbox.alert("<p style='color:black;'>"+data.message+"</p>");
                                    }
                                });
                            }
                        }
                    }
        });
        //console.log("genres", genres);
        $("#purchase_modal").append(edit_template({
            title: gamedata.title,
            description: gamedata.description,
            game_url: gamedata.game_url,
            image_url: gamedata.image_url,
            thumbnail_url: gamedata.thumbnail_url,
            price: gamedata.price,
            code: gamedata.code,

        }));
        var existing_genre=[];
        gamedata.genres.forEach(function(elem){
            existing_genre.push(elem.id);
        });
        genres.forEach(function(elem){
           //console.log(elem)
            if(existing_genre.indexOf(elem.id)!==-1) {
                $("#fgenre").append("<option value='" + elem.id + "' selected='selected'>" + elem.name + "</option>");
            } else{
                $("#fgenre").append("<option value='"+elem.id+"'>"+elem.name+"</option>");
            }
        });
    });
};
var edit_template = _.template(
    '<div class="col-md-12">' +
        '<div class="form-horizontal">' +

            '<div class="form-group"> ' +
                '<label class="col-md-2 control-label" for="title">Title</label> ' +
                '<div class="col-md-5"> ' +
                    '<input id="ftitle" type="text" value="{{title}}" placeholder="Game Name" class="form-control input-md"> ' +
                '</div> ' +
                '<label class="col-md-2 control-label" for="code">Code</label> ' +
                '<div class="col-md-3"> ' +
                    '<input id="fcode" value="{{code}}" type="text" placeholder="Code" class="form-control input-md"> ' +
                '</div> ' +
            '</div> ' +
            '<div class="form-group"> ' +
                '<label class="col-md-4 control-label" for="description">Description</label> ' +
                '<div class="col-md-4"> ' +
                    '<textarea rows="3" id="fdescription" placeholder="Game Description" class="form-control input-md"> ' +
                    '{{description}}</textarea>'+
                '</div> ' +
            '</div> ' +
            '<div class="form-group"> ' +
                '<label class="col-md-4 control-label" for="price">Price</label> ' +
                '<div class="col-md-4"> ' +
                    '<input id="fprice" value="{{price}}" type="number" placeholder="Enter Price" class="form-control input-md"> ' +
                '</div> ' +
            '</div> ' +
            '<div class="form-group"> ' +
                '<label class="col-md-4 control-label" for="genre">Genres</label> ' +
                '<div class="col-md-4"> ' +
                    '<select id="fgenre" multiple class="form-control input-md"> ' +
                    '</select>'+
                '</div> ' +
            '</div> ' +
            '<div class="form-group"> ' +
                '<label class="col-md-4 control-label" for="game_url">Game Url</label> ' +
                '<div class="col-md-4"> ' +
                    '<input id="fgame_url" value="{{game_url}}" type="text" placeholder="Game Url" class="form-control input-md"> ' +
                '</div> ' +
            '</div> ' +
            '<div class="form-group"> ' +
                '<label class="col-md-4 control-label" for="thumnail_url">Thumbnail Url</label> ' +
                '<div class="col-md-4"> ' +
                    '<input id="fthumbnail_url" value="{{thumbnail_url}}" type="text" placeholder="Thumbnail Url" class="form-control input-md"> ' +
                '</div> ' +
            '</div> ' +
            '<div class="form-group"> ' +
                '<label class="col-md-4 control-label" for="image_url">Image Url</label> ' +
                '<div class="col-md-4"> ' +
                    '<input id="fimage_url" value="{{image_url}}" type="text" placeholder="Image Url" class="form-control input-md"> ' +
                '</div> ' +
            '</div> ' +
        '</div>'+
    '</div>'
);
var loadDeveloper = function(){
    $.ajax({
            url: '/api/developers/game?gameId='+gameId,
            type: 'GET',
            success: function (data) {
                // if developer owns the game
                if(data.code===undefined){
                    //data = {"payments":[{"id":33,"player":7,"game":7,"status":false,"ref":"","pub_date":"2016-03-01"},{"id":34,"player":7,"game":7,"status":true,"ref":"","pub_date":"2016-03-02"},{"id":43,"player":5,"game":7,"status":true,"ref":"","pub_date":"2016-03-04"},{"id":63,"player":7,"game":7,"status":false,"ref":"","pub_date":"2016-02-15"},{"id":64,"player":7,"game":7,"status":true,"ref":"5608","pub_date":"2016-02-15"},{"id":64,"player":7,"game":7,"status":true,"ref":"5608","pub_date":"2016-02-10"},{"id":64,"player":7,"game":7,"status":true,"ref":"5608","pub_date":"2016-02-10"},{"id":64,"player":7,"game":7,"status":true,"ref":"5608","pub_date":"2016-02-10"}],"game":[{"id":7,"title":"Click The different DOTS","code":"TWI001","price":"9.89","description":"Game developed by team","pub_date":"2016-03-04T21:49:49.038865Z","image_url":"http://1onlineplay.com/img/bubble-shooter-retro-gaming-aim-hit-color-balls.jpg","thumbnail_url":"http://1onlineplay.com/img/bubble-shooter-retro-gaming-aim-hit-color-balls.jpg","game_url":"http://thuyn.me/jsgames/index.html","genres":[{"id":1,"name":"Action"},{"id":7,"name":"Shooter"},{"id":8,"name":"Survival Horror"}],"labels":[{"id":1,"name":"Editors' Top Picks"},{"id":2,"name":"Hot"},{"id":3,"name":"Promotion"}],"game_developer":{"id":9,"username":"dev1","first_name":"","last_name":""},"players":[{"id":5,"username":"player1","first_name":"","last_name":""},{"id":7,"username":"player3","first_name":"","last_name":""}]}]}

                    //console.log(data.payments)
                    $("#mainArea").empty();
                    $("#mainArea").append('<div id="chart" style="background-color:rgba(253, 250, 250, 0.8);"></div>');
                    $('#btnBuy').html('Edit Game');
                    $("#btnBuy").click(function(){editGame();});
                    var x = ['x'];
                    var purchase_count = 0;
                    var paid = ['Paid'];
                    var pending = ['Pending'];
                    data.payments.forEach(function(elem){
                        var date = new Date(elem.pub_date);
                        var properlyFormatted = date.getYear() +"-"+ ("0" + (date.getMonth() + 1)).slice(-2)+"-"+ ("0" + date.getDate()).slice(-2);
                        if(x.indexOf(properlyFormatted)==-1){
                            x.push(properlyFormatted);
                            if(elem.status){
                                purchase_count++;
                                paid.push(1);
                                pending.push(0);
                            } else {
                                paid.push(0);
                                pending.push(1);
                            }
                        } else {
                             var ind= x.indexOf(properlyFormatted);
                            if(elem.status){
                                paid[ind]=paid[ind]+1;
                            } else {
                                pending[ind]=pending[ind]+1;
                            }
                        }
                    });
                    //console.log("Awesome2",data, x,paid,pending);
                    $("#description").parent().children("h3").html("Sale Statistics");
                    var earnings = purchase_count * data.game[0].price;
                    $("#description").empty();
                    $("#description").append("<b>Total sales=</b> "+ purchase_count);
                    $("#description").append("<br/><b>Earnings= €</b> "+ earnings);
                    c3.generate({
                        data: {
                            x: 'x',
                    //        xFormat: '%Y%m%d', // 'xFormat' can be used as custom format of 'x'
                            columns: [
                                /*['x', '2013-01-01', '2013-01-05', '2013-01-03', '2013-01-04', '2013-01-05', '2013-01-06'],
                    //            ['x', '20130101', '20130102', '20130103', '20130104', '20130105', '20130106'],
                                ['data1', 30, 0, 100, 400, 150, 250],
                                ['data2', 130, 340, 0, 500, 250, 350]*/
                                x,
                                paid,
                                pending
                            ]
                        },
                        axis: {
                            x: {
                                type: 'timeseries',
                                tick: {
                                    format: '%d.%m.%y'
                                }
                            }
                        }
                    });
                } else{
                    $('#btnBuy').html('Unavailable').attr('disabled', 'disabled');
                }
            },
            error: function(){
                $('#btnBuy').html('Unavailable').attr('disabled', 'disabled');
            }
    });

};
var purchase_template = _.template(
    '<div class="col-md-12">' +
        '<form id="formPurchase" class="form-horizontal awesome-form" action="http://payments.webcourse.niksula.hut.fi/pay/" method="POST">' +
            '<input type="hidden" name="pid" value="{{id}}" />' +
            '<input type="hidden" name="sid" value="{{sid}}" />' +
            '<input type="hidden" name="success_url" value="{{redirect_url}}" />' +
            '<input type="hidden" name="cancel_url" value="{{redirect_url}}" />' +
            '<input type="hidden" name="error_url" value="{{redirect_url}}" />' +
            '<input type="hidden" name="checksum" value="{{checksum}}" />' +
            '<input type="hidden" id="id_amount" name="amount" value="{{amount}}" />' +
            '<div class="form-group"> ' +
                '<div class="col-md-6"> ' +
                    '<p><b>Amount to be paid: </b>€{{amount}}/-</p>' +
                '</div> ' +
            '</div> ' +
            '<div class="form-group"> ' +
                '<label class="col-md-4 control-label" for="card">Card Number</label> ' +
                '<div class="col-md-4"> ' +
                    '<input id="card" type="text" placeholder="xxxx xxxx xxxx xxxx" class="form-control input-md"> ' +
                '</div> ' +
            '</div> ' +
            '<div class="form-group"> ' +
                '<label class="col-md-4 control-label" for="name">Name on Card</label> ' +
                '<div class="col-md-4"> ' +
                    '<input id="name" type="text" placeholder="Your name" class="form-control input-md"> ' +
                '</div> ' +
            '</div> ' +
            '<div class="form-group"> ' +
                '<label class="col-md-1 control-label" for="cvv">CVV</label> ' +
                '<div class="col-md-2"> ' +
                    '<input id="cvv" type="password" placeholder="cvv" class="form-control input-md"> ' +
                '</div> ' +
                '<label class="col-md-2 control-label" for="exp">Valid until</label> ' +
                '<div class="col-md-2"> ' +
                    '<input id="exp" type="number" placeholder="mm" class="form-control input-md"> ' +
                '</div> ' +
                '<div class="col-md-2"> ' +
                    '<input id="exp2" type="number" placeholder="yy" class="form-control input-md"> ' +
                '</div> ' +
            '</div> ' +
        '</form>' +
    '</div>'
);

