var csrf;

$(function () {
    init();
});

function init() {
     //load profile for developer only
     $.ajax({
         url: '/api/developers/isDeveloper',
         type: 'GET',
         success: function (data) {
            csrf = $('[name=csrfmiddlewaretoken]')[0].value;
            $('#btnAddGame').click(function () {
                addGame();
            });
            loadGameList();
            loadStatistics();
         },
         error: function () {
             show404();
             window.location = '/';
         }
     });
}

var loadStatistics = function() {
    $.get('api/developers/statistics', function(data) {
        $('#numGame').html(data.games_count);
        $('#numSales').html(data.sales_count);
        $('#numLikes').html(data.likes);
        $('#numRevenue').html(data.revenue);
        $('#profileImg').attr('src', data.profile_image);
    });
}

var loadGameList = function () {
    $.get('api/games/my_game_list', function (data) {
        var tbody = $('table.table-summary tbody').eq(0);
        tbody.empty();
        data.forEach(function (game) {
            tbody.append('<tr>' +
                '<td class="hidden-xs">' + game.code + '</td>' +
                '<td class="game-title">' + game.title + '</td>' +
                '<td class="hidden-xs">' + game.price + '€</td>' +
                '<td class="hidden-xs">' + game.players.length + '</td>' +
                '<td class="hidden-xs">' + game.game_url + '</td>' +
                '<td><a class="btn btn-awe" href="#" onclick="editGame(' + game.id + ')"><i class="glyphicon glyphicon-pencil"></i>Edit</a></td>' +
                '</tr>');
        });
    });
};

var addGame = function () {
    $.get("/api/genre/", function (genres) {
        bootbox.dialog({
            title: "Add new Game",
            message: '<div id="addGameModal" class="row">  ' +
            '</div>',
            buttons: {
                success: {
                    label: "Save",
                    className: "btn-awe pull-right btn-save",
                    callback: function () {
                        var multipleValues = $("#fgenre").val() || [];
                        for (var i = 0; i < multipleValues.length; i++) {
                            multipleValues[i] = parseInt(multipleValues[i]);
                        }
                        var game = {"csrfmiddlewaretoken": csrf};
                        game.code = $("#fcode").val();
                        game.title = $("#ftitle").val();
                        game.description = $("#fdescription").val();
                        game.game_url = $("#fgame_url").val();
                        game.thumbnail_url = $("#fthumbnail_url").val();
                        game.image_url = $("#fimage_url").val();
                        game.price = $("#fprice").val();
                        game.genres = JSON.stringify(multipleValues);

                        var result = validateGame(game);
                        if (result.success) {
                            $.ajax({
                                url: '/api/games/create_game',
                                type: 'POST',
                                data: game,
                                success: function () {
                                    loadGameList();
                                    loadStatistics();
                                    showMessage('Game "' + game.title + '" added sucessfully');
                                },
                                error: function (xhr) {
                                    console.log(xhr.responseText);
                                }
                            });
                        } else {
                            showMessageInPopup(result.message);
                            return false;
                        }
                    }
                },
                close: {
                    label: "Close",
                    className: 'btn-awe',
                    callback: function() {}
                }
            }
        });
        $("#addGameModal").append(add_edit_template({
            title: '',
            code: '',
            price: '',
            gameUrl: '',
            thumbnailUrl: '',
            imageUrl: '',
            description: ''
        }));
        genres.forEach(function (elem) {
            $("#fgenre").append("<option value='" + elem.id + "'>" + elem.name + "</option>");
        });
    });
};

