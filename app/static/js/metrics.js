async function loadMetrics() {
    try {
        const [entries, settings, weights] = await Promise.all([
            getEntries(null, 1000),
            getSettings(),
            getWeightEntries(100)
        ]);

        updateAverageIntake(entries);
        updateTotalEntries(entries);
        updateCurrentWeek(entries, weights);
        updateCommonFoods(entries);
        updateMacros(entries);
        updateWeightSummary(weights);
        updateWeightChart(weights);
        updateWeeklyAverageWeightChart(weights, entries);
        updateWeeklyAverageCalorieChart(entries);
        await updateWeeklyChart(settings.daily_calorie_goal);
    } catch (error) {
        console.error('Failed to load metrics:', error);
    }
}

function updateAverageIntake(entries) {
    const el = document.getElementById('avg-intake');

    if (entries.length === 0) {
        el.textContent = '-';
        return;
    }

    const dailyTotals = {};
    entries.forEach(entry => {
        const date = entry.logged_at.split('T')[0];
        dailyTotals[date] = (dailyTotals[date] || 0) + entry.calories;
    });

    const days = Object.keys(dailyTotals).length;
    const totalCalories = Object.values(dailyTotals).reduce((a, b) => a + b, 0);
    const average = totalCalories / days;

    el.textContent = average.toFixed(0);
}

function updateTotalEntries(entries) {
    document.getElementById('total-entries').textContent = entries.length;
}

function updateCurrentWeek(entries, weights) {
    const weekEl = document.getElementById('current-week');
    const rangeEl = document.getElementById('current-week-range');
    const startDate = getTrackingStartDate(entries, weights);

    if (!startDate) {
        weekEl.textContent = '-';
        rangeEl.textContent = 'No tracking data yet';
        return;
    }

    const today = new Date();
    const weekNumber = getWeekNumber(startDate, today);
    const weekStart = addDays(startDate, (weekNumber - 1) * 7);
    const weekEnd = addDays(weekStart, 6);

    weekEl.textContent = `Week ${weekNumber}`;
    rangeEl.textContent = `${formatDisplayDate(weekStart)} – ${formatDisplayDate(weekEnd)}`;
}

function updateCommonFoods(entries) {
    const list = document.getElementById('common-foods');

    if (entries.length === 0) {
        list.innerHTML = '<li class="empty">No data</li>';
        return;
    }

    const counts = {};
    entries.forEach(entry => {
        const name = entry.food_name.toLowerCase();
        counts[name] = (counts[name] || 0) + 1;
    });

    const sorted = Object.entries(counts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5);

    list.innerHTML = sorted.map(([name, count]) => `
        <li>${escapeHtml(name)} <span class="food-count">(${count}x)</span></li>
    `).join('');
}

function updateMacros(entries) {
    if (entries.length === 0) return;

    let totalProtein = 0, totalCarbs = 0, totalFat = 0;
    let proteinCount = 0, carbsCount = 0, fatCount = 0;

    entries.forEach(entry => {
        if (entry.protein_g != null) {
            totalProtein += entry.protein_g;
            proteinCount++;
        }
        if (entry.carbs_g != null) {
            totalCarbs += entry.carbs_g;
            carbsCount++;
        }
        if (entry.fat_g != null) {
            totalFat += entry.fat_g;
            fatCount++;
        }
    });

    document.getElementById('avg-protein').textContent =
        proteinCount > 0 ? `${(totalProtein / proteinCount).toFixed(1)}g` : '-';
    document.getElementById('avg-carbs').textContent =
        carbsCount > 0 ? `${(totalCarbs / carbsCount).toFixed(1)}g` : '-';
    document.getElementById('avg-fat').textContent =
        fatCount > 0 ? `${(totalFat / fatCount).toFixed(1)}g` : '-';
}

function updateWeightSummary(weights) {
    const latestEl = document.getElementById('latest-weight');
    const changeEl = document.getElementById('weight-change');

    if (!weights || weights.length === 0) {
        latestEl.textContent = '-';
        changeEl.textContent = 'No weigh-ins yet';
        return;
    }

    const sorted = [...weights].sort((a, b) => new Date(a.logged_at) - new Date(b.logged_at));
    const latest = sorted[sorted.length - 1];
    latestEl.textContent = `${latest.weight_kg.toFixed(1)} kg`;

    if (sorted.length < 2) {
        changeEl.textContent = 'First weigh-in recorded';
        changeEl.className = 'weight-change neutral';
        return;
    }

    const previous = sorted[sorted.length - 2];
    const delta = latest.weight_kg - previous.weight_kg;
    const direction = delta < 0 ? 'down' : delta > 0 ? 'up' : 'flat';

    if (direction === 'flat') {
        changeEl.textContent = 'No change from previous weigh-in';
        changeEl.className = 'weight-change neutral';
    } else {
        changeEl.textContent = `${Math.abs(delta).toFixed(1)} kg ${direction} from previous`;
        changeEl.className = `weight-change ${direction === 'down' ? 'good' : 'up'}`;
    }
}

