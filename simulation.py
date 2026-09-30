import json
from flask import Blueprint, render_template, request, jsonify, session
from models import db, Device, Simulation
from routes.auth import login_required
from services.exploitation_simulator import ExploitationSimulatorService

simulation_bp = Blueprint('simulation', __name__)


@simulation_bp.route('/simulation')
@login_required
def index():
    devices = Device.query.order_by(Device.name.asc()).all()
    scenarios = ExploitationSimulatorService.get_available_scenarios()
    recent_simulations = Simulation.query.order_by(Simulation.created_at.desc()).limit(10).all()
    selected_device_id = request.args.get('device_id', type=int)

    return render_template(
        'simulation.html',
        devices=devices,
        scenarios=scenarios,
        recent_simulations=recent_simulations,
        selected_device_id=selected_device_id
    )


# --- REST API Endpoints ---

@simulation_bp.route('/api/simulation/start', methods=['POST'])
@login_required
def api_start_simulation():
    data = request.get_json() or {}
    device_id = data.get('device_id')
    scenario_id = data.get('scenario_id')

    if not device_id or not scenario_id:
        return jsonify({'error': 'Bad Request', 'message': 'device_id and scenario_id are required'}), 400

    device = db.session.get(Device, device_id)
    if not device:
        return jsonify({'error': 'Not Found', 'message': f'Device {device_id} not found'}), 404

    if scenario_id not in ExploitationSimulatorService.AVAILABLE_SCENARIOS:
        return jsonify({'error': 'Bad Request', 'message': f'Invalid scenario: {scenario_id}'}), 400

    # Run safe educational simulation
    result = ExploitationSimulatorService.run_simulation(
        scenario_id=scenario_id,
        device_name=device.name,
        mac_address=device.mac_address
    )

    # Persist simulation log in database
    sim_record = Simulation(
        device_id=device.id,
        user_id=session.get('user_id', 1),
        scenario_name=result['scenario_title'],
        status='Completed',
        timeline_json=json.dumps(result['timeline']),
        outcome_summary=result['outcome_summary']
    )
    db.session.add(sim_record)
    db.session.commit()

    response_data = result.copy()
    response_data['simulation_id'] = sim_record.id
    return jsonify(response_data), 200


@simulation_bp.route('/api/simulation/<int:sim_id>', methods=['GET'])
@login_required
def api_get_simulation(sim_id):
    sim = db.session.get(Simulation, sim_id)
    if not sim:
        return jsonify({'error': 'Not Found', 'message': f'Simulation {sim_id} not found'}), 404

    return jsonify(sim.to_dict()), 200
