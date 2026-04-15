"""
Admin Blueprint - Phase 5
Handles administrative tasks, system-wide overview, and audit logging.
"""
from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload
from sqlalchemy import func
from app.utils.decorators import role_required
from app.models.user import User
# Import models inside functions if needed to avoid circular imports, 
# but here they are used at top level for type hinting if any
from app.models.event import Event, EventStatus
from app.models.approval import Approval
from app.models.audit import AuditLog
from app.utils.search import apply_search_and_pagination

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
@role_required('Admin')
def dashboard():
    """System-wide overview for Administrators with aggregated stats."""
    
    user_count = User.query.count()
    event_count = Event.query.count()
    
    # Aggregated stats
    pending_count = Event.query.filter(Event.status.in_([EventStatus.Pending_Faculty, EventStatus.Pending_Head])).count()
    approved_count = Event.query.filter(Event.status == EventStatus.Approved).count()
    
    # Total Budget (Aggregated)
    from app import db
    total_budget = db.session.query(func.sum(Event.budget)).scalar() or 0
    
    # Recent Events with Joined Loads (Optimization)
    recent_events = Event.query.options(joinedload(Event.creator)).order_by(Event.created_at.desc()).limit(10).all()
    
    # Recent Audit Logs
    recent_logs = AuditLog.query.options(joinedload(AuditLog.user)).order_by(AuditLog.timestamp.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html', 
                           user_count=user_count, 
                           event_count=event_count,
                           pending_count=pending_count,
                           approved_count=approved_count,
                           total_budget=total_budget,
                           recent_events=recent_events,
                           recent_logs=recent_logs)

@admin_bp.route('/audit-logs')
@login_required
@role_required('Admin')
def audit_logs():
    """Viewable only by Admins. Display filterable table of all actions."""
    query = AuditLog.query.options(joinedload(AuditLog.user))
    
    # Apply search and pagination
    # Search fields: details, action_type, entity_type
    pagination, search_query = apply_search_and_pagination(
        query, 
        AuditLog, 
        search_fields=['details', 'action_type', 'entity_type'],
        filter_params={'action_type': request.args.get('action_type')}
    )
    
    return render_template('admin/audit_logs.html', 
                           pagination=pagination, 
                           search_query=search_query)

@admin_bp.route('/users')
@login_required
@role_required('Admin')
def list_users():
    """List all users with search and pagination."""
    query = User.query
    pagination, search_query = apply_search_and_pagination(
        query,
        User,
        search_fields=['username', 'email', 'department']
    )
    return render_template('admin/manage_users.html', pagination=pagination, search_query=search_query)

@admin_bp.route('/manage-users')
@login_required
@role_required('Admin')
def manage_users():
    return list_users()

@admin_bp.route('/all-reports')
@login_required
@role_required('Admin')
def all_events():
    """View all events in the system."""
    query = Event.query.options(joinedload(Event.creator))
    pagination, search_query = apply_search_and_pagination(
        query, Event, search_fields=['title', 'venue']
    )
    return render_template('admin/all_events.html', 
                           pagination=pagination, 
                           search_query=search_query)

@admin_bp.route('/workflow-analytics')
@login_required
@role_required('Admin')
def workflow_analytics():
    return render_template('admin/workflow_analytics.html')

@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
@role_required('Admin')
def delete_user(user_id):
    """Delete a user from the system."""
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You cannot delete yourself.", "danger")
    else:
        username = user.username
        from app import db
        db.session.delete(user)
        db.session.commit()
        log_action('DELETE', 'USER', user_id, f"Deleted user: {username}")
        flash(f"User {username} deleted successfully.", "success")
    return redirect(url_for('admin.list_users'))

@admin_bp.route('/users/toggle-status/<int:user_id>', methods=['POST'])
@login_required
@role_required('Admin')
def toggle_user_status(user_id):
    """Toggle user active status."""
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You cannot deactivate yourself.", "warning")
    else:
        user.is_active = not user.is_active
        from app import db
        db.session.commit()
        log_action('UPDATE', 'USER', user_id, f"Toggled status to: {user.is_active}")
        flash(f"User {user.username} status updated.", "info")
    return redirect(url_for('admin.list_users'))

@admin_bp.route('/export/events')
@login_required
@role_required('Admin')
def export_reports():
    """Export all events as CSV."""
    import csv
    from io import StringIO
    from flask import Response
    
    events = Event.query.all()
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID', 'Title', 'Creator', 'Status', 'Date', 'Budget'])
    
    for event in events:
        cw.writerow([
            event.reference_id, 
            event.title, 
            event.creator.username if event.creator else 'Unknown',
            event.status.value,
            event.event_date.strftime('%Y-%m-%d'),
            event.budget
        ])
    
    output = si.getvalue()
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=event_reports.csv"}
    )

from app import db # Import at bottom or inside to ensure db is available

@admin_bp.route('/system-settings')
@login_required
@role_required('Admin')
def system_settings():
    """Placeholder for system settings."""
    return render_template('admin/placeholder.html', title="System Settings")
