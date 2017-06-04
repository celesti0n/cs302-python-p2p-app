$(document).ready(function () {
    setInterval(function() {
        $("#users-online").load("./getList");
        $("#list-of-total-users").load("./listAllUsers");
        $("#list-of-online-users").load("./showList");
        $("#received-message-list").load("./displayReceivedMessage");
        $("#sent-message-list").load("./displaySentMessage")
    }, 30000);
});
