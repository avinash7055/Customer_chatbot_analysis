/**
 * SkyRocket Analytics - Frontend Application
 * Handles file uploads, API communication, and dashboard visualization
 */

// Configuration
const API_BASE_URL = 'http://localhost:5001/api';
const POLL_INTERVAL = 2000; // 2 seconds

// State
let pollInterval = null;
let currentResults = null;
let charts = {};

// ============================================
// Initialization
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    initializeUpload();
    initializeEventListeners();
    checkServerHealth();
});

// ============================================
// Server Health Check
// ============================================

async function checkServerHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            showToast('Backend server connected', 'success');
        }
    } catch (error) {
        showToast('Backend server not available. Please start the server.', 'error');
    }
}

// ============================================
// Upload Functionality
// ============================================

function initializeUpload() {
    const uploadZone = document.getElementById('uploadZone');
    const fileInput = document.getElementById('fileInput');
    const browseBtn = document.getElementById('browseBtn');

    // Click to browse
    browseBtn.addEventListener('click', () => fileInput.click());
    uploadZone.addEventListener('click', (e) => {
        if (e.target !== browseBtn) {
            fileInput.click();
        }
    });

    // File input change
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });

    // Drag and drop
    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('dragover');
    });

    uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('dragover');
    });

    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('dragover');

        if (e.dataTransfer.files.length > 0) {
            handleFileUpload(e.dataTransfer.files[0]);
        }
    });
}

async function handleFileUpload(file) {
    // Validate file
    const validExtensions = ['xlsx', 'csv'];
    const fileExtension = file.name.split('.').pop().toLowerCase();

    if (!validExtensions.includes(fileExtension)) {
        showToast('Invalid file type. Please upload .xlsx or .csv file', 'error');
        return;
    }

    if (file.size > 50 * 1024 * 1024) {
        showToast('File too large. Maximum size is 50MB', 'error');
        return;
    }

    // Show progress section
    document.getElementById('uploadZone').style.display = 'none';
    document.getElementById('progressSection').classList.remove('hidden');

    // Upload file
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${API_BASE_URL}/upload`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Upload failed');
        }

        const data = await response.json();
        showToast(`File uploaded: ${data.filename}`, 'success');

        // Start polling for progress
        startProgressPolling();

    } catch (error) {
        showToast('Upload failed. Please try again.', 'error');
        resetUploadSection();
    }
}

// ============================================
// Progress Polling
// ============================================

function startProgressPolling() {
    if (pollInterval) {
        clearInterval(pollInterval);
    }

    pollInterval = setInterval(async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/status`);
            const status = await response.json();

            updateProgress(status);

            if (status.status === 'completed') {
                clearInterval(pollInterval);
                await loadResults();
                showDashboard();
            } else if (status.status === 'error') {
                clearInterval(pollInterval);
                showToast(`Analysis failed: ${status.error}`, 'error');
                resetUploadSection();
            }
        } catch (error) {
            console.error('Polling error:', error);
        }
    }, POLL_INTERVAL);
}

function updateProgress(status) {
    const progressFill = document.getElementById('progressFill');
    const progressPercentage = document.getElementById('progressPercentage');
    const progressTitle = document.getElementById('progressTitle');
    const progressStep = document.getElementById('progressStep');

    progressFill.style.width = `${status.progress}%`;
    progressPercentage.textContent = `${status.progress}%`;
    progressStep.textContent = status.current_step;

    if (status.progress === 100) {
        progressTitle.textContent = 'Analysis Complete!';
    }
}

// ============================================
// Results Loading
// ============================================

async function loadResults() {
    try {
        const response = await fetch(`${API_BASE_URL}/results`);
        if (!response.ok) {
            throw new Error('Failed to load results');
        }

        currentResults = await response.json();
        renderDashboard(currentResults);
        showToast('Analysis complete! Dashboard loaded.', 'success');

    } catch (error) {
        showToast('Failed to load results', 'error');
        console.error('Results loading error:', error);
    }
}

// ============================================
// Dashboard Rendering
// ============================================

function renderDashboard(data) {
    // Update KPIs
    updateKPIs(data);

    // Render charts
    renderTopicChart(data.topics);
    renderQualityChart(data.evaluation);

    // Render topics table
    renderTopicsTable(data.topics);

    // Render entity insights
    renderEntityInsights(data.entities);

    // Render quality metrics
    renderQualityMetrics(data.evaluation);

    // Render key insights
    renderInsights(data);
}

function updateKPIs(data) {
    document.getElementById('totalQueries').textContent =
        formatNumber(data.data_summary.total_queries);

    if (data.evaluation) {
        document.getElementById('containmentRate').textContent =
            `${data.evaluation.containment_rate.toFixed(1)}%`;
        document.getElementById('qualityScore').textContent =
            data.evaluation.avg_overall_quality.toFixed(1);
    }

    document.getElementById('topicsCount').textContent =
        data.topics.n_topics;
}

