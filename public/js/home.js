$(document).ready(function() {
  $('.left .person').mousedown(function(){ //on left click
      if ($(this).hasClass('.active')) { //don't change things if clicked user is already active user
          return false;
      } else {
          var personName = $(this).find('.name').text(); //span class ="name" shows name, grab that
          var conversation;
          $('.right .top .name').html(personName); //css value at top changes
          // now send an HTTP get request to call a python function that grabs DB data
          $.ajax({
            type: 'GET',
            url: './getChatConvo?username='+personName,
            success: function(data){
              console.log("success",data);
              $(".chat").html(data);
            }
          });
          $(".chat").scrollTop($(".chat")[0].scrollHeight);
          //$(".chat").prop({ scrollTop: $(".chat").prop("scrollHeight") });
          // $('.chat').animate({
          //          scrollTop: $(".chat").prop("scrollHeight")}, 0
          //       );
          // $(".chat").html(conversation);
          //$(".chat").load(location.href + " #chat");
      }
  });
});
