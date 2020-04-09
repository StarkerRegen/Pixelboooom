var ctx, cav;         // canvas
var socket;           // websocket
var interval = null;  // timer  
let isPC = true;
let x = 0, y = 0;
let x_c = 0, y_c = 0;
let u = 0, r = 0;
let styleId = 0;      // style for icon
let cavHistory = [];
let CanvasAutoResize = {
  draw: function() {
    let canvasContainer = document.getElementById('canvasContainer');
    if(canvasContainer.offsetWidth < 512)
      ctx.canvas.width  = canvasContainer.offsetWidth;
    else
      ctx.canvas.width = 512;
    ctx.canvas.height = ctx.canvas.width; 
    ctx.fillStyle="#FFFFFF";
    ctx.fillRect(0, 0, cav.width, cav.height);
    ctx.fillStyle="#000000";
    ctx.lineWidth = 6;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
  },
 
  initialize: function() {
    let self = CanvasAutoResize;
    self.draw();
    $(window).on('resize', function(event){
      self.draw();
      let len = cavHistory.length-u+r;
      if(len > 0) {
        Ops.show(len);
        socket.emit('cav', {id: styleId, data: cavHistory[len-1], refresh: false});
      }else {
        cavHistory.push(cav.toDataURL());
        socket.emit('cav', {id: styleId, data: cavHistory[0], refresh: true});
      }
    });
  }
};

let Tools = {
  pen: function(flag) {
    if(!flag) {
      ctx.lineTo(x_c, y_c);
      ctx.stroke();
    }
  },
  eraser: function(flag) {
    if(!flag) {
      ctx.clearRect(x_c, y_c, 10, 10);
    }
  },
  line: function(flag) {
    if(flag) {
      ctx.lineTo(x_c, y_c);
      ctx.stroke();
    }
  },
  circle: function(flag) {
    if(flag) {
      let x_m = 0.5*(x_c-x);
      let y_m = 0.5*(y_c-y);
      let r = Math.sqrt(Math.pow(x_m,2)+Math.pow(y_m,2));
      ctx.beginPath();
      ctx.arc(x+x_m,y+y_m,r,0,Math.PI*2);
      ctx.stroke();
    }
  }
}

let Ops = {
  delete: function(cur) {
    ctx.fillStyle="#FFFFFF";
    ctx.fillRect(0, 0, cav.width, cav.height);
    ctx.fillStyle="#000000";
    ctx.beginPath();
    cavHistory = [cav.toDataURL()];
    u = r = 0;
  },
  undo: function(cur) {
    u++;
    if(cur > 1) {
      Ops.show(cur-1);
      socket.emit('cav', {id: styleId, data: cavHistory[cur-2], refresh:false});
    }else {
      alert("Can't undo anymore.");
      u--;
    }
  },
  redo: function(cur) {
    r++;
    if(cur < cavHistory.length) {
      Ops.show(cur+1);
      socket.emit('cav', {id: styleId, data: cavHistory[cur], refresh:false});
    }else {
      alert("It's the newest cavPic.");
      r--;
    }
  },
  download: function(cur) {
    let MIME_TYPE = "image/png";
    let imgURL = cav.toDataURL(MIME_TYPE);
    let dlLink = document.createElement('a');
    let timestamp = new Date().getTime();
    dlLink.download = timestamp;
    dlLink.href = imgURL;
    dlLink.dataset.downloadurl = [MIME_TYPE, dlLink.download, dlLink.href].join(':');
    document.body.appendChild(dlLink);
    dlLink.click();
    document.body.removeChild(dlLink);
  },
  show: function(cur) {
    ctx.clearRect(0, 0, cav.width,cav.height);
    ctx.beginPath();
    let cavPic = new Image();
    cavPic.src = cavHistory[cur-1];
    cavPic.addEventListener('load', () => {
      ctx.drawImage(cavPic, 0, 0);
    });
  }
}

