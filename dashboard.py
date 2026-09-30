from flask import Blueprint, render_template, jsonify
from models import db, Device, Scan, ScanFinding, Vulnerability
from routes.auth import login_required

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    # Statistics calculations
    total_devices = Device.query.count()
    total_scans = Scan.query.count()
    secure_devices = Device.query.filter(Device.current_risk_score <= 25.0).count()
    high_risk_devices = Device.query.filter(Device.current_risk_score > 50.0).count()
    critical_findings = ScanFinding.query.filter_by(severity='CRITICAL').count()

    # Recent scans
    recent_scans = Scan.query.order_by(Scan.scan_timestamp.desc()).limit(6).all()

    # Vulnerability severity breakdown for Chart.js
    crit_count = ScanFinding.query.filter_by(severity='CRITICAL').count()
    high_count = ScanFinding.query.filter_by(severity='HIGH').count()
    med_count = ScanFinding.query.filter_by(severity='MEDIUM').count()
    low_count = ScanFinding.query.filter_by(severity='LOW').count()

    # Device risk levels breakdown for Chart.js
    low_risk_devs = Device.query.filter(Device.current_risk_score <= 25.0).count()
    mod_risk_devs = Device.query.filter(Device.current_risk_score > 25.0, Device.current_risk_score <= 50.0).count()
    high_risk_devs = Device.query.filter(Device.current_risk_score > 50.0, Device.current_risk_score <= 75.0).count()
    crit_risk_devs = Device.query.filter(Device.current_risk_score > 75.0).count()

    # Recent discovered devices
    recent_devices = Device.query.order_by(Device.last_seen.desc()).limit(5).all()

    return render_template(
        'dashboard.html',
        total_devices=total_devices,
        total_scans=total_scans,
        secure_devices=secure_devices,
        high_risk_devices=high_risk_devices,
        critical_findings=critical_findings,
        recent_scans=recent_scans,
        recent_devices=recent_devices,
        severity_chart_data={
            'labels': ['Critical', 'High', 'Medium', 'Low'],
            'data': [crit_count, high_count, med_count, low_count]
        },
        device_risk_chart_data={
            'labels': ['Low Risk (0-25)', 'Moderate Risk (26-50)', 'High Risk (51-75)', 'Critical Risk (76-100)'],
            'data': [low_risk_devs, mod_risk_devs, high_risk_devs, crit_risk_devs]
        }
    )


@dashboard_bp.route('/api/dashboard/statistics', methods=['GET'])
@login_required
def api_statistics():
    total_devices = Device.query.count()
    total_scans = Scan.query.count()
    secure_devices = Device.query.filter(Device.current_risk_score <= 25.0).count()
    high_risk_devices = Device.query.filter(Device.current_risk_score > 50.0).count()
    critical_findings = ScanFinding.query.filter_by(severity='CRITICAL').count()

    crit_count = ScanFinding.query.filter_by(severity='CRITICAL').count()
    high_count = ScanFinding.query.filter_by(severity='HIGH').count()
    med_count = ScanFinding.query.filter_by(severity='MEDIUM').count()
    low_count = ScanFinding.query.filter_by(severity='LOW').count()

    low_risk_devs = Device.query.filter(Device.current_risk_score <= 25.0).count()
    mod_risk_devs = Device.query.filter(Device.current_risk_score > 25.0, Device.current_risk_score <= 50.0).count()
    high_risk_devs = Device.query.filter(Device.current_risk_score > 50.0, Device.current_risk_score <= 75.0).count()
    crit_risk_devs = Device.query.filter(Device.current_risk_score > 75.0).count()

    return jsonify({
        'total_devices': total_devices,
        'total_scans': total_scans,
        'secure_devices': secure_devices,
        'high_risk_devices': high_risk_devices,
        'critical_findings': critical_findings,
        'severity_distribution': {
            'CRITICAL': crit_count,
            'HIGH': high_count,
            'MEDIUM': med_count,
            'LOW': low_count
        },
        'risk_distribution': {
            'low': low_risk_devs,
            'moderate': mod_risk_devs,
            'high': high_risk_devs,
            'critical': crit_risk_devs
        }
    }), 200
