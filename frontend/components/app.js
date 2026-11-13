const API_BASE_URL = window.RESEARCH_API_URL || 'http://localhost:8000';
const API = API_BASE_URL.replace(/\/+$/, '') + '/api';

const Auth = {
  get: () => JSON.parse(localStorage.getItem('ra_user') || 'null'),
  set: (u) => localStorage.setItem('ra_user', JSON.stringify(u)),
  clear: () => localStorage.removeItem('ra_user'),
  require: () => {
    if (!Auth.get()) { window.location.href = '../index.html'; return false; }
    return true;
  }
};

async function apiGet(path) {
  const r = await fetch(API + path);
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}
async function apiPost(path, body) {
  const r = await fetch(API + path, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body) });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}
async function apiDelete(path) {
  const r = await fetch(API + path, { method:'DELETE' });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

const SIDEBAR_ICONS = {
  dashboard: '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/><rect width="7" height="9" x="14" y="12" rx="1"/><rect width="7" height="5" x="3" y="16" rx="1"/></svg>',
  research:  '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>',
  history:   '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M12 7v5l4 2"/></svg>',
};

const LOGO_SVG = '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96-.46 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 4.44-1.14Z"/><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96-.46 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-4.44-1.14Z"/></svg>';

const MOON_SVG = '<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>';
const SUN_SVG  = '<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/></svg>';

function initTheme() {
  const saved = localStorage.getItem('nr_theme') || 'dark';
  document.documentElement.setAttribute('data-theme', saved);
}

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme');
  const next = current === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('nr_theme', next);
  updateThemeBtn();
}

function updateThemeBtn() {
  const btn = document.getElementById('theme-toggle-btn');
  if (!btn) return;
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  btn.innerHTML = isDark ? SUN_SVG : MOON_SVG;
  btn.title = isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode';
}

initTheme();

function initSidebar(activePage) {
  const user = Auth.get();
  if (!user) return;

  document.querySelectorAll('.logo-icon').forEach(el => el.innerHTML = LOGO_SVG);

  const links = [
    { id:'dashboard', icon: SIDEBAR_ICONS.dashboard, label:'Dashboard', href:'dashboard.html' },
    { id:'research',  icon: SIDEBAR_ICONS.research,  label:'New Research', href:'research.html' },
    { id:'history',   icon: SIDEBAR_ICONS.history,   label:'History', href:'history.html' },
  ];
  document.getElementById('sidebar-nav').innerHTML = links.map(l => `
    <a href="${l.href}" class="nav-link ${activePage === l.id ? 'active' : ''}">
      <span class="icon">${l.icon}</span>
      <span>${l.label}</span>
    </a>`).join('');

  document.getElementById('user-name').textContent = user.name;
  document.getElementById('user-avatar').textContent = user.name[0].toUpperCase();
  document.getElementById('logout-btn').onclick = () => { Auth.clear(); window.location.href = '../index.html'; };

  const toggleBtn = document.getElementById('theme-toggle-btn');
  if (toggleBtn) toggleBtn.onclick = toggleTheme;
  updateThemeBtn();
}

function renderMarkdown(md) {
  if (!md) return '';
  return md
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/`(.+?)`/g, '<code>$1</code>')
    .replace(/^\- (.+)$/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>')
    .replace(/^\d+\. (.+)$/gm, '<li>$1</li>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/^(?!<[hul])/gm, '')
    .replace(/<p><\/p>/g, '');
}

const KW_COLORS = [
  ['rgba(108,99,255,0.15)', '#a78bfa'],
  ['rgba(34,211,165,0.15)', '#22d3a5'],
  ['rgba(245,158,11,0.15)', '#f59e0b'],
  ['rgba(239,68,68,0.15)', '#ef4444'],
  ['rgba(59,130,246,0.15)', '#60a5fa'],
];

function renderKeywordCloud(keywords, containerId) {
  const el = document.getElementById(containerId);
  if (!el || !keywords?.length) return;
  el.innerHTML = keywords.map((k, i) => {
    const [bg, color] = KW_COLORS[i % KW_COLORS.length];
    const size = 0.75 + (k.score || k.count / 10 || 0.1) * 0.5;
    return `<span class="kw-tag" style="background:${bg};color:${color};font-size:${size}rem">${k.word}</span>`;
  }).join('');
}

function initTabs(containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;
  container.querySelectorAll('.tab-btn').forEach(btn => {
    btn.onclick = () => {
      container.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      container.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      container.querySelector('#' + btn.dataset.tab).classList.add('active');
    };
  });
}

function depthBadge(depth) {
  const cls = { Basic:'badge-basic', Medium:'badge-medium', Advanced:'badge-advanced' };
  return `<span class="badge ${cls[depth] || ''}">${depth}</span>`;
}

function timeAgo(iso) {
  const diff = Math.floor((Date.now() - new Date(iso + 'Z')) / 1000);
  if (diff < 60) return 'just now';
  if (diff < 3600) return Math.floor(diff/60) + 'm ago';
  if (diff < 86400) return Math.floor(diff/3600) + 'h ago';
  return Math.floor(diff/86400) + 'd ago';
}

