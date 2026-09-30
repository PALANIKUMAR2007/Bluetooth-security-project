from datetime import datetime
import json
from . import db


class Device(db.Model):
    """Bluetooth device model storing discovered and analyzed targets."""
    __tablename__ = 'devices'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, default='Unknown Device')
    mac_address = db.Column(db.String(32), unique=True, nullable=False, index=True)
    device_type = db.Column(db.String(64), default='Unknown')
    vendor = db.Column(db.String(128), default='Generic')
    rssi = db.Column(db.Integer, default=-65)
    is_demo = db.Column(db.Boolean, default=False)
    services_json = db.Column(db.Text, nullable=True)  # Stored as JSON array
    first_seen = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    current_risk_score = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(32), default='Discovered')  # Discovered, Scanned, Analyzed

    # Relationships
    scans = db.relationship('Scan', backref='device', lazy=True, cascade='all, delete-orphan')
    findings = db.relationship('ScanFinding', backref='device', lazy=True, cascade='all, delete-orphan')
    simulations = db.relationship('Simulation', backref='device', lazy=True, cascade='all, delete-orphan')
    reports = db.relationship('Report', backref='device', lazy=True, cascade='all, delete-orphan')

    @property
    def services(self) -> list:
        if self.services_json:
            try:
                return json.loads(self.services_json)
            except Exception:
                return []
        return []

    @services.setter
    def services(self, value: list):
        self.services_json = json.dumps(value)

    @property
    def risk_level(self) -> str:
        score = self.current_risk_score or 0.0
        if score <= 25.0:
            return 'Low Risk'
        elif score <= 50.0:
            return 'Moderate Risk'
        elif score <= 75.0:
            return 'High Risk'
        else:
            return 'Critical Risk'

    @property
    def risk_badge_class(self) -> str:
        score = self.current_risk_score or 0.0
        if score <= 25.0:
            return 'bg-success'
        elif score <= 50.0:
            return 'bg-warning text-dark'
        elif score <= 75.0:
            return 'bg-orange text-white'
        else:
            return 'bg-danger'

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'mac_address': self.mac_address,
            'device_type': self.device_type,
            'vendor': self.vendor,
            'rssi': self.rssi,
            'is_demo': self.is_demo,
            'services': self.services,
            'first_seen': self.first_seen.strftime('%Y-%m-%d %H:%M:%S') if self.first_seen else None,
            'last_seen': self.last_seen.strftime('%Y-%m-%d %H:%M:%S') if self.last_seen else None,
            'current_risk_score': round(self.current_risk_score, 1),
            'risk_level': self.risk_level,
            'status': self.status
        }
