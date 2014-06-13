

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


function closeOverlay(){
    $('.overlay').toggle();return false;
}


function showMonitorDefinition(){
    $.ajax({ type : "POST", url : "/data/monitors?action=monitoroverview",
        success: function(result) {
            $('#overlaycontent').html(result);
            $('.overlay').toggle();
            return false;
        }
    });
    return false;
}


$('.usermenu').hover(function() {
    $(this).find('.dropdown-menu').stop(true, true).delay(200).fadeIn(500);
    }, function() {
        $(this).find('.dropdown-menu').stop(true, true).delay(200).fadeOut(500);
});