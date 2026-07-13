/* Global UI behaviour: sidebar toggle, auto-submitting filters,
   cascading dropdown helper and small chart utilities. */
document.addEventListener('DOMContentLoaded', () => {
  // Sidebar toggle (desktop collapse + mobile off-canvas)
  const sidebar = document.getElementById('sidebar');
  const toggle = document.getElementById('sidebarToggle');
  if (sidebar && toggle) {
    toggle.addEventListener('click', () => {
      if (window.innerWidth < 992) {
        sidebar.classList.toggle('show-mobile');
      } else {
        sidebar.classList.toggle('collapsed');
      }
    });
    document.addEventListener('click', (e) => {
      if (window.innerWidth < 992 && sidebar.classList.contains('show-mobile')
          && !sidebar.contains(e.target) && !toggle.contains(e.target)) {
        sidebar.classList.remove('show-mobile');
      }
    });
  }

  // Auto-submit filter selects marked with data-autosubmit
  document.querySelectorAll('select[data-autosubmit]').forEach((el) => {
    el.addEventListener('change', () => el.closest('form')?.submit());
  });

  // Auto-dismiss flash alerts
  document.querySelectorAll('.alert-dismissible').forEach((el) => {
    setTimeout(() => bootstrap.Alert.getOrCreateInstance(el)?.close(), 6000);
  });
});

/* ------------------------------------------------------------------
   Chart helpers (Chart.js)
   ------------------------------------------------------------------ */
const CHART_COLORS = {
  blue: '#1d4ed8', lightBlue: '#60a5fa', green: '#16a34a',
  red: '#dc2626', amber: '#d97706', slate: '#64748b', sky: '#0284c7',
};

async function fetchJSON(url) {
  const res = await fetch(url, { headers: { Accept: 'application/json' } });
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return res.json();
}

function lineChart(canvasId, labels, data, label) {
  const el = document.getElementById(canvasId);
  if (!el) return null;
  return new Chart(el, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label,
        data,
        borderColor: CHART_COLORS.blue,
        backgroundColor: 'rgba(29, 78, 216, 0.12)',
        fill: true,
        tension: 0.35,
        pointRadius: 3,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: { y: { beginAtZero: true, max: 100, ticks: { callback: (v) => v + '%' } } },
      plugins: { legend: { display: false } },
    },
  });
}

function barChart(canvasId, labels, data, label, color = CHART_COLORS.blue, horizontal = false) {
  const el = document.getElementById(canvasId);
  if (!el) return null;
  return new Chart(el, {
    type: 'bar',
    data: {
      labels,
      datasets: [{ label, data, backgroundColor: color, borderRadius: 5, maxBarThickness: 34 }],
    },
    options: {
      indexAxis: horizontal ? 'y' : 'x',
      responsive: true,
      maintainAspectRatio: false,
      scales: horizontal
        ? { x: { beginAtZero: true } }
        : { y: { beginAtZero: true, max: 100, ticks: { callback: (v) => v + '%' } } },
      plugins: { legend: { display: false } },
    },
  });
}

function doughnutChart(canvasId, labels, data, colors) {
  const el = document.getElementById(canvasId);
  if (!el) return null;
  return new Chart(el, {
    type: 'doughnut',
    data: { labels, datasets: [{ data, backgroundColor: colors, borderWidth: 2 }] },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '62%',
      plugins: { legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11 } } } },
    },
  });
}

/* Attendance page helpers */
function markAll(status) {
  document.querySelectorAll(`input[type="radio"][value="${status}"]`).forEach((r) => {
    r.checked = true;
  });
}

function resetMarks() {
  document.querySelectorAll('input[type="radio"][value="Present"]').forEach((r) => {
    r.checked = true;
  });
  document.querySelectorAll('input[name^="remarks_"]').forEach((i) => { i.value = ''; });
}
