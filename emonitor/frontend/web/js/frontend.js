

window.WebSocket=window.WebSocket || window.MozWebSocket || false;
if(!window.WebSocket){
    $('#ws').html("-");
    console.log('websockets not supportetd');
}else {
    ws = new WebSocket("ws://"+location.host+"/ws");
    var reloadtimer = null;
    var connection_info = "";

    $.ajax({ type : "POST", url : "/data/frontpage?action=translatebaseinfo",
        success: function(result) {
            connection_info = result.connection_info;
        }
    });


    ws.onclose=function(){
        setTimeout(function(){
            $('#overlaycontent').html(connection_info);
            $('.overlay').show();
        }, 2000);
        if(!reloadtimer){ reloadtimer = setInterval(tryReconnect, 5000);}
        $('#ws').html('<i class="fa fa-unlink fa-lg"></i>');
    };
    ws.onmessage=function(e){
        var d = JSON.parse(e.data);
        console.log(d);
        /*alert(d);*/
    }
}

function tryReconnect() {
    $.get(window.location.href).done(function () {
        location.reload();

    }).fail(function () {
        console.log('reload failed');
    });
}

function closeOverlay(){
    $('.overlay').toggle();return false;
}


function showMonitorDefinition(){
    $.ajax({ type : "POST", url : "/data/monitors?action=monitoroverview",
        success: function(result) {
            $('#overlaycontent').html(result);
            $('.overlay').show();
            $('.overlay').on('hide', function(){stopMonitorPing();});
            return false;
        }
    });
    return false;
}

function stopMonitorPing(){
    clearTimeout(nextrun);
}

$('.usermenu').hover(function() {
    $(this).find('.dropdown-menu').stop(true, true).delay(200).fadeIn(500);
    }, function() {
        $(this).find('.dropdown-menu').stop(true, true).delay(200).fadeOut(500);
});

(function ($) {
      $.each(['show', 'hide'], function (i, ev) {
          var el = $.fn[ev];
          $.fn[ev] = function () {
              this.trigger(ev);
              return el.apply(this, arguments);
          };
      });
})(jQuery);


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

function restartApp(){
    $.ajax({ type : "POST", url : "/data/frontpage?action=restart",
        success: function(result) {

        }
    });
    return false;
}