function updateWeightChart(weights) {
    const chart = document.getElementById('weight-chart');

    if (!weights || weights.length === 0) {
        chart.innerHTML = '<div class="chart-loading">No weight data yet</div>';
        return;
    }

    const sorted = [...weights]
        .sort((a, b) => new Date(a.logged_at) - new Date(b.logged_at))
        .slice(-7);

    const vals = sorted.map(w => w.weight_kg);
    const min = Math.min(...vals);
    const max = Math.max(...vals);
    const baseline = Math.floor(min) - 1;
    const ceiling = Math.ceil(max) + 1;
    const range = Math.max(ceiling - baseline, 1);

    chart.innerHTML = sorted.map(entry => {
        const normalized = ((entry.weight_kg - baseline) / range) * 100;
        const height = Math.max(Math.min(normalized, 100), 12);
        const dayLabel = new Date(entry.logged_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        return `
            <div class="chart-bar weight-bar-wrap">
                <div class="bar-value">${entry.weight_kg.toFixed(1)}</div>
                <div class="bar-track">
                    <div class="bar weight-bar" style="height: ${height}%"></div>
                </div>
                <div class="bar-label">${dayLabel}</div>
            </div>
        `;
    }).join('');
}

function updateWeeklyAverageWeightChart(weights, entries) {
    const chart = document.getElementById('weekly-weight-line-chart');
    const startDate = getTrackingStartDate(entries, weights);

    if (!startDate || !weights || weights.length === 0) {
        chart.innerHTML = '<div class="chart-loading">No weight data yet</div>';
        return;
    }

    const weekly = new Map();
    weights.forEach(entry => {
        const date = startOfDay(new Date(entry.logged_at));
        const week = getWeekNumber(startDate, date);
        if (!weekly.has(week)) {
            weekly.set(week, []);
        }
        weekly.get(week).push(entry.weight_kg);
    });

    const points = [...weekly.entries()]
        .sort((a, b) => a[0] - b[0])
        .map(([week, values]) => ({
            xLabel: `W${week}`,
            value: values.reduce((sum, v) => sum + v, 0) / values.length,
            valueLabel: `${(values.reduce((sum, v) => sum + v, 0) / values.length).toFixed(1)} kg`
        }));

    renderLineChart(chart, points, {
        lineClass: 'line-path weight-line',
        pointClass: 'line-point weight-point',
        emptyText: 'No weekly weight data yet'
    });
}

function updateWeeklyAverageCalorieChart(entries) {
    const chart = document.getElementById('weekly-calorie-line-chart');
    const startDate = getTrackingStartDate(entries, []);

    if (!startDate || !entries || entries.length === 0) {
        chart.innerHTML = '<div class="chart-loading">No calorie data yet</div>';
        return;
    }

    const dailyTotals = new Map();
    entries.forEach(entry => {
        const day = entry.logged_at.split('T')[0];
        dailyTotals.set(day, (dailyTotals.get(day) || 0) + entry.calories);
    });

    const weekly = new Map();
    [...dailyTotals.entries()].forEach(([day, total]) => {
        const date = startOfDay(new Date(day));
        const week = getWeekNumber(startDate, date);
        if (!weekly.has(week)) {
            weekly.set(week, []);
        }
        weekly.get(week).push(total);
    });

    const points = [...weekly.entries()]
        .sort((a, b) => a[0] - b[0])
        .map(([week, values]) => ({
            xLabel: `W${week}`,
            value: values.reduce((sum, v) => sum + v, 0) / values.length,
            valueLabel: `${(values.reduce((sum, v) => sum + v, 0) / values.length).toFixed(0)} kcal`
        }));

    renderLineChart(chart, points, {
        lineClass: 'line-path',
        pointClass: 'line-point',
        emptyText: 'No weekly calorie data yet'
    });
}

function renderLineChart(container, points, options = {}) {
    if (!points || points.length === 0) {
        container.innerHTML = `<div class="chart-loading">${options.emptyText || 'No data yet'}</div>`;
        return;
    }

    if (points.length === 1) {
        container.innerHTML = `
            <div class="chart-loading">Only one week of data so far: ${escapeHtml(points[0].valueLabel)}</div>
        `;
        return;
    }

    const width = 720;
    const height = 240;
    const padding = { top: 24, right: 20, bottom: 40, left: 20 };
    const innerWidth = width - padding.left - padding.right;
    const innerHeight = height - padding.top - padding.bottom;
    const values = points.map(p => p.value);
    const min = Math.min(...values);
    const max = Math.max(...values);
    const span = Math.max(max - min, 1);
    const yPad = Math.max(span * 0.2, 0.5);
    const yMin = min - yPad;
    const yMax = max + yPad;
    const yRange = Math.max(yMax - yMin, 1);

    const toX = idx => padding.left + (points.length === 1 ? innerWidth / 2 : (idx / (points.length - 1)) * innerWidth);
    const toY = value => padding.top + innerHeight - ((value - yMin) / yRange) * innerHeight;

    const polyline = points.map((point, idx) => `${toX(idx)},${toY(point.value)}`).join(' ');
    const gridLines = [0, 0.5, 1].map(f => {
        const y = padding.top + innerHeight - f * innerHeight;
        return `<line class="line-grid" x1="${padding.left}" y1="${y}" x2="${width - padding.right}" y2="${y}"></line>`;
    }).join('');

    const pointCircles = points.map((point, idx) => {
        const x = toX(idx);
        const y = toY(point.value);
        return `
            <circle class="${options.pointClass || 'line-point'}" cx="${x}" cy="${y}" r="4"></circle>
            <text class="point-label" x="${x}" y="${y - 10}" text-anchor="middle">${escapeHtml(point.valueLabel)}</text>
            <text class="axis-label" x="${x}" y="${height - 12}" text-anchor="middle">${escapeHtml(point.xLabel)}</text>
        `;
    }).join('');

    container.innerHTML = `
        <svg class="line-chart-svg" viewBox="0 0 ${width} ${height}" preserveAspectRatio="none" role="img" aria-label="Weekly trend chart">
            ${gridLines}
            <polyline class="${options.lineClass || 'line-path'}" points="${polyline}"></polyline>
            ${pointCircles}
        </svg>
    `;
}

async function updateWeeklyChart(dailyGoal) {
    const chart = document.getElementById('weekly-chart');
    const dates = getLast7Days();

    try {
        const deficits = await Promise.all(
            dates.map(date => getDeficitByDate(date).catch(() => null))
        );

        const maxCalories = Math.max(
            dailyGoal,
            ...deficits.map(d => d?.total_consumed || 0)
        );

        chart.innerHTML = dates.map((date, i) => {
            const deficit = deficits[i];
            const consumed = deficit?.total_consumed || 0;
            const heightPercent = maxCalories > 0 ? (consumed / maxCalories) * 100 : 0;
            const isOver = consumed > dailyGoal;
            const dayLabel = new Date(date).toLocaleDateString('en-US', { weekday: 'short' });

            return `
                <div class="chart-bar">
                    <div class="bar-value">${consumed.toFixed(0)}</div>
                    <div class="bar-track">
                        <div class="bar ${isOver ? 'over-goal' : ''}" style="height: ${heightPercent}%"></div>
                    </div>
                    <div class="bar-label">${dayLabel}</div>
                </div>
            `;
        }).join('');
    } catch (error) {
        chart.innerHTML = '<div class="chart-loading">Failed to load</div>';
    }
}

function getTrackingStartDate(entries = [], weights = []) {
    const dates = [];

    entries.forEach(entry => dates.push(startOfDay(new Date(entry.logged_at))));
    weights.forEach(entry => dates.push(startOfDay(new Date(entry.logged_at))));

    if (dates.length === 0) return null;

    return new Date(Math.min(...dates.map(d => d.getTime())));
}

function getWeekNumber(startDate, targetDate) {
    const start = startOfDay(startDate);
    const target = startOfDay(targetDate);
    const msPerDay = 24 * 60 * 60 * 1000;
    const diffDays = Math.max(0, Math.floor((target - start) / msPerDay));
    return Math.floor(diffDays / 7) + 1;
}

function startOfDay(date) {
    return new Date(date.getFullYear(), date.getMonth(), date.getDate());
}

function addDays(date, days) {
    const next = new Date(date);
    next.setDate(next.getDate() + days);
    return next;
}

function formatDisplayDate(date) {
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
