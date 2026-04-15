from flask import request
from flask_login import current_user
from app import db
from app.models.audit import AuditLog
from datetime import datetime, timezone

def log_action(action_type, entity_type=None, entity_id=None, details=None):
    """
    Utility function to log an action to the AuditLog table.
    """
    user_id = current_user.id if current_user.is_authenticated else None
    ip_address = request.remote_addr
    
    log = AuditLog(
        user_id=user_id,
        action_type=action_type,
        entity_type=entity_type,
        entity_id=entity_id,
        timestamp=datetime.now(timezone.utc),
        ip_address=ip_address,
        details=details
    )
    db.session.add(log)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        # In a real app, we might want to log this failure to a file
        print(f"Failed to save audit log: {e}")
