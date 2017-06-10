/*Styles the chat messaging page, home.html*/

$(document).ready(function() {
  $('.left .person').mousedown(function(){ //on left click of a person
    var personName = $(this).find('.name').text(); //span class ="name" shows name, grab that
    $('.right .top .name').html(personName); //css value at top changes to show the currently selected user
    // now send an HTTP get request to call a python function that grabs DB data
    $.ajax({
      type: 'GET',
      url: './getChatConvo?username='+personName,
      success: function(data){
        console.log("success getting convo");
        $(".chat").html(data); //reload the chat class with the contents of this AJAX request
      }
    });
    $('.chat').animate({
        scrollTop: $('.wrapper')[0].scrollHeight //scroll to the bottom of the messaging screen when clicked
    });
  });
  $('.message-form').submit(function () { //if a message is submitted on enter press
    var msg = $('.message-form').find('input[name="message"]').val(); //the message is written in the input
    var destination =  $('.right .top').find('.name').text(); //the destination if the user of the top right
    var markdown = $('.message-form').find('select[name="markdown"]').val(); //the markdown argument is the value of the dropdown
    console.log(msg)
    console.log(destination)
    console.log(markdown)
    $.ajax({
      type: 'POST',
      url: './sendMessage?destination='+destination+'&message='+msg+'&markdown='+markdown,
      timeout: 10000,
      success: function(e){
        $('.message-form').find('input[name="message"]').val("");
        alert("Message sent!");
      },
      error: function(xmlhttprequest, textstatus, message) {
        if(textstatus==="timeout") {
          alert("5: Timeout Error"); //after 10 seconds, show this
        }
      },
    });
    return false;
  });
});