var editGame = function(gameId) {
    $.get('/api/games/' + gameId, function (data) {
        bootbox.dialog({
            title: 'Edit game ' + data.title,
            message: '<div id="editGameModal" class="row">  ' +
            '</div>',
            buttons: {
                success: {
                    label: "Save",
                    className: "btn-awe pull-right btn-save",
                    callback: function () {
                        var multipleValues = $("#fgenre").val() || [];
                        for (var i = 0; i < multipleValues.length; i++) {
                            multipleValues[i] = parseInt(multipleValues[i]);
                        }
                        var game = {"csrfmiddlewaretoken": csrf};
                        game.gameId = gameId;
                        game.code = $("#fcode").val();
                        game.title = $("#ftitle").val();
                        game.description = $("#fdescription").val();
                        game.game_url = $("#fgame_url").val();
                        game.thumbnail_url = $("#fthumbnail_url").val();
                        game.image_url = $("#fimage_url").val();
                        game.price = $("#fprice").val();
                        game.genres = JSON.stringify(multipleValues);

                        var result = validateGame(game);
                        if (result.success) {
                            $.ajax({
                                url: '/api/games/update',
                                type: 'POST',
                                data: game,
                                success: function () {
                                    loadGameList();
                                    loadStatistics();
                                    showMessage('Game "' + game.title + '" updated sucessfully');
                                },
                                error: function (xhr) {
                                    console.log(xhr.responseText);
                                }
                            });
                        } else {
                            showMessageInPopup(result.message);
                            return false;
                        }
                    }
                },
                close: {
                    label: "Close",
                    className: 'btn-awe',
                    callback: function() {}
                }
            }
        });
        $("#editGameModal").append(add_edit_template({
            title: data.title,
            code: data.code,
            price: data.price,
            gameUrl: data.game_url,
            thumbnailUrl: data.thumbnail_url,
            imageUrl: data.image_url,
            description: data.description
        }));

        var existing_genre=[];
        data.genres.forEach(function(elem){
            existing_genre.push(elem.id);
        });

        $.get("/api/genre/", function(genres) {
            genres.forEach(function(elem){
                if(existing_genre.indexOf(elem.id)!==-1) {
                    $("#fgenre").append("<option value='" + elem.id + "' selected='selected'>" + elem.name + "</option>")
                } else{
                    $("#fgenre").append("<option value='"+elem.id+"'>"+elem.name+"</option>");
                }
            });
        });
    });
};

var add_edit_template = _.template(
    '<div id="popup-message-wrap" class="panel panel-awe panel-screen">' +
        '<div class="message"></div>' +
    '</div>' +
    '<form class="awesome-form">' +
        '<div class="col-md-12">' +
            '<div class="form-horizontal">' +
                '<div class="form-group"> ' +
                    '<div class="col-md-6"> ' +
                        '<label for="ftitle">Title*</label>' +
                        '<input id="ftitle" type="text" value="<%= title %>" placeholder="Game Title" class="form-control input-md">' +
                    '</div> ' +
                    '<div class="col-md-3"> ' +
                        '<label for="fcode">Code*</label>' +
                        '<input id="fcode" value="<%= code %>" type="text" placeholder="Code" class="form-control input-md"> ' +
                    '</div> ' +
                    '<div class="col-md-3"> ' +
                        '<label for="fprice">Price*</label>' +
                        '<input id="fprice" value="<%= price %>" type="number" placeholder="Price" class="form-control input-md"> ' +
                    '</div> ' +
                '</div> ' +
            '</div>' +
            '<div class="form-horizontal">' +
                '<div class="row">' +
                    '<div class="col-md-8"> ' +
                            '<label for="fgame_url">Game URL*</label>' +
                            '<input id="fgame_url" value="<%= gameUrl %>" type="text" placeholder="Game Url" class="form-control input-md"> ' +
                            '<label for="fthumbnail_url">Thumbnail URL</label>' +
                            '<input id="fthumbnail_url" value="<%= thumbnailUrl %>" type="text" placeholder="Thumbnail Url" class="form-control input-md"> ' +
                            '<label for="fimage_url">Image URL</label>' +
                            '<input id="fimage_url" value="<%= imageUrl %>" type="text" placeholder="Image Url" class="form-control input-md"> ' +
                    '</div> ' +
                    '<div class="col-md-4"> ' +
                        '<label for="fgenre">Genres</label>' +
                        '<select id="fgenre" multiple class="form-control input-md"> ' +
                        '</select>' +
                    '</div> ' +
                '</div> ' +
            '</div> ' +
            '<div class="form-horizontal">' +
                '<div class="col-md-12"> ' +
                    '<div class="form-group"> ' +
                        '<label for="fdescription">Description</label>' +
                        '<textarea rows="5" id="fdescription" placeholder="Game Description" class="form-control input-md"><%= description %></textarea>' +
                    '</div> ' +
                '</div>' +
            '</div>' +
        '</div>' +
    '</div>'
);