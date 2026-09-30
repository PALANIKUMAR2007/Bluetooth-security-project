from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .device import Device
from .scan import Scan
from .vulnerability import Vulnerability, ScanFinding
from .simulation import Simulation, Report


def seed_initial_data():
    """Seed standard vulnerability definitions and demo data if not present."""
    # 1. Standard Vulnerability Catalog
    standard_vulns = [
        {
            'code': 'BT-VULN-001',
            'name': 'Excessive Bluetooth Discoverability',
            'cve_id': 'CWE-200',
            'description': 'The target device is operating in continuous General Discoverable mode, broadcasting Inquiry and Advertising packets openly to arbitrary nearby scanning radios.',
            'severity': 'LOW',
            'default_score': 2.0,
            'recommendation': 'Configure device to Non-Discoverable or Limited Discoverable mode when not actively performing authorized device pairing.'
        },
        {
            'code': 'BT-VULN-002',
            'name': 'Legacy or Unauthenticated Pairing Configuration',
            'cve_id': 'CVE-2020-15802',
            'description': 'Device accepts Legacy PIN pairing (4-digit numeric code like 0000/1234) or unauthenticated Just Works association without MITM protection.',
            'severity': 'HIGH',
            'default_score': 8.0,
            'recommendation': 'Enforce Bluetooth Secure Connections (LE Secure Connections) utilizing ECDH P-256 public key cryptography and Passkey/Numeric Comparison.'
        },
        {
            'code': 'BT-VULN-003',
            'name': 'Unnecessary and Insecure Service Exposure',
            'cve_id': 'CWE-284',
            'description': 'Device advertises insecure or legacy service profiles such as OBEX File Transfer, unprotected Serial Port Profile (SPP), or unencrypted AT command channels.',
            'severity': 'HIGH',
            'default_score': 8.0,
            'recommendation': 'Disable unused SDP/GATT services. Restrict SPP and OBEX services behind mandatory encrypted channels with cryptographic authentication.'
        },
        {
            'code': 'BT-VULN-004',
            'name': 'Outdated Bluetooth Core Specification Implementation',
            'cve_id': 'CVE-2019-9506',
            'description': 'The Bluetooth firmware reports support for legacy Bluetooth 4.0/4.1 specifications susceptible to KNOB (Key Negotiation of Bluetooth) or BIAS attacks.',
            'severity': 'CRITICAL',
            'default_score': 10.0,
            'recommendation': 'Upgrade host controller firmware to Bluetooth 5.0+ with mandatory 16-byte minimum entropy encryption keys and mutual authentication.'
        },
        {
            'code': 'BT-VULN-005',
            'name': 'Unencrypted Custom GATT Service Exposure',
            'cve_id': 'CWE-319',
            'description': 'Non-standard proprietary GATT characteristics transmit raw telemetry and device commands in cleartext without link-layer or application-layer encryption.',
            'severity': 'MEDIUM',
            'default_score': 5.0,
            'recommendation': 'Enforce Insufficient Encryption error response (0x0F) on GATT read/write operations to mandate authenticated pairing before reading telemetry.'
        }
    ]

    for v_data in standard_vulns:
        if not Vulnerability.query.filter_by(code=v_data['code']).first():
            vuln = Vulnerability(**v_data)
            db.session.add(vuln)

    # 2. Default Analyst User
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='admin@cybersec.local')
        admin.set_password('Admin@12345')
        db.session.add(admin)

    # 3. Seed initial demo devices if none exist
    if Device.query.count() == 0:
        demo_devices = [
            {
                'name': 'Demo Headphones (Safe Audio)',
                'mac_address': '00:1A:7D:DA:71:01',
                'device_type': 'Audio / Headset',
                'vendor': 'AudioTech Corp',
                'rssi': -52,
                'is_demo': True,
                'services_json': '["A2DP Audio Sink", "AVRCP Remote Control", "Handsfree Profile (HFP)"]',
                'current_risk_score': 20.0,
                'status': 'Analyzed'
            },
            {
                'name': 'Demo Smartphone (Testing Target)',
                'mac_address': '00:1A:7D:DA:71:02',
                'device_type': 'Smartphone',
                'vendor': 'NexusMobile Labs',
                'rssi': -68,
                'is_demo': True,
                'services_json': '["Generic Access", "Generic Attribute", "Phonebook Access (PBAP)", "OBEX File Transfer", "Device Information Service"]',
                'current_risk_score': 65.0,
                'status': 'Analyzed'
            },
            {
                'name': 'Demo Wireless Speaker (Legacy Mode)',
                'mac_address': '00:1A:7D:DA:71:03',
                'device_type': 'Audio / Speaker',
                'vendor': 'SonicWave Inc',
                'rssi': -74,
                'is_demo': True,
                'services_json': '["A2DP Audio Sink", "AVRCP Target", "Serial Port Profile (SPP)"]',
                'current_risk_score': 82.0,
                'status': 'Analyzed'
            },
            {
                'name': 'Demo Laptop (Workstation)',
                'mac_address': '00:1A:7D:DA:71:04',
                'device_type': 'Computer / Laptop',
                'vendor': 'ThinkLab Systems',
                'rssi': -45,
                'is_demo': True,
                'services_json': '["Human Interface Device (HID)", "Personal Area Networking (PAN)", "Serial Port Profile (SPP)", "OBEX Object Push"]',
                'current_risk_score': 45.0,
                'status': 'Analyzed'
            }
        ]

        for d_data in demo_devices:
            dev = Device(**d_data)
            db.session.add(dev)
        
        db.session.commit()

        # Seed sample findings for demo devices
        dev_smart = Device.query.filter_by(mac_address='00:1A:7D:DA:71:02').first()
        dev_speaker = Device.query.filter_by(mac_address='00:1A:7D:DA:71:03').first()
        dev_laptop = Device.query.filter_by(mac_address='00:1A:7D:DA:71:04').first()

        v1 = Vulnerability.query.filter_by(code='BT-VULN-001').first()
        v2 = Vulnerability.query.filter_by(code='BT-VULN-002').first()
        v3 = Vulnerability.query.filter_by(code='BT-VULN-003').first()
        v4 = Vulnerability.query.filter_by(code='BT-VULN-004').first()

        if dev_smart and v1 and v3:
            db.session.add(ScanFinding(
                device_id=dev_smart.id,
                vulnerability_id=v1.id,
                vuln_name=v1.name,
                severity=v1.severity,
                evidence='Target continuously advertises LE General Discoverability flags (0x02) in passive beacon scan.',
                recommendation=v1.recommendation,
                finding_score=v1.default_score
            ))
            db.session.add(ScanFinding(
                device_id=dev_smart.id,
                vulnerability_id=v3.id,
                vuln_name=v3.name,
                severity=v3.severity,
                evidence='OBEX Push service (UUID 0x1105) advertised on open RFCOMM channel without authorization enforcement.',
                recommendation=v3.recommendation,
                finding_score=v3.default_score
            ))

        if dev_speaker and v2 and v4:
            db.session.add(ScanFinding(
                device_id=dev_speaker.id,
                vulnerability_id=v2.id,
                vuln_name=v2.name,
                severity=v2.severity,
                evidence='Speaker accepts unauthenticated Just Works pairing with no PIN or user verification required.',
                recommendation=v2.recommendation,
                finding_score=v2.default_score
            ))
            db.session.add(ScanFinding(
                device_id=dev_speaker.id,
                vulnerability_id=v4.id,
                vuln_name=v4.name,
                severity=v4.severity,
                evidence='Controller version indicates BT 4.1 implementation susceptible to key entropy reduction.',
                recommendation=v4.recommendation,
                finding_score=v4.default_score
            ))

        if dev_laptop and v3:
            db.session.add(ScanFinding(
                device_id=dev_laptop.id,
                vulnerability_id=v3.id,
                vuln_name=v3.name,
                severity=v3.severity,
                evidence='RFCOMM Serial Port Profile service detected in public SDP discovery records.',
                recommendation=v3.recommendation,
                finding_score=v3.default_score
            ))

    db.session.commit()


def init_db(app):
    """Initialize database tables and seed essential catalog data."""
    with app.app_context():
        try:
            db.create_all()
            seed_initial_data()
        except Exception as e:
            app.logger.error(f"Error during database initialization: {e}")

