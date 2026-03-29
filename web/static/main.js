/**
 * Mirage Studios — main.js
 * Interactions UI, animations et appels API
 */

// ── Smooth scroll pour les ancres ────────────────────────
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});

// ── Navbar scroll effect ──────────────────────────────────
const navbar = document.querySelector('.navbar');
if (navbar) {
  window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
      navbar.style.background = 'rgba(10,10,15,0.98)';
    } else {
      navbar.style.background = 'rgba(10,10,15,0.85)';
    }
  });
}

// ── Animate elements on scroll ───────────────────────────
const observerOptions = {
  threshold: 0.1,
  rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.style.opacity = '1';
      entry.target.style.transform = 'translateY(0)';
    }
  });
}, observerOptions);

document.querySelectorAll('.feature-card, .stat-card, .kpi-card, .module-card').forEach(el => {
  el.style.opacity = '0';
  el.style.transform = 'translateY(20px)';
  el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
  observer.observe(el);
});

// ── API Client (Mirage Studios Backend) ──────────────────
const MirageAPI = {
  baseUrl: '/api',

  async generateScript(config) {
    const res = await fetch(`${this.baseUrl}/script/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config)
    });
    return res.json();
  },

  async predictSuccess(projectId) {
    const res = await fetch(`${this.baseUrl}/prediction/${projectId}`);
    return res.json();
  },

  async getProjects() {
    const res = await fetch(`${this.baseUrl}/projects`);
    return res.json();
  },

  async renderVFXShot(shotId) {
    const res = await fetch(`${this.baseUrl}/vfx/render/${shotId}`, {
      method: 'POST'
    });
    return res.json();
  }
};

// ── Progress bar animation ────────────────────────────────
function animateProgressBars() {
  document.querySelectorAll('.progress-fill, .step-fill').forEach(bar => {
    const targetWidth = bar.style.width;
    bar.style.width = '0%';
    bar.style.transition = 'width 1s ease';
    setTimeout(() => { bar.style.width = targetWidth; }, 300);
  });
}

// ── Toast notifications ───────────────────────────────────
function showToast(message, type = 'info') {
  const toast = document.createElement('div');
  const colors = { info: '#7c5cfc', success: '#4ade80', error: '#f87171', warning: '#fb923c' };
  toast.style.cssText = `
    position: fixed; bottom: 24px; right: 24px; z-index: 9999;
    background: #16161e; border: 1px solid ${colors[type]};
    color: #f0f0f8; padding: 0.75rem 1.25rem; border-radius: 10px;
    font-size: 0.88rem; font-family: inherit;
    box-shadow: 0 8px 30px rgba(0,0,0,0.4);
    animation: slideIn 0.3s ease;
  `;
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => {
    toast.style.animation = 'slideOut 0.3s ease forwards';
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

// CSS for toast animations
const style = document.createElement('style');
style.textContent = `
  @keyframes slideIn { from { opacity:0; transform: translateX(20px); } to { opacity:1; transform: translateX(0); } }
  @keyframes slideOut { from { opacity:1; transform: translateX(0); } to { opacity:0; transform: translateX(20px); } }
`;
document.head.appendChild(style);

// ── Init ──────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  animateProgressBars();
  console.log('%c◈ MIRAGE STUDIOS', 'color:#7c5cfc; font-size:16px; font-weight:bold;');
  console.log('%cPython AI Engine — Production Ready', 'color:#8888aa; font-size:12px;');
});
