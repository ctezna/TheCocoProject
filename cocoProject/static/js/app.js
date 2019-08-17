function post(path, params, method) {
    method = method || "post"; // Set method to post by default if not specified.
    var form = document.createElement("form");
    form.setAttribute("method", method);
    form.setAttribute("action", path);
    if(params){
        for(var key in params) {
            if(params.hasOwnProperty(key)) {
            var hiddenField = document.createElement("input");
            hiddenField.setAttribute("type", "hidden");
            hiddenField.setAttribute("name", key);
            hiddenField.setAttribute("value", params[key]);
            form.appendChild(hiddenField);
            }
        }
    }
    document.body.appendChild(form);
    form.submit();
}

function deleteData(url){
    post(url,null,'get');
}

function progress(){
    document.getElementById('prog').style.display = 'inline';
    document.getElementById('prog').style.width = '10%';
    setTimeout(function(){document.getElementById('prog').style.width = '40%';},1000);
    setTimeout(function(){document.getElementById('prog').style.width = '73%';},1000);
    setTimeout(function(){document.getElementById('prog').style.width = '99%';},1000);
}

function taskController(proxy, id, taskLabel){
    switch (taskLabel) {
        case 0:
            proxy = proxy + '/feed';
            break;
        case 1:
            proxy = proxy + '/lightOn';
            break;
        case 2:
            proxy = proxy + '/lightOff';
            break;
        case 3:
            proxy = proxy + '/ring';
            break;
    }
    $.post('/task', {
        data:proxy, 
        id:id
    }).done(function(response){
        $('#message').html('');
        $('#message').append(
              '<div class="alert alert-'+response.msgcat +' alert-dismissable fade show">'+
                '<button type="button" class="close" data-dismiss="alert">'+
                    '<span aria-hidden="true">&times;</span>'+
                    '<span class="sr-only">Close</span>'+
                '</button>'+
                response.msg+
              '</div>'
        );
    }).fail(function(){

    });
}

function playVid(id){
    document.getElementById('play;'+id).style.display = 'none';
    document.getElementById('frame;'+id).style.display = 'inline';
    document.getElementById('stop;'+id).style.display = 'inline';
    document.getElementById('ring;'+id).style.display = 'inline';
    document.getElementById('routine;'+id).style.display = 'none';
    document.getElementById('fullscreen;'+id).style.display = 'inline';
}
function stopVid(id){
    document.getElementById('play;'+id).style.display = 'inline';
    document.getElementById('frame;'+id).style.display = 'none';
    document.getElementById('stop;'+id).style.display = 'none';
    document.getElementById('ring;'+id).style.display = 'none';
    document.getElementById('fullscreen;'+id).style.display = 'none';
    document.getElementById('routine;'+id).style.display = 'inline';
}

function fullscreen() {
    // check if fullscreen mode is available
    if (document.fullscreenEnabled || 
        document.webkitFullscreenEnabled || 
        document.mozFullScreenEnabled ||
        document.msFullscreenEnabled) {
        
        // which element will be fullscreen
        var iframe = document.querySelector('#vid iframe');
        // Do fullscreen
        if (iframe.requestFullscreen) {
        iframe.requestFullscreen();
        } else if (iframe.webkitRequestFullscreen) {
        iframe.webkitRequestFullscreen();
        } else if (iframe.mozRequestFullScreen) {
        iframe.mozRequestFullScreen();
        } else if (iframe.msRequestFullscreen) {
        iframe.msRequestFullscreen();
        }
    }
    }

function fullscreenChange() {
    if (document.fullscreenEnabled ||
        document.webkitIsFullScreen || 
        document.mozFullScreen ||
        document.msFullscreenElement) {
        console.log('enter fullscreen');
    }
    else {
        console.log('exit fullscreen');
    }
    // force to reload iframe once to prevent the iframe source didn't care about trying to resize the window
    // comment this line and you will see
    var iframe = document.querySelector('iframe');
    //iframe.src = iframe.src;
}