$(function () {
    $('.form-wrap').click(function () {
        $('.form-wrap').addClass('disabled');
        $(this).removeClass('disabled');
    });

    $("form").submit(function (event) {
        var messageWrap = $(this).find('.alert');
        $.ajax({
            type: "POST",
            url: $(this).attr('action'),
            data: $(this).serialize(),
            success: function () {
                $(messageWrap).html('Register successfully. Please check your email for activation link.').removeClass('hidden');
            },
            error: function (xhr) {
                // handle error message via xhr.responseJSON
                var message = _.values(xhr.responseJSON);
                $(messageWrap).html(message).removeClass('hidden');
            }
        });
        event.preventDefault();
    });
});