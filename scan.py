from datetime import datetime
import json
from . import db


class Scan(db.Model):
    """Scan history entry for a Bluetooth device."""
    __tablename__ = 'scans'

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False, index=True)
    scan_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    scan_type = db.Column(db.String(64), default='Security Assessment')
    raw_data = db.Column(db.Text, nullable=True)  # JSON raw scan attributes
    risk_score = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(32), default='Completed')

    # Relationships
    findings = db.relationship('ScanFinding', backref='scan', lazy=True, cascade='all, delete-orphan')

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'device_id': self.device_id,
            'device_name': self.device.name if self.device else 'Unknown',
            'scan_timestamp': self.scan_timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.scan_timestamp else None,
            'scan_type': self.scan_type,
            'risk_score': round(self.risk_score, 1),
            'status': self.status,
            'findings_count': len(self.findings) if self.findings else 0
        }
