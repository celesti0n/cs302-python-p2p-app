// This .js file serves the files page.

$(document).ready(function () {
    $('.left .person').mousedown(function(){ //if a user clicks an option on the left side of the container box
      var sentOrReceive = $(this).find('.name').text(); //store the HTML text in a variable
      $('.right .top .name').html(sentOrReceive); //css value at top changes (received or sent messages)
      // now send an HTTP get request to call a python function that grabs DB data
      if (sentOrReceive === "Send a file") {
        $.ajax({
          type: 'GET',
          url: './displayFileForm',
          success: function(data){
            console.log("success getting file send form displayed");
            $(".chat").html(data);
            return false;
          },
          });
      }
      else { //view received Files
        $.ajax({
          type: 'GET',
          url: './displayFile',
          success: function(data){
            console.log("success getting recevied files displayed");
            $(".chat").html(data);
            return false;
          },
          });
      }
      return false;
    });
});
