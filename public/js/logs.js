/*For the message logs page*/
$(document).ready(function () {
    $('.left .person').mousedown(function(){ //on left click on the left container pane
      var sentOrReceive = $(this).find('.name').text();
      $('.right .top .name').html(sentOrReceive); //css value at top changes
      // now send an HTTP get request to call a python function that grabs DB data
      if (sentOrReceive === "Sent messages") {
        $.ajax({
          type: 'GET',
          url: './displaySentMessage',
          success: function(data){
            console.log("success getting chat logs");
            $(".chat").html(data);
            return false;
          },
          });
      }
      else { //retrieve sent messages
        $.ajax({
          type: 'GET',
          url: './displayReceivedMessage',
          success: function(data){
            console.log("success getting chat logs");
            $(".chat").html(data);
            return false;
          },
          });
      }
      return false;
    });

    $('.left .top .write-link').mousedown(function(){ //on search button click
      var text = $('.search').find('input[name="msg_phrase"]').val();
      if(text === "") {
        alert("You did not specify a message to search for.");
        return false;
      }
      $('.right .top .name').html('Search results'); //css value at top changes
      // now send an HTTP get request to call a python function that grabs DB data
      $.ajax({
        type: 'GET',
        url: './searchMessage?msg_phrase='+text,
        success: function(data){
          console.log("success searching messages");
          $(".chat").html(data);
          return false;
        }
        });
      return false;
    });
});
