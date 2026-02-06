const API_BASE = '/api';

export async function analyzeStyle(files) {
  const formData = new FormData();
  for (const file of files) {
    formData.append('images', file);
  }

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

export async function findMatches({ limit = 25, min_score = 6 } = {}) {
  const res = await fetch(`${API_BASE}/find-matches`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ limit, min_score }),
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.error || 'Failed to find matches');
  }

  return res.json();
}
