$(document).ready(function () {
    setInterval(function() {
        $("#users-online").load("./getList");
        $("#list-of-users").load("./showList");
        $("#received-message-list").load("./displayReceivedMessage");
        $("#sent-message-list").load("./displaySentMessage")
    }, 8000);
});
