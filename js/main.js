// ===== StrateGis — JavaScript principal =====
const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];

// Header + progress + glow
const hd=$('#hd'),pg=$('#prog'),gl=$('#glow');
addEventListener('scroll',()=>{hd.classList.toggle('s',scrollY>40);pg.style.transform=`scaleX(${scrollY/(document.body.scrollHeight-innerHeight)})`},{passive:true});
addEventListener('pointermove',e=>{gl.style.left=e.clientX+'px';gl.style.top=e.clientY+'px'},{passive:true});

// Theme toggle
const tgb=$('#tg'),root=document.documentElement;
function syncTg(){const l=root.dataset.theme==='light';tgb.setAttribute('aria-label',l?'Passer en mode sombre':'Passer en mode clair')}
syncTg();
tgb.onclick=()=>{const n=root.dataset.theme==='light'?'dark':'light';root.dataset.theme=n;try{localStorage.setItem('sg-theme',n)}catch(e){}syncTg()};

// Back to top
const tb=$('#top-btn'),pr=tb.querySelector('.p');
function place(){const max=document.documentElement.scrollHeight-innerHeight,p=max>0?Math.min(scrollY/max,1):0;
  const top=86+p*(innerHeight-86-70-52);tb.style.transform=`translateY(${top}px)`;pr.style.strokeDashoffset=151*(1-p);tb.classList.toggle('on',scrollY>320)}
addEventListener('scroll',place,{passive:true});addEventListener('resize',place);place();
tb.onclick=()=>scrollTo({top:0,behavior:'smooth'});

// Reveal + count-up
const io=new IntersectionObserver(es=>es.forEach(e=>{if(!e.isIntersecting)return;e.target.classList.add('in');
  e.target.querySelectorAll('[data-to]').forEach(b=>{const to=+b.dataset.to,suf=b.dataset.suf||'',t0=performance.now();
    (function f(t){const p=Math.min((t-t0)/1600,1),v=Math.round(to*(1-Math.pow(1-p,4)));b.textContent=v+suf;if(p<1)requestAnimationFrame(f)})(t0)});
  io.unobserve(e.target)}),{threshold:.15});
$$('.rv').forEach((el,i)=>{el.style.transitionDelay=(i%6)*60+'ms';io.observe(el)});

// Lightbox
const lb=$('#lb'),img=$('#lbi'),stg=$('#stg');let s=1,x=0,y=0,drag=null,last=null;
const apply=(anim)=>{img.style.transition=anim?'':'none';img.style.transform=`translate(calc(-50% + ${x}px),calc(-50% + ${y}px)) scale(${s})`;lb.classList.toggle('zoomed',s>1)};
function open(src,alt){img.src=src;img.alt=alt;s=1;x=y=0;lb.classList.add('on');document.body.style.overflow='hidden';last=document.activeElement;
  img.style.transition='none';img.style.transform='translate(-50%,-46%) scale(.92)';img.offsetWidth;requestAnimationFrame(()=>apply(true));$('#lx').focus()}
function close(){lb.classList.remove('on');document.body.style.overflow='';last&&last.focus()}
function zoom(n,cx=0,cy=0){n=Math.min(5,Math.max(1,n));const k=n/s;x=cx-(cx-x)*k;y=cy-(cy-y)*k;s=n;if(s===1)x=y=0;apply(true)}
$$('[data-zoom]').forEach(b=>b.addEventListener('click',()=>{const i=b.querySelector('img');open(i.src,i.alt)}));
$('#lx').onclick=close;
$('#zi').onclick=()=>zoom(s*1.5);$('#zo').onclick=()=>zoom(s/1.5);$('#zr').onclick=()=>zoom(1);
addEventListener('keydown',e=>{if(!lb.classList.contains('on'))return;if(e.key==='Escape')close();if(e.key==='+'||e.key==='=')zoom(s*1.5);if(e.key==='-')zoom(s/1.5)});
stg.addEventListener('wheel',e=>{e.preventDefault();zoom(s*(e.deltaY<0?1.2:1/1.2),e.clientX-innerWidth/2,e.clientY-innerHeight/2)},{passive:false});
let moved=0;
stg.addEventListener('pointerdown',e=>{drag={px:e.clientX,py:e.clientY,x,y};moved=0;stg.setPointerCapture(e.pointerId)});
stg.addEventListener('pointermove',e=>{if(!drag)return;const dx=e.clientX-drag.px,dy=e.clientY-drag.py;moved=Math.max(moved,Math.hypot(dx,dy));if(s>1&&moved>4){lb.classList.add('drag');x=drag.x+dx;y=drag.y+dy;apply(false)}});
stg.addEventListener('pointerup',e=>{lb.classList.remove('drag');if(drag&&moved<5){if(e.target===img)s>1?zoom(1):zoom(2.4,e.clientX-innerWidth/2,e.clientY-innerHeight/2);else close()}drag=null});

