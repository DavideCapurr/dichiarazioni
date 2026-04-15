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

    let searchTimer = null;

    // Set default date to today
    declarationDate.value = new Date().toISOString().split('T')[0];

    function showNotification(message, type) {
        notification.textContent = message;
        notification.className = `notification ${type}`;
    }

    function hideNotification() {
        notification.className = 'notification hidden';
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
        } catch (err) {
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
                <td><button class="btn-select" data-id="${c.id}">Seleziona</button></td>
            `;
            tr.querySelector('.btn-select').addEventListener('click', () => openModal(c));
            resultsBody.appendChild(tr);
        }
        resultsSection.classList.remove('hidden');
    }

    function escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    function openModal(client) {
        clientIdInput.value = client.id;
        clientSummary.innerHTML = `
            <strong>${escapeHtml(client.name)}</strong><br>
            P.IVA: ${escapeHtml(client.vat_number || '-')}<br>
            CF: ${escapeHtml(client.tax_code || '-')}<br>
            ${escapeHtml(client.address_street || '')} ${escapeHtml(client.address_postal_code || '')} ${escapeHtml(client.address_city || '')} ${escapeHtml(client.address_province ? '(' + client.address_province + ')' : '')}
        `;
        modal.classList.remove('hidden');
    }

    function closeModal() {
        modal.classList.add('hidden');
        generateForm.reset();
        declarationDate.value = new Date().toISOString().split('T')[0];
    }

    async function generateDeclaration(event) {
        event.preventDefault();
        const submitBtn = generateForm.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Generazione in corso...';

        const payload = {
            client_id: parseInt(clientIdInput.value, 10),
        };
        if (declarationDate.value) payload.declaration_date = declarationDate.value;
        const num = document.getElementById('declarationNumber').value;
        if (num) payload.declaration_number = num;
        const notes = document.getElementById('notes').value;
        if (notes) payload.notes = notes;

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
            const contentDisposition = response.headers.get('Content-Disposition') || '';
            const match = contentDisposition.match(/filename="?([^"]+)"?/);
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
        } catch (err) {
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
        if (e.key === 'Enter') {
            clearTimeout(searchTimer);
            searchClients(searchInput.value);
        }
    });
    searchBtn.addEventListener('click', () => searchClients(searchInput.value));
    modalClose.addEventListener('click', closeModal);
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });
    generateForm.addEventListener('submit', generateDeclaration);
})();
