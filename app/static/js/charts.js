/**
 * Chart.js initialization and API calls for VitalSync.
 * Fetches data from /api/charts/<metric> and renders line charts.
 */

function loadChart(metric, canvasId, label, borderColor, bgColor, userId) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    let url = `/api/charts/${metric}`;
    if (userId) {
        url += `?user_id=${userId}`;
    }

    fetch(url)
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                console.error('Chart error:', data.error);
                return;
            }

            const ctx = canvas.getContext('2d');

            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: label,
                        data: data.data,
                        borderColor: borderColor,
                        backgroundColor: bgColor,
                        borderWidth: 2.5,
                        pointBackgroundColor: borderColor,
                        pointBorderColor: 'rgba(10, 14, 26, 0.8)',
                        pointBorderWidth: 2,
                        pointRadius: 5,
                        pointHoverRadius: 7,
                        fill: true,
                        tension: 0.4,
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    interaction: {
                        mode: 'index',
                        intersect: false,
                    },
                    plugins: {
                        legend: {
                            display: false,
                        },
                        tooltip: {
                            backgroundColor: 'rgba(17, 24, 39, 0.95)',
                            titleColor: '#e2e8f0',
                            bodyColor: '#94a3b8',
                            borderColor: 'rgba(255, 255, 255, 0.1)',
                            borderWidth: 1,
                            padding: 12,
                            cornerRadius: 10,
                            displayColors: false,
                            titleFont: {
                                family: 'Inter',
                                weight: 600,
                            },
                            bodyFont: {
                                family: 'Inter',
                            },
                        }
                    },
                    scales: {
                        x: {
                            grid: {
                                color: 'rgba(255, 255, 255, 0.04)',
                                drawBorder: false,
                            },
                            ticks: {
                                color: '#64748b',
                                font: {
                                    family: 'Inter',
                                    size: 11,
                                },
                            },
                        },
                        y: {
                            grid: {
                                color: 'rgba(255, 255, 255, 0.04)',
                                drawBorder: false,
                            },
                            ticks: {
                                color: '#64748b',
                                font: {
                                    family: 'Inter',
                                    size: 11,
                                },
                            },
                            beginAtZero: true,
                        }
                    },
                    animation: {
                        duration: 800,
                        easing: 'easeOutQuart',
                    },
                }
            });
        })
        .catch(err => {
            console.error('Failed to load chart:', err);
        });
}
