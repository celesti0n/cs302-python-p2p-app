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
          $('.left .person').removeClass('active');
          $(this).addClass('active'); //whoever got clicked is now the 'active' chat, refer to refresh.js to how its used to refresh convos
          $('.chat').animate({
              scrollTop: $('.wrapper')[0].scrollHeight
          });
      }
  });
  $('.message-form').submit(function (e) {
    var msg = $('.message-form').find('input[name="message"]').val();
    var destination =  $('.right .top').find('.name').text();
    $.ajax({
      type: 'POST',
      url: './sendMessage',
      data: { destination: destination, message: msg},
      //data: $(this).serialize() //grab form data
      success: function(e){
        console.log("successful message sent");
        $.ajax({
          type: 'GET',
          url: './getChatConvo?username='+destination,
          success: function(data){
            console.log("success",data);
            $(".chat").html(data);
          }
        });
      }
    });
    e.preventDefault();
     return false;
    });
});
