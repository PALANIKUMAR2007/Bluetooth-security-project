import json
import datetime
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from models import db, Device, Scan, ScanFinding, Vulnerability
from routes.auth import login_required
from services.bluetooth_scanner import BluetoothScannerService
from services.security_analyzer import SecurityAnalyzerService
from services.risk_engine import RiskEngineService

bluetooth_bp = Blueprint('bluetooth', __name__)


@bluetooth_bp.route('/devices')
@login_required
def devices():
    all_devices = Device.query.order_by(Device.last_seen.desc()).all()
    avail, status_msg = BluetoothScannerService.check_bluetooth_availability()
    return render_template(
        'devices.html',
        devices=all_devices,
        adapter_available=avail,
        adapter_msg=status_msg
    )


@bluetooth_bp.route('/devices/<int:device_id>')
@login_required
def device_details(device_id):
    device = db.get_or_404(Device, device_id)
    findings = ScanFinding.query.filter_by(device_id=device.id).order_by(ScanFinding.timestamp.desc()).all()
    scans = Scan.query.filter_by(device_id=device.id).order_by(Scan.scan_timestamp.desc()).all()

    # Calculate transparent risk evaluation
    findings_dicts = [f.to_dict() for f in findings]
    risk_evaluation = RiskEngineService.calculate_device_risk(findings_dicts)

    return render_template(
        'device_details.html',
        device=device,
        findings=findings,
        scans=scans,
        risk_eval=risk_evaluation
    )


# --- REST API Endpoints ---

@bluetooth_bp.route('/api/devices', methods=['GET'])
@login_required
def api_get_devices():
    devices_list = Device.query.order_by(Device.last_seen.desc()).all()
    return jsonify({
        'status': 'success',
        'count': len(devices_list),
        'devices': [d.to_dict() for d in devices_list]
    }), 200


@bluetooth_bp.route('/api/devices/scan', methods=['POST'])
@login_required
def api_scan_devices():
    data = request.get_json() or {}
    force_demo = data.get('force_demo', True)

    scan_result = BluetoothScannerService.scan_devices(force_demo=force_demo)
    discovered_list = scan_result.get('devices', [])

    persisted_devices = []
    for d_data in discovered_list:
        mac = d_data['mac_address']
        dev = Device.query.filter_by(mac_address=mac).first()
        if not dev:
            dev = Device(
                name=d_data.get('name', 'Unknown Device'),
                mac_address=mac,
                device_type=d_data.get('device_type', 'Unknown'),
                vendor=d_data.get('vendor', 'Generic'),
                rssi=d_data.get('rssi', -65),
                is_demo=d_data.get('is_demo', False),
                status=d_data.get('status', 'Discovered')
            )
            dev.services = d_data.get('services', [])
            db.session.add(dev)
        else:
            dev.name = d_data.get('name', dev.name)
            dev.rssi = d_data.get('rssi', dev.rssi)
            dev.last_seen = datetime.datetime.utcnow()
            if d_data.get('services'):
                dev.services = d_data.get('services')

        db.session.commit()
        persisted_devices.append(dev.to_dict())

    return jsonify({
        'status': 'success',
        'mode': scan_result.get('mode'),
        'is_demo': scan_result.get('is_demo'),
        'message': scan_result.get('message'),
        'devices': persisted_devices
    }), 200


@bluetooth_bp.route('/api/devices/<int:device_id>', methods=['GET'])
@login_required
def api_get_device(device_id):
    device = db.session.get(Device, device_id)
    if not device:
        return jsonify({'error': 'Not Found', 'message': f'Device with ID {device_id} not found'}), 404

    findings = ScanFinding.query.filter_by(device_id=device.id).all()
    findings_data = [f.to_dict() for f in findings]
    risk_data = RiskEngineService.calculate_device_risk(findings_data)

    resp = device.to_dict()
    resp['findings'] = findings_data
    resp['risk_evaluation'] = risk_data
    return jsonify(resp), 200


@bluetooth_bp.route('/api/devices/<int:device_id>/security-scan', methods=['POST'])
@login_required
def api_security_scan_device(device_id):
    device = db.session.get(Device, device_id)
    if not device:
        return jsonify({'error': 'Not Found', 'message': f'Device with ID {device_id} not found'}), 404

    # 1. Execute safe vulnerability analysis
    analysis_result = SecurityAnalyzerService.analyze_device(device.to_dict())
    new_findings = analysis_result.get('findings', [])

    # 2. Record new scan record
    scan_record = Scan(
        device_id=device.id,
        scan_type='Vulnerability Audit',
        raw_data=json.dumps(analysis_result),
        status='Completed'
    )
    db.session.add(scan_record)
    db.session.flush()

    # 3. Clear old findings for this device to prevent duplicate stacking and insert new findings
    ScanFinding.query.filter_by(device_id=device.id).delete()

    created_findings = []
    for f in new_findings:
        catalog_vuln = Vulnerability.query.filter_by(code=f.get('code')).first()
        finding = ScanFinding(
            scan_id=scan_record.id,
            device_id=device.id,
            vulnerability_id=catalog_vuln.id if catalog_vuln else None,
            vuln_name=f['name'],
            severity=f['severity'],
            evidence=f['evidence'],
            recommendation=f['recommendation'],
            finding_score=f.get('finding_score', 0.0)
        )
        db.session.add(finding)
        created_findings.append(finding)

    db.session.flush()

    # 4. Calculate transparent risk score via Risk Engine
    findings_dicts = [f.to_dict() for f in created_findings]
    risk_evaluation = RiskEngineService.calculate_device_risk(findings_dicts)

    # 5. Update device score and status
    device.current_risk_score = risk_evaluation['normalized_score']
    device.status = 'Analyzed'
    scan_record.risk_score = risk_evaluation['normalized_score']
    db.session.commit()

    return jsonify({
        'status': 'success',
        'message': f"Security assessment completed for '{device.name}'. Found {len(created_findings)} security items.",
        'scan_id': scan_record.id,
        'device_id': device.id,
        'risk_score': device.current_risk_score,
        'risk_level': risk_evaluation['risk_level'],
        'formula_breakdown': risk_evaluation['formula_breakdown'],
        'findings': findings_dicts
    }), 200
