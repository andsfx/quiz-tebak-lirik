/* auth.js — simple role-based auth for team review */
const AUTH_USERS = {
  admin: { password: "admin123", role: "admin", label: "Admin" },
  demo:  { password: "demo123",  role: "demo",  label: "Demo" },
};
const AUTH_TTL = 7 * 24 * 60 * 60 * 1000; // 7 days
const AUTH_KEY = "quizTebakLirik_auth_v1";

function authToken() {
  try {
    const raw = localStorage.getItem(AUTH_KEY);
    if (!raw) return null;
    const t = JSON.parse(raw);
    if (Date.now() > t.expires) { localStorage.removeItem(AUTH_KEY); return null; }
    return t;
  } catch (_) { return null; }
}

function authRole() {
  const t = authToken();
  return t ? t.role : null;
}

function authLabel() {
  const t = authToken();
  return t ? t.label || t.role : null;
}

function authLogin(role, password) {
  const u = AUTH_USERS[role];
  if (!u || u.password !== password) return false;
  const t = { role: u.role, label: u.label, loginAt: Date.now(), expires: Date.now() + AUTH_TTL };
  localStorage.setItem(AUTH_KEY, JSON.stringify(t));
  return true;
}

function authLogout() {
  localStorage.removeItem(AUTH_KEY);
  location.reload();
}

function authRequire() {
  const t = authToken();
  if (!t) { document.getElementById('auth-overlay').style.display = 'flex'; document.getElementById('app').style.display = 'none'; return null; }
  document.getElementById('auth-overlay').style.display = 'none';
  document.getElementById('app').style.display = '';
  // Show role badge
  const el = document.getElementById('role-badge');
  if (el) { el.textContent = t.label || t.role; el.style.display = 'inline'; }
  return t.role;
}

function authGateAdmin() {
  const t = authToken();
  if (!t || t.role !== 'admin') { window.location.href = 'index.html?auth=gate'; return null; }
  const el = document.getElementById('role-badge');
  if (el) { el.textContent = t.label || t.role; el.style.display = 'inline'; }
  return t.role;
}

function authDemoGate() {
  const t = authToken();
  if (!t) return false;
  if (t.role === 'demo') { alert('Fitur ini hanya untuk Admin'); return false; }
  return true;
}
