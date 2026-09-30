// Dashboard Chart.js Visualizations
document.addEventListener('DOMContentLoaded', () => {
    // 1. Vulnerability Severity Doughnut Chart
    const severityCanvas = document.getElementById('severityChart');
    if (severityCanvas && window.severityChartData) {
        const ctx = severityCanvas.getContext('2d');
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: window.severityChartData.labels,
                datasets: [{
                    data: window.severityChartData.data,
                    backgroundColor: [
                        '#ef4444', // Critical
                        '#f97316', // High
                        '#f59e0b', // Medium
                        '#10b981'  // Low
                    ],
                    borderColor: '#121a2d',
                    borderWidth: 2,
                    hoverOffset: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#94a3b8',
                            font: { size: 11 },
                            padding: 14,
                            usePointStyle: true
                        }
                    },
                    tooltip: {
                        backgroundColor: '#0a0f1d',
                        titleColor: '#fff',
                        bodyColor: '#e2e8f0',
                        borderColor: '#1e2d4a',
                        borderWidth: 1,
                        padding: 10
                    }
                },
                cutout: '68%'
            }
        });
    }

    // 2. Device Risk Posture Bar Chart
    const riskCanvas = document.getElementById('deviceRiskChart');
    if (riskCanvas && window.deviceRiskChartData) {
        const ctx = riskCanvas.getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: window.deviceRiskChartData.labels,
                datasets: [{
                    label: 'Devices',
                    data: window.deviceRiskChartData.data,
                    backgroundColor: [
                        'rgba(16, 185, 129, 0.7)',
                        'rgba(245, 158, 11, 0.7)',
                        'rgba(249, 115, 22, 0.7)',
                        'rgba(239, 68, 68, 0.7)'
                    ],
                    borderColor: [
                        '#10b981',
                        '#f59e0b',
                        '#f97316',
                        '#ef4444'
                    ],
                    borderWidth: 1.5,
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { color: '#94a3b8', stepSize: 1 },
                        grid: { color: 'rgba(30, 45, 74, 0.6)' }
                    },
                    x: {
                        ticks: { color: '#94a3b8', font: { size: 10 } },
                        grid: { display: false }
                    }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: '#0a0f1d',
                        titleColor: '#fff',
                        bodyColor: '#e2e8f0',
                        borderColor: '#1e2d4a',
                        borderWidth: 1
                    }
                }
            }
        });
    }
});
