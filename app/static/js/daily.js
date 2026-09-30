async function loadDailyStatus() {
    try {
        const deficit = await getDeficitToday();
        updateGauge(deficit);
        updateStats(deficit);

        const today = formatDate(new Date());
        const entries = await getEntries(today);
        updateEntriesList(entries);
    } catch (error) {
        console.error('Failed to load daily status:', error);
        document.getElementById('gauge-label').textContent = 'Error loading data';
    }
}

function updateGauge(deficit) {
    const { daily_goal, total_consumed, remaining } = deficit;
    const percentage = Math.min((total_consumed / daily_goal) * 100, 100);

    const gaugeFill = document.getElementById('gauge-fill');
    const gaugeLabel = document.getElementById('gauge-label');

    gaugeFill.style.width = `${percentage}%`;
    gaugeFill.classList.remove('green', 'yellow', 'red');

    if (remaining < 0) {
        gaugeFill.classList.add('red');
        gaugeFill.style.width = '100%';
        gaugeLabel.textContent = `${Math.abs(remaining).toFixed(0)} kcal over`;
        gaugeLabel.style.color = '#e74c3c';
    } else if (percentage >= 80) {
        gaugeFill.classList.add('yellow');
        gaugeLabel.textContent = `${remaining.toFixed(0)} kcal left`;
        gaugeLabel.style.color = '#f39c12';
    } else {
        gaugeFill.classList.add('green');
        gaugeLabel.textContent = `${remaining.toFixed(0)} kcal left`;
        gaugeLabel.style.color = '#27ae60';
    }
}

function updateStats(deficit) {
    document.getElementById('goal-value').textContent = `${deficit.daily_goal.toFixed(0)} kcal`;
    document.getElementById('consumed-value').textContent = `${deficit.total_consumed.toFixed(0)} kcal`;

    const remainingEl = document.getElementById('remaining-value');
    if (deficit.remaining < 0) {
        remainingEl.textContent = `${Math.abs(deficit.remaining).toFixed(0)} kcal over`;
        remainingEl.style.color = '#e74c3c';
    } else {
        remainingEl.textContent = `${deficit.remaining.toFixed(0)} kcal`;
        remainingEl.style.color = '#27ae60';
    }
}

function updateEntriesList(entries) {
    const list = document.getElementById('entries-list');

    if (entries.length === 0) {
        list.innerHTML = '<li class="empty">No entries today</li>';
        return;
    }

    list.innerHTML = entries.map(entry => `
        <li>
            <span class="entry-name">${escapeHtml(entry.food_name)}</span>
            <span class="entry-calories">${entry.calories.toFixed(0)} kcal</span>
        </li>
    `).join('');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