function Sketchpad() {
  $('.img-btn-group').on('click', '.img-btn', function(e) {
    $('.img-btn-group').removeClass('img-btn-active').find('img').css('background', '#333');
    $(this).addClass('img-btn-active').css('background', '#fff');     // 功能按钮按下背景改变
    let state = this.id;
    $('span#L').text(state);      // 显示被按下的按钮
    $('#sketchpad').off();
    if($(this).hasClass('left')) {
      if(isPC) {
        $('#sketchpad').mousedown(function(e) {
          x = e.offsetX;
          y = e.offsetY;
          $('span#R').text('X:' + x + ', Y:' + y);
          cavHistory.length = cavHistory.length-u+r;
          u = r = 0;
          ctx.beginPath();
          ctx.moveTo(x, y);
          $(this).mousemove(function(e) {
            x_c = e.offsetX;
            y_c = e.offsetY;
            $('span#R').text('X:' + x_c + ', Y:' + y_c);
            Tools[state](0);
            start();
          });
        });
        $('#sketchpad').mouseup(function(e) {
          x_c = e.offsetX;
          y_c = e.offsetY;
          $('span#R').text('X:' + x_c + ', Y:' + y_c);
          Tools[state](1);
          cavHistory.push(cav.toDataURL());
          $(this).off('mousemove');
        });
      }else {
        let sketchpad = document.getElementById('sketchpad');
        sketchpad.addEventListener('touchstart', function(e) {
          ctx.beginPath();
          var touch = e.targetTouches[0];
          x = touch.pageX - sketchpad.offsetLeft;
          y = touch.pageY - sketchpad.offsetTop;
          ctx.moveTo(x, y);
          $('span#R').text('X:' + x + ', Y:' + y);
          cavHistory.length = cavHistory.length-u+r;
          u = r = 0;
          sketchpad.addEventListener('touchmove', function(e) {
            touch = e.targetTouches[0];
            x_c = touch.pageX - sketchpad.offsetLeft;
            y_c = touch.pageY - sketchpad.offsetTop;
            Tools[state](0);
            start();
          }, false);
        }, false);
        sketchpad.addEventListener('touchend', function(e) {
          Tools[state](1);
          cavHistory.push(cav.toDataURL());
          $(this).off('touchmove');
        }, false);
      }
    }else {
      stop();
      if(!e.isPropagationStopped()) {
        let cur = cavHistory.length-u+r;
        Ops[state](cur);
      }
      e.stopPropagation();
    }
  });    
}

function sendcav() {
  let imgURL = cav.toDataURL('image/png');
  socket.emit('cav', {id: styleId, data: imgURL, refresh: false});
}

function start() {
  if(interval != null) {
    clearInterval(interval);
    interval = null;
  }
  interval = setInterval(sendcav, 600);
}

function stop() {
  clearInterval(interval);
  interval = null;
}

function refresh() {
  let imgURL = cav.toDataURL('image/png');
  socket.emit('cav', {id: styleId, data: imgURL, refresh: true});
}

function arrayBuffer2Base64(buffer) {
  let binary = '';
  const bytes = new Uint8Array(buffer);
  let len = bytes.byteLength;
  for(let i=0; i<len; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return binary;
}

$(function(argument) {
  namespace = '/playground';      
  socket = io.connect("http://"+ document.domain + ":" + location.port + namespace);     // 连接Socket.IO server
  socket.on('connect', function() {
    console.log('connect!');
  });                             // 建立新连接的回调函数
  socket.on('my response', function(msg) {
    let id = "";
    for(let i=0; i<12; i++) {
      let str = 'data_' + i;
      id = msg['id'] + i.toString();
      let src = 'data:image/png;base64,'+ arrayBuffer2Base64(msg[str]);
      document.getElementById(id).src = src;
    }
  });                             // 处理服务器发送的消息
  cav = document.getElementById('sketchpad');
  if (cav.getContext){
    ctx = cav.getContext('2d');
  } else {
    alert("Sorry, your browser can't support canvas");
  }
  CanvasAutoResize.initialize();    // 画布大小自适应
  if(/Android|webOS|iPhone|iPod|BlackBerry/i.test(navigator.userAgent)) {
    isPC = false;
  }
  console.log(isPC);
  Sketchpad();
  $('.style-nav').click(function() {
    styleId = this.id;
    refresh();
  });
  $('#refresh').click(refresh);
});
