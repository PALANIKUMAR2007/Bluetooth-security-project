// Bluetooth Device Scanner & Security Audit Controller

function triggerBluetoothScan(forceDemo = false) {
    const scanModalEl = document.getElementById('scanModal');
    let scanModal = null;
    if (scanModalEl) {
        scanModal = new bootstrap.Modal(scanModalEl);
        scanModal.show();
    }

    const scanBtn = document.getElementById('btnStartScan');
    if (scanBtn) {
        scanBtn.disabled = true;
        scanBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Scanning Airwaves...';
    }

    fetch('/api/devices/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ force_demo: forceDemo })
    })
    .then(res => res.json())
    .then(data => {
        setTimeout(() => {
            if (scanModal) {
                scanModal.hide();
            }
            if (data.status === 'success') {
                window.location.reload();
            } else {
                alert('Scan alert: ' + (data.message || 'Unknown status'));
                window.location.reload();
            }
        }, 1200);
    })
    .catch(err => {
        console.error('Scan failed:', err);
        alert('Discovery error: ' + err.message);
        if (scanModal) scanModal.hide();
        if (scanBtn) {
            scanBtn.disabled = false;
            scanBtn.innerHTML = '<i class="bi bi-broadcast me-2"></i>Scan Devices';
        }
    });
}

function runDeviceSecurityScan(deviceId) {
    const auditBtn = document.getElementById(`audit-btn-${deviceId}`);
    if (auditBtn) {
        auditBtn.disabled = true;
        auditBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Auditing...';
    }

    fetch(`/api/devices/${deviceId}/security-scan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {
            window.location.href = `/devices/${deviceId}`;
        } else {
            alert('Security Audit error: ' + (data.message || 'Unknown failure'));
            if (auditBtn) {
                auditBtn.disabled = false;
                auditBtn.innerHTML = '<i class="bi bi-shield-check me-1"></i> Security Scan';
            }
        }
    })
    .catch(err => {
        console.error('Security scan error:', err);
        alert('Security Audit network error: ' + err.message);
        if (auditBtn) {
            auditBtn.disabled = false;
            auditBtn.innerHTML = '<i class="bi bi-shield-check me-1"></i> Security Scan';
        }
    });
}
