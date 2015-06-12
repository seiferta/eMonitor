

window.WebSocket=window.WebSocket || window.MozWebSocket || false;
if(!window.WebSocket){
    $('#ws').html("-");
    console.log('websockets not supportetd');
}else {
    ws = new WebSocket("ws://"+location.host+"/ws");
    ws.onclose=function(){
        $('#ws').html('<i class="fa fa-unlink fa-lg"></i>');
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