// ===== FORMSPREE (ID : mvkgjpjn) =====
const form=$('#devis-form'),status=$('#form-status'),submitBtn=$('#submit-btn');
form.addEventListener('submit',async e=>{
  e.preventDefault();
  const required=['nom','email','service','message'];
  let valid=true;
  required.forEach(id=>{
    const el=document.getElementById(id);
    if(!el.value.trim()){el.style.borderColor='#F87171';valid=false}
    else{el.style.borderColor=''}
  });
  const email=document.getElementById('email');
  if(email.value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)){email.style.borderColor='#F87171';valid=false}
  if(!valid){
    status.className='form-status err';
    status.textContent='⚠️ Merci de remplir tous les champs obligatoires.';
    return;
  }
  submitBtn.disabled=true;
  submitBtn.innerHTML='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:18px;height:18px;animation:spin 1s linear infinite"><path d="M21 12a9 9 0 1 1-6.2-8.5"/></svg> Envoi en cours...';
  status.className='form-status';status.textContent='';
  try{
    const res=await fetch(form.action,{method:'POST',body:new FormData(form),headers:{Accept:'application/json'}});
    if(res.ok){
      status.className='form-status ok';
      status.textContent='✅ Merci ! Votre demande a bien été envoyée. Nous vous répondrons sous 24h.';
      form.reset();
    }else{
      const data=await res.json().catch(()=>({}));
      throw new Error((data.errors&&data.errors.map(x=>x.message).join(', '))||'Erreur inconnue');
    }
  }catch(err){
    status.className='form-status err';
    status.textContent='❌ Oups, une erreur est survenue. Écrivez-nous directement à strategisobf@gmail.com';
  }finally{
    submitBtn.disabled=false;
    submitBtn.innerHTML='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:18px;height:18px"><path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/></svg> Envoyer ma demande';
  }
});

// Sound
let ctx,playing=false;const sb=$('#snd');
const mel=[[261.63,0,.32,.09],[329.63,.16,.32,.09],[392,.32,.32,.09],[523.25,.48,.55,.1],[392,.95,.45,.07],[523.25,1.2,.7,.1]];
sb.onclick=()=>{ctx=ctx||new(window.AudioContext||window.webkitAudioContext)();if(ctx.state==='suspended')ctx.resume();if(playing)return;playing=true;sb.classList.add('playing');sb.setAttribute('aria-pressed','true');
  mel.forEach(([f,st,d,g])=>{const o=ctx.createOscillator(),n=ctx.createGain(),t=ctx.currentTime+st;o.type='triangle';o.frequency.value=f;n.gain.value=0;o.connect(n);n.connect(ctx.destination);o.start(t);n.gain.linearRampToValueAtTime(g,t+.04);n.gain.exponentialRampToValueAtTime(.0001,t+d);o.stop(t+d+.05)});
  setTimeout(()=>{playing=false;sb.classList.remove('playing');sb.setAttribute('aria-pressed','false')},2100)};

/* ============================================ */
/* ===== VIDEO PROMO ===== */
/* ============================================ */
(function() {
  const video = document.getElementById('promo-video');
  const player = video ? video.closest('.video-player') : null;
  const playBtn = document.getElementById('video-play-btn');

  if (!video || !player || !playBtn) return;

  // Click sur le bouton play → lance la vidéo
  playBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    video.play();
  });

  // Click sur la vidéo → toggle play/pause
  video.addEventListener('click', () => {
    if (video.paused) {
      video.play();
    } else {
      video.pause();
    }
  });

  // Synchronise la classe 'playing' avec l'état de la vidéo
  video.addEventListener('play', () => {
    player.classList.add('playing');
  });

  video.addEventListener('pause', () => {
    player.classList.remove('playing');
  });

  video.addEventListener('ended', () => {
    player.classList.remove('playing');
    video.currentTime = 0;
  });

  // Auto-play au scroll (une seule fois, sans son)
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting && !video.dataset.autoplayed) {
        video.dataset.autoplayed = 'true';
        // Petit délai pour laisser le scroll finir
        setTimeout(() => {
          if (video.paused && !video.dataset.userPaused) {
            // Optionnel : décommentez pour activer l'autoplay silencieux
            // video.muted = true;
            // video.play().catch(() => {});
          }
        }, 800);
      }
    });
  }, { threshold: 0.5 });

  observer.observe(player);

  // Mémorise si l'utilisateur a mis en pause manuellement
  video.addEventListener('pause', () => {
    if (!video.ended) video.dataset.userPaused = 'true';
  });

  video.addEventListener('play', () => {
    delete video.dataset.userPaused;
  });
})();