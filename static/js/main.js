// ── PAGE LOADER ─────────────────────────────────────────────────────────────
window.addEventListener('load', () => {
  const loader = document.getElementById('loader');
  if (loader) {
    setTimeout(() => {
      loader.style.opacity = '0';
      setTimeout(() => loader.remove(), 500);
    }, 600);
  }
});

// ── TOAST AUTO DISMISS ───────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const toasts = document.querySelectorAll('.toast');
  toasts.forEach((t, i) => {
    setTimeout(() => {
      t.style.opacity = '0';
      t.style.transform = 'translateX(100%)';
      t.style.transition = 'all 0.4s';
      setTimeout(() => t.remove(), 400);
    }, 3000 + i * 500);
  });
});

// ── MOBILE NAV TOGGLE ────────────────────────────────────────────────────────
const menuToggle = document.getElementById('menuToggle');
const navMenu = document.getElementById('navMenu');
if (menuToggle && navMenu) {
  menuToggle.addEventListener('click', () => {
    const isOpen = navMenu.style.display === 'flex';
    navMenu.style.display = isOpen ? 'none' : 'flex';
    navMenu.style.flexDirection = 'column';
    menuToggle.innerHTML = isOpen ? '<i class="fa fa-bars"></i>' : '<i class="fa fa-times"></i>';
  });
}

// ── SCROLL NAVBAR SHADOW ─────────────────────────────────────────────────────
window.addEventListener('scroll', () => {
  const nb = document.getElementById('navbar');
  if (nb) {
    nb.style.boxShadow = window.scrollY > 50 ? '0 4px 20px rgba(0,0,0,0.3)' : '';
  }
});

// ── SMOOTH SCROLL FOR ANCHOR LINKS ──────────────────────────────────────────
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    const target = document.querySelector(a.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth' });
    }
  });
});

// ── CARD HOVER ANIMATION ─────────────────────────────────────────────────────
document.querySelectorAll('.card').forEach(card => {
  card.addEventListener('mouseenter', () => {
    card.style.transition = 'transform 0.3s, box-shadow 0.3s';
  });
});

// ── FORM VALIDATION FEEDBACK ─────────────────────────────────────────────────
const regForm = document.getElementById('regForm');
if (regForm) {
  regForm.addEventListener('submit', e => {
    let valid = true;
    regForm.querySelectorAll('[required]').forEach(field => {
      if (!field.value.trim()) {
        field.style.borderColor = '#C62828';
        valid = false;
      } else {
        field.style.borderColor = '';
      }
    });
    // Phone validation
    const phone = regForm.querySelector('[name="whatsapp"]');
    if (phone && phone.value.replace(/\D/g,'').length < 10) {
      phone.style.borderColor = '#C62828';
      valid = false;
      showToastMsg('Please enter a valid 10-digit WhatsApp number.', 'error');
    }
    if (!valid) {
      e.preventDefault();
      showToastMsg('Please fill all required fields.', 'error');
    }
  });
}

// ── GLOBAL TOAST ─────────────────────────────────────────────────────────────
function showToastMsg(msg, type) {
  const t = document.createElement('div');
  t.className = 'toast toast-' + type;
  t.textContent = msg;
  let c = document.getElementById('toastContainer');
  if (!c) {
    c = document.createElement('div');
    c.id = 'toastContainer';
    c.className = 'toast-container';
    document.body.appendChild(c);
  }
  c.appendChild(t);
  setTimeout(() => {
    t.style.opacity = '0';
    t.style.transform = 'translateX(100%)';
    t.style.transition = 'all 0.4s';
    setTimeout(() => t.remove(), 400);
  }, 3500);
}

// ── INTERSECTION OBSERVER (fade-in cards) ────────────────────────────────────
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.style.opacity = '1';
      entry.target.style.transform = 'translateY(0)';
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll('.card, .timeline-item').forEach(el => {
  el.style.opacity = '0';
  el.style.transform = 'translateY(20px)';
  el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
  observer.observe(el);
});
