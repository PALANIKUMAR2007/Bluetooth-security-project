import os
from flask import Blueprint, render_template, request, jsonify, send_file, current_app, session, flash, redirect, url_for
from models import db, Report, Device, ScanFinding, Simulation, Scan
from routes.auth import login_required
from services.risk_engine import RiskEngineService
from services.report_generator import ReportGeneratorService

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/reports')
@login_required
def index():
    reports_list = Report.query.order_by(Report.generated_at.desc()).all()
    devices = Device.query.order_by(Device.name.asc()).all()
    return render_template('reports.html', reports=reports_list, devices=devices)


@reports_bp.route('/reports/download/<int:report_id>')
@login_required
def download_report(report_id):
    report = db.get_or_404(Report, report_id)
    if not os.path.exists(report.file_path):
        flash('Report file was not found on server disk.', 'danger')
        return redirect(url_for('reports.index'))

    return send_file(
        report.file_path,
        as_attachment=True,
        download_name=os.path.basename(report.file_path),
        mimetype='application/pdf'
    )


@reports_bp.route('/reports/view/<int:report_id>')
@login_required
def view_report(report_id):
    report = db.get_or_404(Report, report_id)
    if not os.path.exists(report.file_path):
        flash('Report file was not found on server disk.', 'danger')
        return redirect(url_for('reports.index'))

    return send_file(
        report.file_path,
        as_attachment=False,
        mimetype='application/pdf'
    )


# --- REST API Endpoints ---

@reports_bp.route('/api/reports/generate', methods=['POST'])
@login_required
def api_generate_report():
    data = request.get_json() or {}
    device_id = data.get('device_id')

    if not device_id:
        return jsonify({'error': 'Bad Request', 'message': 'device_id is required'}), 400

    device = db.session.get(Device, device_id)
    if not device:
        return jsonify({'error': 'Not Found', 'message': f'Device {device_id} not found'}), 404

    # Fetch device findings and simulations
    findings = ScanFinding.query.filter_by(device_id=device.id).all()
    findings_dicts = [f.to_dict() for f in findings]
    risk_data = RiskEngineService.calculate_device_risk(findings_dicts)

    sims = Simulation.query.filter_by(device_id=device.id).order_by(Simulation.created_at.desc()).limit(5).all()
    sims_dicts = [s.to_dict() for s in sims]

    # Target folder
    reports_dir = current_app.config.get('REPORTS_DIR', os.path.join(os.getcwd(), 'generated_reports'))
    analyst_name = session.get('username', 'Authorized Security Analyst')

    try:
        pdf_meta = ReportGeneratorService.generate_pdf_report(
            output_dir=reports_dir,
            device_dict=device.to_dict(),
            risk_data=risk_data,
            findings=findings_dicts,
            simulations=sims_dicts,
            analyst_name=analyst_name
        )

        # Persist report entity
        report_record = Report(
            report_uid=pdf_meta['report_uid'],
            device_id=device.id,
            user_id=session.get('user_id', 1),
            title=f"Security Assessment: {device.name}",
            file_path=pdf_meta['filepath'],
            risk_score=pdf_meta['risk_score']
        )
        db.session.add(report_record)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'PDF Report generated successfully',
            'report_id': report_record.id,
            'report_uid': report_record.report_uid,
            'filename': pdf_meta['filename'],
            'download_url': f"/reports/download/{report_record.id}",
            'view_url': f"/reports/view/{report_record.id}"
        }), 201

    except Exception as e:
        return jsonify({
            'error': 'Generation Error',
            'message': f'Failed to generate PDF report: {str(e)}'
        }), 500
