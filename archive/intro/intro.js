function playIntro(){
  if(introDone){show('loginScreen');return;}
  // hide title, show intro screen on top
  var ts=document.getElementById('titleScreen');if(ts)ts.classList.remove('active');
  var is=document.getElementById('introScreen');if(!is){show('loginScreen');return;}
  is.style.display='flex';
  var iv=document.getElementById('introVid');
  if(!iv){endIntro();return;}
  try{iv.muted=true;iv.currentTime=0;iv.load();}catch(e){}
  if(introTimer)clearTimeout(introTimer);
  introTimer=setTimeout(endIntro,6000); // safety: video ~4s
  var pr=iv.play();
  if(pr&&pr.then){pr.then(function(){}).catch(function(){
    var sk=document.getElementById('introSkip');if(sk)sk.textContent='TAP TO PLAY \u25B6';
    var h=function(){iv.play().catch(function(){endIntro();});is.removeEventListener('click',h);};
    is.addEventListener('click',h);
  });}
  if(!iv.__ended){iv.__ended=true;iv.addEventListener('ended',endIntro);}
}
function endIntro(){
  introDone=true;
  if(introTimer){clearTimeout(introTimer);introTimer=null;}
  var iv=document.getElementById('introVid');if(iv){try{iv.pause();}catch(e){}}
  var is=document.getElementById('introScreen');if(is)is.style.display='none';
  show('loginScreen');
}
