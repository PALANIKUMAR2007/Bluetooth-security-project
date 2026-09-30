import os
import sqlalchemy
from flask import Flask, render_template, jsonify
from config import Config
from models import db, init_db
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.bluetooth import bluetooth_bp
from routes.vulnerabilities import vulnerabilities_bp
from routes.simulation import simulation_bp
from routes.reports import reports_bp


def create_app(config_class=None):
    """Application factory for the Bluetooth Security Platform."""
    if config_class is None:
        config_class = Config

    app = Flask(__name__)
    app.config.from_object(config_class)

    # Verify MySQL connectivity if specified; fallback seamlessly to SQLite if offline
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if not app.config.get('TESTING') and db_uri.startswith('mysql'):
        try:
            test_engine = sqlalchemy.create_engine(db_uri, pool_pre_ping=True, connect_args={'connect_timeout': 2})
            with test_engine.connect() as conn:
                pass
            test_engine.dispose()
        except Exception as e:
            print(f"[*] Notice: MySQL connection at '{db_uri}' could not be established.")
            print(f"[*] Reason: {e}")
            print("[*] Automatically falling back to local SQLite database: sqlite:///bluetooth_security.db")
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bluetooth_security.db'
            app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {}

    # Ensure generated reports directory exists
    os.makedirs(app.config.get('REPORTS_DIR', os.path.join(app.root_path, 'generated_reports')), exist_ok=True)

    # Initialize SQLAlchemy database
    db.init_app(app)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(bluetooth_bp)
    app.register_blueprint(vulnerabilities_bp)
    app.register_blueprint(simulation_bp)
    app.register_blueprint(reports_bp)

    # Global Error Handlers
    @app.errorhandler(400)
    def bad_request_error(error):
        if app.testing or hasattr(error, 'description'):
            msg = getattr(error, 'description', 'Bad Request')
        else:
            msg = 'Bad Request'
        return jsonify({'error': 'Bad Request', 'message': msg}), 400

    @app.errorhandler(401)
    def unauthorized_error(error):
        return jsonify({'error': 'Unauthorized', 'message': 'Authentication session is invalid or expired'}), 401

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('base.html', error_title="404 - Not Found", error_message="The requested cybersecurity resource was not located."), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        db.session.rollback()
        return render_template('base.html', error_title="500 - System Error", error_message="An internal security engine error occurred. Check server logs."), 500

    # Auto-initialize database tables and seed default catalog & demo devices
    init_db(app)

    return app


app = create_app()

if __name__ == '__main__':
    print("=" * 70)
    print("  BLUETOOTH SECURITY VULNERABILITY ASSESSMENT & SIMULATOR")
    print("  Host: http://127.0.0.1:5000")
    print("  Defensive Security & Educational Simulator (SIMULATION ONLY)")
    print("=" * 70)
    app.run(host='127.0.0.1', port=5000, debug=True)
