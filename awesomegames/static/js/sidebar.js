$(function() {
    // Labels
    $.get('api/label', function(data) {
        data.forEach(function(label){
            $('ul#labels').append('<li><a href="/label/' + label.id + '"> ' + label.name + '</a></li>');
        });
    });

    // Genre
    $.get('api/genre', function(data) {
        data.forEach(function(genre){
            $('ul#genres').append('<li><a href="/label/' + genre.id + '"> ' + genre.name + '</a></li>');
        });
    });
});