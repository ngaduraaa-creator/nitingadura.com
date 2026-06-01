/* =========================================================
   GADURA REAL ESTATE — CONVERSION WIDGETS
   WhatsApp float, urgency bar, exit-intent, trust badges
   ========================================================= */

(function(){
  'use strict';

  var PHONE = '19177050132';
  var PHONE_DISPLAY = '(917) 705-0132';
  var WHATSAPP_MSG = encodeURIComponent('Hi Nitin, I found your website and I\'m interested in buying/selling a home in Queens. Can you help?');

  /* ---- 1. WHATSAPP FLOATING BUTTON ---- */
  (function(){
    var wa = document.createElement('a');
    wa.href = 'https://wa.me/' + PHONE + '?text=' + WHATSAPP_MSG;
    wa.target = '_blank';
    wa.rel = 'noopener';
    wa.className = 'whatsapp-float';
    wa.setAttribute('aria-label', 'Chat on WhatsApp');
    wa.innerHTML = '<svg viewBox="0 0 32 32" width="28" height="28" fill="#fff"><path d="M16.004 0h-.008C7.174 0 0 7.176 0 16.004c0 3.5 1.132 6.744 3.054 9.378L1.054 31.2l6.042-1.94a15.93 15.93 0 008.908 2.7C24.826 31.96 32 24.784 32 16.004 32 7.176 24.826 0 16.004 0zm9.334 22.594c-.394 1.11-1.95 2.03-3.188 2.298-.846.18-1.952.324-5.672-1.22-4.762-1.974-7.82-6.802-8.058-7.116-.228-.314-1.918-2.556-1.918-4.874s1.214-3.456 1.644-3.928c.43-.472.94-.59 1.254-.59.314 0 .628.002.902.016.29.014.678-.11.06 1.566-.292.668-1.546 3.77-1.684 4.044-.136.274-.228.594-.046.942.182.348.274.564.548.872.274.308.576.688.822.924.274.262.56.546.88.848.296.278.578.578.896.858.294.26.566.542.882.83.332.302.622.582.936.85.3.254.622.486.962.684.296.172.59.318.87.422.434.16.82.136 1.128-.078.308-.214 1.34-1.564 1.528-2.1.188-.536.376-.448.634-.322.258.128 1.63.77 1.91.91.28.14.466.208.534.324.068.118.068.668-.326 1.778z"/></svg>';
    document.body.appendChild(wa);
  })();

  /* ---- 2. URGENCY BAR ---- */
  (function(){
    // Check if dismissed recently
    var dismissed = localStorage.getItem('gadura_urgency_dismissed');
    if(dismissed){
      var ts = parseInt(dismissed, 10);
      if(Date.now() - ts < 86400000) return; // 24 hours
    }

    var bar = document.createElement('div');
    bar.className = 'urgency-bar';
    bar.innerHTML = '<span class="urgency-text">🔥 Queens market is HOT — homes selling in 14 days avg. <a href="/sell.html" style="color:#6dffb3;font-weight:700;text-decoration:underline;">Get your free valuation →</a></span><button class="urgency-close" aria-label="Dismiss">×</button>';

    var header = document.querySelector('.site-header') || document.querySelector('header');
    if(header && header.parentNode){
      header.parentNode.insertBefore(bar, header);
    } else {
      document.body.insertBefore(bar, document.body.firstChild);
    }

    bar.querySelector('.urgency-close').addEventListener('click', function(){
      bar.style.display = 'none';
      localStorage.setItem('gadura_urgency_dismissed', Date.now().toString());
    });
  })();

  /* ---- 3. EXIT INTENT OVERLAY ---- */
  (function(){
    if(sessionStorage.getItem('gadura_exit_shown')) return;
    var shown = false;

    function showExitIntent(){
      if(shown) return;
      shown = true;
      sessionStorage.setItem('gadura_exit_shown', '1');

      var overlay = document.createElement('div');
      overlay.className = 'exit-overlay';
      overlay.innerHTML = '<div class="exit-card">' +
        '<button class="exit-close" aria-label="Close">×</button>' +
        '<h2 style="font-size:1.6rem;margin-bottom:8px;color:#1B2A6B;">Wait! Before You Go…</h2>' +
        '<p style="color:#555;margin-bottom:16px;line-height:1.6;">Get a <strong>free home valuation</strong> for your Queens, Brooklyn, or Long Island property — no obligation, no pressure.</p>' +
        '<a href="tel:+' + PHONE + '" class="exit-cta-call">📞 Call Nitin Now: ' + PHONE_DISPLAY + '</a>' +
        '<a href="/sell.html#valuation-form" class="exit-cta-form">Get Free Home Valuation Online →</a>' +
        '<p style="font-size:.75rem;color:#999;margin-top:16px;">Licensed NYS Agent · 500+ Families Served · 5-Star Google Reviews</p>' +
        '</div>';
      document.body.appendChild(overlay);

      // Animate in
      requestAnimationFrame(function(){
        overlay.classList.add('visible');
      });

      overlay.querySelector('.exit-close').addEventListener('click', function(){
        overlay.classList.remove('visible');
        setTimeout(function(){ overlay.remove(); }, 300);
      });
      overlay.addEventListener('click', function(e){
        if(e.target === overlay){
          overlay.classList.remove('visible');
          setTimeout(function(){ overlay.remove(); }, 300);
        }
      });
    }

    // Desktop: mouse leaves viewport top
    document.addEventListener('mouseout', function(e){
      if(!e.relatedTarget && e.clientY < 5){
        showExitIntent();
      }
    });

    // Mobile: back button / scroll-up after 30s
    var scrollTimer = null;
    var pageTime = Date.now();
    window.addEventListener('scroll', function(){
      if(Date.now() - pageTime < 30000) return;
      if(window.scrollY < 200 && !shown){
        if(!scrollTimer){
          scrollTimer = setTimeout(function(){
            if(window.scrollY < 200) showExitIntent();
            scrollTimer = null;
          }, 2000);
        }
      }
    }, { passive: true });
  })();

  /* ---- 4. TRUST BADGES (inject after hero or first section) ---- */
  (function(){
    // Only on main pages, not blog posts or deep pages
    var path = window.location.pathname;
    if(path.split('/').length > 3) return; // Skip deep pages

    var badges = [
      { icon: '🏠', text: 'NYS Licensed Brokerage' },
      { icon: '⭐', text: '5-Star Google Reviews' },
      { icon: '👨‍👩‍👧‍👦', text: '500+ Families Served' },
      { icon: '💰', text: 'Free Home Valuations' },
    ];

    var existing = document.querySelector('.trust-badges');
    if(existing) return;

    var container = document.createElement('div');
    container.className = 'trust-badges';
    container.innerHTML = badges.map(function(b){
      return '<span class="trust-badge">' + b.icon + ' ' + b.text + '</span>';
    }).join('<span class="trust-sep">·</span>');

    // Insert after hero section or first section
    var hero = document.querySelector('.hero') || document.querySelector('.hero-section') || document.querySelector('section');
    if(hero && hero.nextSibling){
      hero.parentNode.insertBefore(container, hero.nextSibling);
    }
  })();

  /* ---- 5. GA4 TRACKING FOR WIDGETS ---- */
  (function(){
    // Track WhatsApp clicks
    var waBtn = document.querySelector('.whatsapp-float');
    if(waBtn && window.gtag){
      waBtn.addEventListener('click', function(){
        gtag('event', 'click', { event_category: 'WhatsApp', event_label: 'Floating Button' });
      });
    }

    // Track exit intent interactions
    document.addEventListener('click', function(e){
      if(!window.gtag) return;
      if(e.target.closest('.exit-cta-call')){
        gtag('event', 'click', { event_category: 'Exit Intent', event_label: 'Phone Call' });
      }
      if(e.target.closest('.exit-cta-form')){
        gtag('event', 'click', { event_category: 'Exit Intent', event_label: 'Valuation Link' });
      }
    });
  })();

})();