function renderTopicChart(topicsData) {
    const ctx = document.getElementById('topicChart');

    // Destroy existing chart
    if (charts.topicChart) {
        charts.topicChart.destroy();
    }

    const topics = topicsData.topics.slice(0, 10);
    const labels = topics.map(t => t.topic_name);
    const values = topics.map(t => t.count);
    const colors = generateColors(topics.length);

    charts.topicChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: colors,
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(31, 41, 55, 0.95)',
                    titleColor: '#f3f4f6',
                    bodyColor: '#d1d5db',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: true,
                    callbacks: {
                        label: function (context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ${formatNumber(value)} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });

    // Render custom legend
    renderTopicLegend(topics, colors);
}

function renderTopicLegend(topics, colors) {
    const legendContainer = document.getElementById('topicLegend');
    legendContainer.innerHTML = topics.map((topic, index) => `
        <div style="display: flex; align-items: center; gap: 8px; font-size: 0.875rem;">
            <div style="width: 12px; height: 12px; border-radius: 3px; background: ${colors[index]};"></div>
            <span style="color: var(--gray-300);">${topic.topic_name}</span>
        </div>
    `).join('');
}

function renderQualityChart(evaluationData) {
    if (!evaluationData) return;

    const ctx = document.getElementById('qualityChart');

    // Destroy existing chart
    if (charts.qualityChart) {
        charts.qualityChart.destroy();
    }

    charts.qualityChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Accuracy', 'Empathy', 'Completeness', 'Overall Quality'],
            datasets: [{
                label: 'Quality Scores',
                data: [
                    evaluationData.avg_accuracy,
                    evaluationData.avg_empathy,
                    evaluationData.avg_completeness,
                    evaluationData.avg_overall_quality
                ],
                backgroundColor: 'rgba(14, 165, 233, 0.2)',
                borderColor: 'rgba(14, 165, 233, 1)',
                borderWidth: 2,
                pointBackgroundColor: 'rgba(14, 165, 233, 1)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgba(14, 165, 233, 1)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 5,
                    ticks: {
                        stepSize: 1,
                        color: '#9ca3af'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    pointLabels: {
                        color: '#d1d5db',
                        font: {
                            size: 12
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(31, 41, 55, 0.95)',
                    titleColor: '#f3f4f6',
                    bodyColor: '#d1d5db',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1,
                    padding: 12
                }
            }
        }
    });
}

function renderTopicsTable(topicsData) {
    const tbody = document.getElementById('topicsTableBody');

    tbody.innerHTML = topicsData.topics.map(topic => `
        <tr>
            <td><strong>#${topic.rank}</strong></td>
            <td>
                <span class="topic-badge">${topic.topic_name}</span>
            </td>
            <td style="max-width: 300px;">${topic.description}</td>
            <td><strong>${formatNumber(topic.count)}</strong></td>
            <td>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span>${topic.percentage.toFixed(1)}%</span>
                    <div class="volume-bar" style="width: 100px;">
                        <div class="volume-fill" style="width: ${topic.percentage}%;"></div>
                    </div>
                </div>
            </td>
            <td>
                <details>
                    <summary style="cursor: pointer; color: var(--primary-400);">
                        View ${topic.representative_queries.length} examples
                    </summary>
                    <ul style="margin-top: 8px; padding-left: 20px; font-size: 0.875rem; color: var(--gray-400);">
                        ${topic.representative_queries.map(q => `<li>${q}</li>`).join('')}
                    </ul>
                </details>
            </td>
        </tr>
    `).join('');

    // Add search functionality
    const searchInput = document.getElementById('topicSearch');
    searchInput.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase();
        const rows = tbody.querySelectorAll('tr');

        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(searchTerm) ? '' : 'none';
        });
    });
}

function renderEntityInsights(entitiesData) {
    const container = document.getElementById('entityList');

    if (!entitiesData || !entitiesData.entity_counts) {
        container.innerHTML = '<p style="color: var(--gray-500);">No entity data available</p>';
        return;
    }

    const entities = Object.entries(entitiesData.entity_counts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10);

    container.innerHTML = entities.map(([type, count]) => `
        <div class="entity-item">
            <span class="entity-type">${formatEntityType(type)}</span>
            <span class="entity-count">${formatNumber(count)}</span>
        </div>
    `).join('');
}

function renderQualityMetrics(evaluationData) {
    const container = document.getElementById('qualityMetrics');

    if (!evaluationData) {
        container.innerHTML = '<p style="color: var(--gray-500);">No evaluation data available</p>';
        return;
    }

    const metrics = [
        { label: 'Accuracy', value: evaluationData.avg_accuracy, max: 5, color: '#0ea5e9' },
        { label: 'Empathy', value: evaluationData.avg_empathy, max: 5, color: '#22c55e' },
        { label: 'Completeness', value: evaluationData.avg_completeness, max: 5, color: '#f59e0b' },
        { label: 'Hallucination Rate', value: evaluationData.hallucination_rate, max: 100, color: '#ef4444', suffix: '%' }
    ];

    container.innerHTML = metrics.map(metric => `
        <div class="metric-item">
            <div class="metric-label">
                <span>${metric.label}</span>
                <strong>${metric.value.toFixed(1)}${metric.suffix || ''}</strong>
            </div>
            <div class="metric-bar">
                <div class="metric-fill" style="width: ${(metric.value / metric.max) * 100}%; background: ${metric.color};"></div>
            </div>
        </div>
    `).join('');
}

