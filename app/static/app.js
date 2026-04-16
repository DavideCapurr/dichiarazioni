(function () {
    'use strict';

    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');
    const resultsSection = document.getElementById('resultsSection');
    const resultsBody = document.getElementById('resultsBody');
    const notification = document.getElementById('notification');
    const modal = document.getElementById('generateModal');
    const modalClose = document.getElementById('modalClose');
    const generateForm = document.getElementById('generateForm');
    const clientIdInput = document.getElementById('clientId');
    const clientSummary = document.getElementById('clientSummary');
    const declarationDate = document.getElementById('declarationDate');
    const comuneInstallazione = document.getElementById('comuneInstallazione');
    const viaInstallazione = document.getElementById('viaInstallazione');
    const proprietarioInput = document.getElementById('proprietario');

    let searchTimer = null;

    declarationDate.value = new Date().toISOString().split('T')[0];

    function showNotification(message, type) {
        notification.textContent = message;
        notification.className = `notification ${type}`;
    }

    function hideNotification() {
        notification.className = 'notification hidden';
    }

    function escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    async function searchClients(query) {
        if (!query || query.trim().length < 1) {
            resultsSection.classList.add('hidden');
            return;
        }
        hideNotification();
        try {
            const response = await fetch(`/api/clients?q=${encodeURIComponent(query)}`);
            if (!response.ok) {
                const data = await response.json().catch(() => ({ error: 'Errore sconosciuto' }));
                showNotification(data.error || `Errore ${response.status}`, 'error');
                resultsSection.classList.add('hidden');
                return;
            }
            const data = await response.json();
            renderResults(data.clients || []);
        } catch {
            showNotification('Errore di connessione al server', 'error');
            resultsSection.classList.add('hidden');
        }
    }

    function renderResults(clients) {
        resultsBody.innerHTML = '';
        if (clients.length === 0) {
            showNotification('Nessun cliente trovato', 'info');
            resultsSection.classList.add('hidden');
            return;
        }
        for (const c of clients) {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${escapeHtml(c.name || '')}</td>
                <td>${escapeHtml(c.vat_number || '-')}</td>
                <td>${escapeHtml(c.tax_code || '-')}</td>
                <td>${escapeHtml(c.address_city || '-')}</td>
                <td><button class="btn-select">Seleziona</button></td>
            `;
            tr.querySelector('.btn-select').addEventListener('click', () => openModal(c));
            resultsBody.appendChild(tr);
        }
        resultsSection.classList.remove('hidden');
    }

    function openModal(client) {
        clientIdInput.value = client.id;

        // Riepilogo cliente
        clientSummary.innerHTML = `
            <strong>${escapeHtml(client.name)}</strong><br>
            P.IVA: ${escapeHtml(client.vat_number || '-')}&nbsp;&nbsp;
            CF: ${escapeHtml(client.tax_code || '-')}<br>
            ${escapeHtml([client.address_street, client.address_postal_code,
                          client.address_city,
                          client.address_province ? `(${client.address_province})` : '']
                         .filter(Boolean).join(' '))}
        `;

        // Pre-fill installation fields from client address
        comuneInstallazione.value = client.address_city || '';
        viaInstallazione.value = client.address_street || '';
        // proprietario = nome cliente (modificabile)
        proprietarioInput.value = client.name || '';

        modal.classList.remove('hidden');
    }

    function closeModal() {
        modal.classList.add('hidden');
    }

    async function generateDeclaration(event) {
        event.preventDefault();
        const submitBtn = generateForm.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Generazione in corso...';

        const payload = {
            client_id: parseInt(clientIdInput.value, 10),
            allegati: {},
        };

        // Text fields
        const textFields = [
            'declaration_date', 'tipo_impianto', 'descrizione_impianto',
            'comune_installazione', 'via_installazione', 'proprietario', 'uso_edificio',
        ];
        for (const f of textFields) {
            const el = generateForm.querySelector(`[name="${f}"]`);
            if (el && el.value) payload[f] = el.value;
        }

        // All 9 checkboxes
        const cbNames = [
            'dichiara_norma', 'dichiara_componenti', 'dichiara_controllo',
            'allegato_progetto', 'allegato_relazione', 'allegato_schema',
            'allegato_precedenti', 'allegato_certificato', 'allegato_conformita',
        ];
        for (const name of cbNames) {
            const el = generateForm.querySelector(`[name="${name}"]`);
            payload.allegati[name] = el ? el.checked : false;
        }

        try {
            const response = await fetch('/api/declarations/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            if (!response.ok) {
                const data = await response.json().catch(() => ({ error: 'Errore sconosciuto' }));
                showNotification(data.error || `Errore ${response.status}`, 'error');
                return;
            }
            const blob = await response.blob();
            const cd = response.headers.get('Content-Disposition') || '';
            const match = cd.match(/filename="?([^"]+)"?/);
            const filename = match ? match[1] : 'dichiarazione.pdf';

            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);

            showNotification('Dichiarazione generata con successo', 'success');
            closeModal();
        } catch {
            showNotification('Errore di connessione al server', 'error');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Genera PDF';
        }
    }

    // Events
    searchInput.addEventListener('input', () => {
        clearTimeout(searchTimer);
        searchTimer = setTimeout(() => searchClients(searchInput.value), 300);
    });
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') { clearTimeout(searchTimer); searchClients(searchInput.value); }
    });
    searchBtn.addEventListener('click', () => searchClients(searchInput.value));
    modalClose.addEventListener('click', closeModal);
    modal.addEventListener('click', (e) => { if (e.target === modal) closeModal(); });
    generateForm.addEventListener('submit', generateDeclaration);
})();
