const form = document.querySelector('#query-form');
const result = document.querySelector('#result');
const button = form.querySelector('button');

const escapeHtml = (value) => String(value).replace(/[&<>'"]/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[char]));
const list = (title, items, render = escapeHtml) => items.length ? `<h3>${title}</h3><ul>${items.map(x => `<li>${render(x)}</li>`).join('')}</ul>` : '';

fetch('/api/runbooks').then(r => r.json()).then(items => {
  document.querySelector('#status').textContent = `${items.length} runbooks locaux chargés`;
}).catch(() => { document.querySelector('#status').textContent = 'API indisponible'; });

form.addEventListener('submit', async event => {
  event.preventDefault(); button.disabled = true; button.textContent = 'Analyse…';
  result.classList.remove('hidden'); result.innerHTML = '<p>Recherche dans la documentation locale…</p>';
  try {
    const response = await fetch('/api/query', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({question:document.querySelector('#question').value, engine:document.querySelector('#engine').value})});
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Erreur inconnue');
    const citations = data.citations.map(c => `<div class="citation"><strong>${escapeHtml(c.title)} · ${escapeHtml(c.section)}</strong><p>${escapeHtml(c.excerpt)}</p><small>${escapeHtml(c.source)} · score ${c.score}</small></div>`).join('');
    result.innerHTML = `<div class="meta"><span class="tag">${escapeHtml(data.engine)}</span><span class="tag">confiance ${Math.round(data.confidence*100)}%</span><span class="tag">${data.duration_ms} ms</span></div><h2>${escapeHtml(data.summary)}</h2>${list('Vérifications',data.checks)}${list('Commandes suggérées',data.commands,x=>`<code>${escapeHtml(x)}</code>`)}${list('Prudence',data.warnings)}<h3>Sources</h3>${citations || '<p>Aucune source pertinente trouvée.</p>'}`;
  } catch (error) { result.innerHTML = `<h2>Analyse impossible</h2><p>${escapeHtml(error.message)}</p>`; }
  finally { button.disabled = false; button.innerHTML = 'Analyser <span>→</span>'; }
});
