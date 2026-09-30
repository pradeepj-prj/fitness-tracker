const API_BASE = (() => {
    if (window.location.protocol.startsWith('http')) {
        return window.location.origin;
    }
    return 'http://localhost:8000';
})();

const PROFILE = window.CALORIE_PROFILE || 'vidhi';

function withProfile(endpoint) {
    const separator = endpoint.includes('?') ? '&' : '?';
    return `${endpoint}${separator}profile=${encodeURIComponent(PROFILE)}`;
}

async function apiGet(endpoint) {
    const response = await fetch(`${API_BASE}${withProfile(endpoint)}`);
    if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
    }
    return response.json();
}

function getDeficitToday() {
    return apiGet('/deficit/today');
}

function getDeficitByDate(date) {
    return apiGet(`/deficit/${date}`);
}

function getEntries(date = null, limit = 100) {
    let url = `/entries?limit=${limit}`;
    if (date) {
        url += `&date=${date}`;
    }
    return apiGet(url);
}

function getSettings() {
    return apiGet('/settings');
}

function getWeightEntries(limit = 100) {
    return apiGet(`/weights?limit=${limit}`);
}

function getLatestWeight() {
    return apiGet('/weights/latest');
}

function formatDate(date) {
    return date.toISOString().split('T')[0];
}

function getLast7Days() {
    const dates = [];
    for (let i = 6; i >= 0; i--) {
        const d = new Date();
        d.setDate(d.getDate() - i);
        dates.push(formatDate(d));
    }
    return dates;
}
