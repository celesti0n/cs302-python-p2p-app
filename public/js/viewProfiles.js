//On the profile viewing screen

$(document).ready(function() {
  var username = $('.right .top').find('.name').text(); //get current logged in user, don't change this
  $('.left .person').mousedown(function(){ //on left click of a user
    var personName = $(this).find('.name').text(); //span class = "name" shows name, grab that
    $('.right .top .name').html(personName); //css value at top changes
    // now send an HTTP get request to call a python function that grabs DB data
    $.ajax({
      type: 'GET',
      url: './grabProfile?profile_username='+personName+'&sender='+username,
      success: function(data){
        console.log("success getting profile");
        $(".chat").html(data);
        return false;
      },
      timeout: 2000,
      error: function(xmlhttprequest, textstatus, message) {
        if(textstatus==="timeout") {
          alert("5: Timeout Error, user probably not online");
          return false;
        }
      }
      });
    return false;
  });


  $('.left .top .write-link').mousedown(function(){ //on search button click
    var text = $('.search').find('input[name="profile_username"]').val(); //take the value written in input
    if(text === "") {
      alert("You did not specify a profile to search for."); //do not allow blank queries
      return false;
    }
    $('.right .top .name').html(text); //css value at top changes
    // now send an HTTP get request to call a python function that grabs DB data
    $.ajax({
      type: 'GET',
      url: './grabProfile?profile_username='+text+'&sender='+username,
      success: function(data){
        console.log("success getting profile");
        $(".chat").html(data);
        return false;
      },
      timeout: 2000,
      error: function(xmlhttprequest, textstatus, message) {
        if(textstatus==="timeout") {
          alert("5: Timeout Error, user probably not online");
          return false;
        }
        else {
          alert("User not found!");
          return false;
        }
      }
      });
    return false;
  });


});