function renderInsights(data) {
    const container = document.getElementById('keyInsights');
    if (!container) return;

    const insights = [];

    // Topic Insight
    if (data.topics && data.topics.topics.length > 0) {
        const topTopic = data.topics.topics[0];
        insights.push({
            type: 'info',
            text: `Most common topic is <strong>${topTopic.topic_name}</strong> (${topTopic.percentage.toFixed(1)}% of queries).`
        });
    }

    // Quality Insight
    if (data.evaluation) {
        if (data.evaluation.avg_overall_quality >= 4) {
            insights.push({
                type: 'success',
                text: `Overall quality is high (<strong>${data.evaluation.avg_overall_quality.toFixed(1)}/5.0</strong>).`
            });
        } else if (data.evaluation.avg_overall_quality < 3) {
            insights.push({
                type: 'warning',
                text: `Overall quality needs attention (<strong>${data.evaluation.avg_overall_quality.toFixed(1)}/5.0</strong>).`
            });
        }

        if (data.evaluation.hallucination_rate > 10) {
            insights.push({
                type: 'danger',
                text: `High hallucination rate detected (<strong>${data.evaluation.hallucination_rate.toFixed(1)}%</strong>).`
            });
        }
    }

    container.innerHTML = insights.map(insight => `
        <div class="insight-banner ${insight.type}">
            <div class="insight-icon">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                    <path d="M10 2C5.58 2 2 5.58 2 10C2 14.42 5.58 18 10 18C14.42 18 18 14.42 18 10C18 5.58 14.42 2 10 2ZM11 15H9V13H11V15ZM11 11H9V5H11V11Z" fill="currentColor"/>
                </svg>
            </div>
            <p>${insight.text}</p>
        </div>
    `).join('');
}

// ============================================
// Event Listeners
// ============================================

function initializeEventListeners() {
    // Download button
    document.getElementById('downloadBtn').addEventListener('click', downloadResults);

    // New analysis button
    document.getElementById('newAnalysisBtn').addEventListener('click', () => {
        resetUploadSection();
        showUploadSection();
    });
}

async function downloadResults() {
    try {
        const response = await fetch(`${API_BASE_URL}/results/download`);
        if (!response.ok) throw new Error('Download failed');

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `skyrocket-analysis-${Date.now()}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        showToast('Results downloaded successfully', 'success');
    } catch (error) {
        showToast('Download failed', 'error');
    }
}

// ============================================
// UI Helpers
// ============================================

function showDashboard() {
    document.getElementById('upload').classList.add('hidden');
    document.getElementById('dashboard').classList.remove('hidden');
}

function showUploadSection() {
    document.getElementById('upload').classList.remove('hidden');
    document.getElementById('dashboard').classList.add('hidden');
}

function resetUploadSection() {
    document.getElementById('uploadZone').style.display = '';
    document.getElementById('progressSection').classList.add('hidden');
    document.getElementById('fileInput').value = '';

    const progressFill = document.getElementById('progressFill');
    const progressPercentage = document.getElementById('progressPercentage');
    progressFill.style.width = '0%';
    progressPercentage.textContent = '0%';
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            ${getToastIcon(type)}
        </svg>
        <span>${message}</span>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideInRight 0.3s ease-out reverse';
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

function getToastIcon(type) {
    const icons = {
        success: '<path d="M10 0C4.48 0 0 4.48 0 10C0 15.52 4.48 20 10 20C15.52 20 20 15.52 20 10C20 4.48 15.52 0 10 0ZM8 15L3 10L4.41 8.59L8 12.17L15.59 4.58L17 6L8 15Z" fill="currentColor"/>',
        error: '<path d="M10 0C4.48 0 0 4.48 0 10C0 15.52 4.48 20 10 20C15.52 20 20 15.52 20 10C20 4.48 15.52 0 10 0ZM11 15H9V13H11V15ZM11 11H9V5H11V11Z" fill="currentColor"/>',
        info: '<path d="M10 0C4.48 0 0 4.48 0 10C0 15.52 4.48 20 10 20C15.52 20 20 15.52 20 10C20 4.48 15.52 0 10 0ZM11 15H9V9H11V15ZM11 7H9V5H11V7Z" fill="currentColor"/>'
    };
    return icons[type] || icons.info;
}

// ============================================
// Utility Functions
// ============================================

function formatNumber(num) {
    return new Intl.NumberFormat('en-US').format(num);
}

function formatEntityType(type) {
    return type.split('_').map(word =>
        word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
    ).join(' ');
}

function generateColors(count) {
    const baseColors = [
        '#0ea5e9', '#3b82f6', '#8b5cf6', '#ec4899', '#f43f5e',
        '#f59e0b', '#10b981', '#14b8a6', '#06b6d4', '#6366f1'
    ];

    const colors = [];
    for (let i = 0; i < count; i++) {
        colors.push(baseColors[i % baseColors.length]);
    }
    return colors;
}
