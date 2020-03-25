var ctx, cav;
let x = 0, y = 0;
let u = 0, r = 0;
let cavHistory = [];
let CanvasAutoResize = {
  draw: function() {
    let canvasContainer = document.getElementById('canvasContainer');
    ctx.canvas.width  = canvasContainer.offsetWidth;
    ctx.canvas.height = ctx.canvas.width;
    ctx.lineWidth = 6;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
  },
 
  initialize: function() {
    let self = CanvasAutoResize;
    self.draw();
    $(window).on('resize', function(event){
      self.draw();
    });
  }
};

let Tools = {
  pen: function(e, flag) {
    if(!flag) {
      $('span#R').text('X:' + e.offsetX + ', Y:' + e.offsetY);
      ctx.lineTo(e.offsetX, e.offsetY);
      ctx.stroke();
    }
  },
  eraser: function(e, flag) {
    if(!flag) {
      $('span#R').text('X:' + e.offsetX + ', Y:' + e.offsetY);
      ctx.clearRect(e.offsetX, e.offsetY, 10, 10);
    }
  },
  line: function(e, flag) {
    if(flag) {
      ctx.lineTo(e.offsetX, e.offsetY);
      ctx.stroke();
    }
  },
  circle: function(e, flag) {
    if(flag) {
      let x_m = 0.5*(e.offsetX-x);
      let y_m = 0.5*(e.offsetY-y);
      let r = Math.sqrt(Math.pow(x_m,2)+Math.pow(y_m,2));
      ctx.beginPath();
      ctx.arc(x+x_m,y+y_m,r,0,Math.PI*2);
      ctx.stroke();
    }
  }
}

let Ops = {
  delete: function(cur) {
    ctx.clearRect(0, 0, cav.width,cav.height);
    ctx.beginPath();
    cavHistory = [cav.toDataURL()];
    u = r = 0;
  },
  undo: function(cur) {
    u++;
    if(cur > 1) {
      Ops.show(cur-1);
    }else {
      alert("Can't undo anymore.");
      u--;
    }
  },
  redo: function(cur) {
    r++;
    if(cur < cavHistory.length) {
      Ops.show(cur+1);
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
      $('#sketchpad').off();
      $('#sketchpad').mousedown(function(e) {
        x = e.offsetX;
        y = e.offsetY;
        $('span#R').text('X:' + x + ', Y:' + y);
        cavHistory.length = cavHistory.length-u+r;
        u = r = 0;
        ctx.beginPath();
        ctx.moveTo(x, y);
        $(this).mousemove(function(e) {
          Tools[state](e, 0);
        });
      });
      $('#sketchpad').mouseup(function(e) {
        Tools[state](e, 1);
        cavHistory.push(cav.toDataURL());
        $(this).off('mousemove');
      });
    }else {
      if(!e.isPropagationStopped()) {
        let cur = cavHistory.length-u+r;
        Ops[state](cur);
      }
      e.stopPropagation();
    }
  });                           
}

$(function(argument) {
  cav = document.getElementById('sketchpad');
  if (cav.getContext){
    ctx = cav.getContext('2d');
  } else {
    alert("Sorry, your browser can't support canvas");
  }
  CanvasAutoResize.initialize();    // 画布大小自适应 
  cavHistory.push(cav.toDataURL());
  Sketchpad();
});
