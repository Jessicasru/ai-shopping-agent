const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:5001/api';

export async function analyzeStyle(files, email) {
  const formData = new FormData();
  for (const file of files) {
    formData.append('images', file);
  }
  if (email) formData.append('email', email);

  const res = await fetch(`${API_BASE}/analyze-style`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.error || 'Failed to analyze style');
  }

  return res.json();
}

export async function getProfile() {
  const res = await fetch(`${API_BASE}/profile`);
  if (!res.ok) return null;
  return res.json();
}

export async function getProducts() {
  const res = await fetch(`${API_BASE}/products`);
  if (!res.ok) return null;
  return res.json();
}

export async function getRecommendations() {
  const res = await fetch(`${API_BASE}/recommendations`);
  if (!res.ok) return null;
  return res.json();
}

export async function findMatches({ limit = 25, min_score = 6, email } = {}) {
  const body = { limit, min_score };
  if (email) body.email = email;

  const res = await fetch(`${API_BASE}/find-matches`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.error || 'Failed to find matches');
  }

  return res.json();
}

export async function getUserByEmail(email) {
  const res = await fetch(`${API_BASE}/user/${encodeURIComponent(email)}`);
  if (!res.ok) return null;
  return res.json();
}
