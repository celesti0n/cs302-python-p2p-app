$(document).ready(function() {
  var username = $('.right .top').find('.name').text(); //get current logged in user, don't change this
  $('.left .person').mousedown(function(){ //on left click
    var personName = $(this).find('.name').text(); //span class ="name" shows name, grab that
    $('.right .top .name').html(personName); //css value at top changes
    // now send an HTTP get request to call a python function that grabs DB data
    $.ajax({
      type: 'POST',
      url: './grabProfile?profile_username='+personName+'&sender='+username,
      success: function(data){
        console.log("success getting profile");
        $(".chat").html(data);
      },
      timeout: 2000,
      error: function(xmlhttprequest, textstatus, message) {
        if(textstatus==="timeout") {
          alert("5: Timeout Error, user probably not online");
        }
      }
      });
    return false;
  });
});
