$(document).ready(function () {
    setInterval(function() {
        $("#users-online").load("./getList");
        $("#list-of-total-users").load("./listAllUsers");
    }, 30000);

    setInterval(function() { // takes currently opened chat window and feeds username out
        var personName = $('.right .top').find('.name').text();
        if (personName == 'mwon724') { // still on the starting screen
          return false;
        }
        else {
        $.ajax({
          type: 'GET',
          url: './getChatConvo?username='+personName,
          success: function(data){
            console.log("success refreshing conversation");
            $(".chat").html(data);
          }
        });
        }
      }, 10000);

});
