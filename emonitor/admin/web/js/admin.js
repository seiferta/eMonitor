
window.WebSocket=window.WebSocket || window.MozWebSocket || false;
if(!window.WebSocket){
    $('#ws').html("-");
    console.log('websockets not supportetd');
}else {
    ws = new WebSocket("ws://"+location.host+"/ws");
    ws.onclose=function(){
        $('#ws').html('<i class="fa fa-eye-slash fa-lg"></i>');
    }
}
