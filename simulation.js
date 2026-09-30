// Educational Exploitation Simulation Interactive Controller

document.addEventListener('DOMContentLoaded', () => {
    const simForm = document.getElementById('simulationForm');
    const simRunBtn = document.getElementById('btnRunSimulation');
    const timelineContainer = document.getElementById('timelineContainer');
    const outcomeAlert = document.getElementById('outcomeAlert');

    if (simForm) {
        simForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const deviceId = document.getElementById('selectDevice').value;
            const scenarioId = document.getElementById('selectScenario').value;

            if (!deviceId || !scenarioId) {
                alert('Please select both a target device and a simulation scenario.');
                return;
            }

            if (simRunBtn) {
                simRunBtn.disabled = true;
                simRunBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Simulating Scenario...';
            }

            if (timelineContainer) {
                timelineContainer.innerHTML = `
                    <div class="text-center py-5">
                        <div class="spinner-border text-info mb-3" style="width: 3rem; height: 3rem;" role="status"></div>
                        <h6 class="text-light">Initializing Controlled Simulation Sandbox...</h6>
                        <p class="text-muted small">Targeting device in non-destructive educational mode (SIMULATION ONLY)</p>
                    </div>
                `;
            }

            if (outcomeAlert) outcomeAlert.classList.add('d-none');

            fetch('/api/simulation/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ device_id: parseInt(deviceId), scenario_id: scenarioId })
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'Completed' || data.simulation_id) {
                    renderSimulationTimeline(data);
                } else {
                    alert('Simulation error: ' + (data.message || 'Unknown response'));
                }
            })
            .catch(err => {
                console.error('Simulation failed:', err);
                alert('Simulation network error: ' + err.message);
            })
            .finally(() => {
                if (simRunBtn) {
                    simRunBtn.disabled = false;
                    simRunBtn.innerHTML = '<i class="bi bi-play-circle me-2"></i>Launch Simulation';
                }
            });
        });
    }

    function renderSimulationTimeline(simData) {
        const timeline = simData.timeline || [];
        timelineContainer.innerHTML = '';

        const timelineList = document.createElement('div');
        timelineList.className = 'sim-timeline';

        timeline.forEach((step, index) => {
            const stepEl = document.createElement('div');
            stepEl.className = 'sim-timeline-step';
            stepEl.id = `sim-step-${index}`;

            let badgeClass = 'badge bg-secondary';
            if (step.badge.includes('CRITICAL')) badgeClass = 'badge bg-danger';
            else if (step.badge.includes('VULNERABILITY') || step.badge.includes('HIGH')) badgeClass = 'badge bg-warning text-dark';
            else if (step.badge.includes('SIMULATION')) badgeClass = 'badge bg-info text-dark';
            else if (step.badge.includes('REMEDIATION')) badgeClass = 'badge bg-success';

            stepEl.innerHTML = `
                <div class="sim-node">${step.step_number}</div>
                <div class="sim-card">
                    <div class="d-flex align-items-center justify-content-between mb-2">
                        <h6 class="mb-0 text-white font-monospace">
                            <span class="text-info me-2">STEP ${step.step_number}:</span>${step.title}
                        </h6>
                        <div>
                            <span class="${badgeClass} me-2">${step.badge}</span>
                            <span class="text-muted small font-monospace">${step.timestamp}</span>
                        </div>
                    </div>
                    <div class="sim-terminal-log">
                        <i class="bi bi-terminal me-2 text-muted"></i>${step.log}
                    </div>
                </div>
            `;
            timelineList.appendChild(stepEl);
        });

        timelineContainer.appendChild(timelineList);

        // Animate progression through steps
        timeline.forEach((_, idx) => {
            setTimeout(() => {
                const el = document.getElementById(`sim-step-${idx}`);
                if (el) {
                    el.classList.add('active');
                    if (idx > 0) {
                        const prevEl = document.getElementById(`sim-step-${idx - 1}`);
                        if (prevEl) {
                            prevEl.classList.remove('active');
                            prevEl.classList.add('completed');
                        }
                    }
                }
            }, idx * 500);
        });

        // Show outcome summary after all steps animated
        setTimeout(() => {
            const lastStep = document.getElementById(`sim-step-${timeline.length - 1}`);
            if (lastStep) {
                lastStep.classList.remove('active');
                lastStep.classList.add('completed');
            }
            if (outcomeAlert) {
                outcomeAlert.classList.remove('d-none');
                outcomeAlert.innerHTML = `
                    <div class="d-flex align-items-start gap-3">
                        <i class="bi bi-shield-check fs-3 text-success"></i>
                        <div>
                            <h6 class="text-success mb-1">SIMULATION COMPLETED (SAFE ENVIRONMENT)</h6>
                            <p class="mb-0 small text-light">${simData.outcome_summary}</p>
                        </div>
                    </div>
                `;
            }
        }, timeline.length * 520);
    }
});
