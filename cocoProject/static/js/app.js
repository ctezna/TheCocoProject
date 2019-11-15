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

function pantiltControl(move, proxy){
    $.ajax(proxy + '/camOff').done(function(){
        $.ajax('https://ctezna.ngrok.io/cam/move/'+ move).done(function(){
            console.log("done");
        });
    });

}

function progress(){
    document.getElementById('prog').style.display = 'inline';
    document.getElementById('prog').style.width = '10%';
    setTimeout(function(){document.getElementById('prog').style.width = '40%';},1000);
    setTimeout(function(){document.getElementById('prog').style.width = '73%';},1000);
    setTimeout(function(){document.getElementById('prog').style.width = '99%';},1000);
}

function taskController(proxy, id, taskLabel, horus=null){
    switch (taskLabel) {
        case 0:
            proxy = proxy + '/feed';
            break;
        case 1:
            var colorRGB = hexToRgb(document.getElementById('color'+id).value);
            var brightness = document.getElementById('brightInput'+id).value;
            proxy = proxy + '/light?red='+colorRGB.r+'&green='+colorRGB.g+'&blue='+colorRGB.b+'&brightness='+brightness;
            if (horus){
                proxy = 'https://ctezna.ngrok.io/light/on?red='+colorRGB.r+'&green='+colorRGB.g+'&blue='+colorRGB.b+'&brightness='+brightness;
            }
            document.getElementById('lightOn'+id).style.display = 'none';
            document.getElementById('lightBright'+id).style.display = 'inline';
            document.getElementById('lightOff'+id).style.display = 'inline';
            break;
        case 2:
            proxy = proxy + '/light?red=0&green=0&blue=0&brightness=0';
            if (horus){
                proxy = 'https://ctezna.ngrok.io/light/off';
            }
            document.getElementById('lightOff'+id).style.display = 'none';
            break;
        case 3:
            proxy = proxy + '/ring';
            break;
        case 4:
            proxy = proxy + '/camOff';
            break;
        case 5:
            proxy = proxy + '/reboot';
            break;
        case 6:
            proxy = proxy + '/light?red=-1&green=-1&blue=-1&brightness=0.2';
            document.getElementById('lightBright'+id).style.display = 'inline';
            document.getElementById('lightOff'+id).style.display = 'inline';
            break;
    }
    $.post('/task', {
        data:proxy, 
        id:id
    }).done(function(response){
        if (response.msg.length > 1){
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
        }
        if (response.cocoLight == true){
            $('#lightOff'+response.cocoId).attr('style', 'display: inline-block;');
            $('#lightOn'+response.cocoId).attr('style', 'display: none;');
            $('#lightBright'+response.cocoId).attr('style', 'display: inline-block;');
            $('#color'+response.cocoId).attr('value', response.lightColor);
            $('#brightInput'+response.cocoId).attr('value', response.lightBrightness);
        }else {
            $('#lightOn'+response.cocoId).attr('style', 'display: inline-block;');
            $('#lightBright'+response.cocoId).attr('style', 'display: none;');
            $('#lightOff'+response.cocoId).attr('style', 'display: none;');
            $('#color'+response.cocoId).attr('value', response.lightColor);
            $('#brightInput'+response.cocoId).attr('value', response.lightBrightness);
        }   
    }).fail(function(){

    });
}

function hexToRgb(hex) {
    var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16)
    } : null;
  }

function proxyGen(cocoId){
    $('#loading'+cocoId).attr('style', 'display:inline;');
    $('#frame'+cocoId).attr('style', 'display:none;');
    $.ajax('/proxyGen/'+ cocoId).done(function(data){
        var frameName = '#frame'+data[0].cocoId.toString();
        var url = data[0].cocoProxy + '/cam';
        var $iframe = $(frameName);
        if ( $iframe.length ) {
            $iframe.attr('src',url);
            $iframe.attr('style', 'display: inline; width:80%; height: 80%;');
            $('#loading'+data[0].cocoId).attr('style', 'display:none;');
        }
    });
}

function playVid(id){
    document.getElementById('play;'+id).style.display = 'none';
    proxyGen(id);
    document.getElementById('stop;'+id).style.display = 'inline';
    document.getElementById('ring;'+id).style.display = 'inline';
    document.getElementById('refresh;'+id).style.display = 'inline';
    document.getElementById('left;'+id).style.display = 'inline';
    document.getElementById('right;'+id).style.display = 'inline';
    document.getElementById('up;'+id).style.display = 'inline';
    document.getElementById('down;'+id).style.display = 'inline';
    document.getElementById('center;'+id).style.display = 'inline';
}
function stopVid(id, proxy){
    document.getElementById('play;'+id).style.display = 'inline';
    taskController(proxy,id,4);
    document.getElementById('frame'+id).src = '';
    document.getElementById('frame'+id).style.display = 'none';
    document.getElementById('stop;'+id).style.display = 'none';
    document.getElementById('ring;'+id).style.display = 'none';
    document.getElementById('refresh;'+id).style.display = 'none';
    document.getElementById('left;'+id).style.display = 'none';
    document.getElementById('right;'+id).style.display = 'none';
    document.getElementById('up;'+id).style.display = 'none';
    document.getElementById('down;'+id).style.display = 'none';
    document.getElementById('center;'+id).style.display = 'none';
}

function fullscreen() {
    // check if fullscreen mode is available
    if (document.fullscreenEnabled || 
        document.webkitFullscreenEnabled || 
        document.mozFullScreenEnabled ||
        document.msFullscreenEnabled) {
        
        // which element will be fullscreen
        var iframe = document.querySelector('#vid img');
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