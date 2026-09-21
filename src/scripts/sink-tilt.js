
(function(){
  var fine = matchMedia('(hover:hover) and (pointer:fine)').matches
          && !matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!fine) return;
  var TILT = 4, SHADOW_LIT = '0 10px 28px -12px rgba(0,0,0,.55)';
  document.querySelectorAll('.project,.badge,.xp').forEach(function(card){
    var tx = 0, ty = 0, cx = 0, cy = 0, raf = null, on = false;
    function frame(){
      cx += (tx - cx) * 0.18; cy += (ty - cy) * 0.18;
      var rx = (-cy) * TILT, ry = cx * TILT;
      card.style.transform = 'perspective(800px) rotateX(' + rx.toFixed(2) + 'deg) rotateY(' + ry.toFixed(2) + 'deg)';
      var X = ((cx + 1) * 50).toFixed(1), Y = ((cy + 1) * 50).toFixed(1);
      card.style.backgroundImage =
        'radial-gradient(42% 34% at ' + X + '% ' + Y + '%, rgba(0,0,0,.28), transparent),' +
        'radial-gradient(52% 42% at ' + (100 - X) + '% ' + (100 - Y) + '%, rgba(255,255,255,.07), transparent)';
      card.style.boxShadow = on ? '0 6px 16px -10px rgba(0,0,0,.5)' : SHADOW_LIT;
      if (Math.abs(tx - cx) <= .001 && Math.abs(ty - cy) <= .001 && !on) {
        raf = null; card.style.transform = ''; card.style.backgroundImage = ''; card.style.boxShadow = '';
      } else if (Math.abs(tx - cx) > .001 || Math.abs(ty - cy) > .001) {
        raf = requestAnimationFrame(frame);
      } else raf = null;
    }
    function kick(){ if (!raf) raf = requestAnimationFrame(frame); }
    card.addEventListener('pointerenter', function(){
      on = true; card.classList.add('sink-active'); kick();
    });
    card.addEventListener('pointermove', function(e){
      var r = card.getBoundingClientRect();
      tx = ((e.clientX - r.left) / r.width) * 2 - 1;
      ty = ((e.clientY - r.top) / r.height) * 2 - 1;
      kick();
    });
    card.addEventListener('pointerleave', function(){
      on = false; tx = 0; ty = 0; card.classList.remove('sink-active');
      card.style.backgroundImage = ''; card.style.transform = '';
      card.style.boxShadow = ''; kick();
    });
  });
})();
