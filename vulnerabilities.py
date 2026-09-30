from flask import Blueprint, render_template, request, jsonify
from models import db, ScanFinding, Vulnerability, Device
from routes.auth import login_required

vulnerabilities_bp = Blueprint('vulnerabilities', __name__)


@vulnerabilities_bp.route('/vulnerabilities')
@login_required
def index():
    severity_filter = request.args.get('severity', '').upper()
    query = ScanFinding.query

    if severity_filter and severity_filter in ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL'):
        query = query.filter_by(severity=severity_filter)

    findings = query.order_by(ScanFinding.timestamp.desc()).all()
    all_count = ScanFinding.query.count()
    crit_count = ScanFinding.query.filter_by(severity='CRITICAL').count()
    high_count = ScanFinding.query.filter_by(severity='HIGH').count()
    med_count = ScanFinding.query.filter_by(severity='MEDIUM').count()
    low_count = ScanFinding.query.filter_by(severity='LOW').count()

    return render_template(
        'vulnerabilities.html',
        findings=findings,
        active_filter=severity_filter or 'ALL',
        counts={
            'ALL': all_count,
            'CRITICAL': crit_count,
            'HIGH': high_count,
            'MEDIUM': med_count,
            'LOW': low_count
        }
    )


@vulnerabilities_bp.route('/api/vulnerabilities', methods=['GET'])
@login_required
def api_get_vulnerabilities():
    severity = request.args.get('severity', '').upper()
    device_id = request.args.get('device_id')

    query = ScanFinding.query
    if severity and severity in ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL'):
        query = query.filter_by(severity=severity)
    if device_id:
        query = query.filter_by(device_id=device_id)

    findings = query.order_by(ScanFinding.timestamp.desc()).all()
    return jsonify({
        'status': 'success',
        'count': len(findings),
        'findings': [f.to_dict() for f in findings]
    }), 200
