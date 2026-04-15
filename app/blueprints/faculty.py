"""
Faculty Blueprint - Phase 5
Handles Faculty Advisor review with search, pagination, and audit logging.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload
from app.models.event import Event, EventStatus
from app.utils.decorators import role_required
from app.utils.workflow import transition_status
from app.utils.search import apply_search_and_pagination
from app.utils.audit_helper import log_action

faculty_bp = Blueprint('faculty', __name__)

@faculty_bp.route('/dashboard')
@login_required
@role_required('Faculty')
def dashboard():
    """List events pending faculty approval with search and pagination."""
    # Use joinedload to prevent N+1 queries for 'creator' relationship
    query = Event.query.options(joinedload(Event.creator)).filter_by(status=EventStatus.Pending_Faculty)
    
    pagination, search_query = apply_search_and_pagination(
        query,
        Event,
        search_fields=['title', 'venue']
    )
    
    return render_template('faculty/faculty_dashboard.html', 
                           pagination=pagination, 
                           search_query=search_query)

@faculty_bp.route('/review/<int:event_id>', methods=['GET'])
@login_required
@role_required('Faculty')
def review(event_id):
    """View details and decision form for an event."""
    # Optimization: join creator
    event = Event.query.options(joinedload(Event.creator)).get_or_404(event_id)
    
    if event.status != EventStatus.Pending_Faculty:
        flash("This event is not awaiting your review.", "warning")
        return redirect(url_for('faculty.dashboard'))
    return render_template('faculty/review.html', event=event)

@faculty_bp.route('/decide/<int:event_id>', methods=['POST'])
@login_required
@role_required('Faculty')
def decide(event_id):
    """Process the approval decision with audit logging."""
    event = Event.query.get_or_404(event_id)
    decision = request.form.get('decision')
    comments = request.form.get('comments')

    success, message = transition_status(event, decision, current_user, comments)
    if success:
        # AUDIT LOG
        log_action(
            'APPROVE' if decision == 'approve' else 'REJECT' if decision == 'reject' else 'EDIT',
            'EVENT', 
            event.id, 
            f"Faculty {current_user.username} decision: {decision}. Comments: {comments}"
        )
        flash(message, "success")
    else:
        flash(message, "danger")
        return redirect(url_for('faculty.review', event_id=event.id))

    return redirect(url_for('faculty.dashboard'))
