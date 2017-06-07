$(document).ready(function() {
  $('.left .person').mousedown(function(){ //on left click
    var personName = $(this).find('.name').text(); //span class ="name" shows name, grab that
    $('.right .top .name').html(personName); //css value at top changes
    // now send an HTTP get request to call a python function that grabs DB data
    $.ajax({
      type: 'GET',
      url: './getChatConvo?username='+personName,
      success: function(data){
        console.log("success getting convo");
        $(".chat").html(data);
      }
    });
    $('.chat').animate({
        scrollTop: $('.wrapper')[0].scrollHeight
    });
  });
  $('.message-form').submit(function () {
    var msg = $('.message-form').find('input[name="message"]').val();
    var destination =  $('.right .top').find('.name').text();
    console.log(msg)
    console.log(destination)
    $.ajax({
      type: 'POST',
      url: './sendMessage?destination='+destination+'&message='+msg,
      timeout: 5000,
      success: function(e){
        $('.message-form').find('input[name="message"]').val("");
        alert("Message sent!");
      },
      error: function(xmlhttprequest, textstatus, message) {
        if(textstatus==="timeout") {
          alert("5: Timeout Error");
        }
      },
    });
    return false;
  });
});
