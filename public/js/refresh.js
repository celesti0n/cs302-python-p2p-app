$(function() {
    startRefresh();
});

function startRefresh() {
    setTimeout(startRefresh,4000);
    $.get('./home', function(data) {
        $('#content_div_id').html(data);
    });
}
