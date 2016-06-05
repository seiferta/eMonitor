
window.WebSocket=window.WebSocket || window.MozWebSocket || false;
if(!window.WebSocket){
    $('#ws').html("-");
    console.log('websockets not supportetd');
}else {
    ws = new WebSocket("ws://"+location.host+"/ws");
    ws.onclose=function(){
        $('#ws').html('<i class="fa fa-unlink fa-lg"></i>');
    };
}

function showInfo(){
    $.ajax({ type : "POST", url : "/data/frontpage?action=info",
        success: function(result) {
            $('#overlaycontent').html(result);
            $('.overlay').toggle();
            return false;
        }
    });
    return false;
}
