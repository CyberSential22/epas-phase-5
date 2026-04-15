"""
Events Blueprint - Phase 5
Handles event creation, submission, and confirmation with search and audit logging.
"""
from flask import (
    Blueprint, render_template, redirect,
    url_for, flash, current_app, request
)
from app import db
from app.models.event import Event, EventStatus
from app.forms.event_form import EventSubmissionForm
from flask_login import login_required, current_user
from app.utils.decorators import role_required
from app.utils.search import apply_search_and_pagination
from app.utils.audit_helper import log_action
from sqlalchemy.orm import joinedload
from datetime import datetime

events_bp = Blueprint('events', __name__)

@events_bp.route('/dashboard')
@login_required
@role_required('Student')
def student_dashboard():
    """List events created by the current student with search and pagination."""
    query = Event.query.filter_by(created_by=current_user.id)
    
    # Stats
    total_count = Event.query.filter_by(created_by=current_user.id).count()
    pending_count = Event.query.filter_by(created_by=current_user.id).filter(Event.status.in_([EventStatus.Pending_Faculty, EventStatus.Pending_Head])).count()
    approved_count = Event.query.filter_by(created_by=current_user.id).filter_by(status=EventStatus.Approved).count()
    
    pagination, search_query = apply_search_and_pagination(
        query,
        Event,
        search_fields=['title', 'description', 'venue'],
        filter_params={'status': request.args.get('status')}
    )
    
    # Calculate percentages for UI
    pending_percent = (pending_count / total_count * 100) if total_count > 0 else 0
    approved_percent = (approved_count / total_count * 100) if total_count > 0 else 0
    
    return render_template('student/student_dashboard.html', 
                           role='Student', 
                           pagination=pagination, 
                           search_query=search_query,
                           total_count=total_count,
                           pending_count=pending_count,
                           approved_count=approved_count,
                           pending_percent=pending_percent,
                           approved_percent=approved_percent,
                           event_statuses=list(EventStatus))


@events_bp.route('/create', methods=['GET'])
@login_required
@role_required('Student')
def create_event():
    """GET /events/create — Render the empty event submission form."""
    form = EventSubmissionForm()
    return render_template('student/create_report.html', form=form)


@events_bp.route('/submit', methods=['POST'])
@login_required
@role_required('Student')
def submit_event():
    """POST /events/submit — Validate and persist a new event with audit logging."""
    form = EventSubmissionForm()

    if form.validate_on_submit():
        try:
            event = Event(
                # Basic Info
                title=form.title.data.strip(),
                description=form.description.data.strip(),
                event_type=form.event_type.data,
                venue=form.venue.data.strip(),
                event_date=form.event_date.data,
                start_time=datetime.combine(form.event_date.data, form.start_time.data),
                end_time=datetime.combine(form.event_date.data, form.end_time.data),
                # Audience
                audience_type=form.audience_type.data,
                audience_size=form.audience_size.data,
                is_external_audience=form.is_external_audience.data,
                # Technical
                requires_projector=form.requires_projector.data,
                requires_microphone=form.requires_microphone.data,
                requires_live_streaming=form.requires_live_streaming.data,
                technical_requirements=(
                    form.technical_requirements.data.strip()
                    if form.technical_requirements.data else None
                ),
                # Security
                requires_security=form.requires_security.data,
                security_requirements=(
                    form.security_requirements.data.strip()
                    if form.security_requirements.data else None
                ),
                # Budget
                budget=form.budget.data,
                budget_breakdown=(
                    form.budget_breakdown.data.strip()
                    if form.budget_breakdown.data else None
                ),
                # Status & Ownership
                status=EventStatus.Pending_Faculty,
                created_by=current_user.id
            )

            db.session.add(event)
            db.session.commit()

            # AUDIT LOG
            log_action('CREATE', 'EVENT', event.id, f"Created event: {event.title}")

            flash(f'Event "{event.title}" submitted successfully! Ref: {event.reference_id}', 'success')
            return redirect(url_for('events.confirmation', event_id=event.id))

        except Exception as exc:
            db.session.rollback()
            current_app.logger.error('Database error: %s', str(exc))
            flash('An error occurred. Please try again.', 'danger')

    return render_template('student/create_report.html', form=form)


@events_bp.route('/confirmation/<int:event_id>')
def confirmation(event_id):
    """GET /events/confirmation/<id> — Show submission success details."""
    event = Event.query.get_or_404(event_id)
    return render_template('events/confirmation.html', event=event)

@events_bp.route('/edit/<int:event_id>', methods=['GET'])
@login_required
@role_required('Student')
def edit_event(event_id):
    """GET /events/edit/<id> — Render the form to edit an event."""
    event = Event.query.get_or_404(event_id)
    
    if event.created_by != current_user.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for('events.student_dashboard'))
    
    if event.status not in [EventStatus.Draft, EventStatus.Changes_Requested]:
        flash(f"Cannot edit event in status: {event.status.value}", "warning")
        return redirect(url_for('events.student_dashboard'))
    
    form = EventSubmissionForm(obj=event)
    return render_template('events/edit.html', form=form, event=event)

@events_bp.route('/update/<int:event_id>', methods=['POST'])
@login_required
@role_required('Student')
def update_event(event_id):
    """POST /events/update/<id> — Update an existing event with audit logging."""
    event = Event.query.get_or_404(event_id)
    
    if event.created_by != current_user.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for('events.student_dashboard'))
    
    form = EventSubmissionForm()
    if form.validate_on_submit():
        try:
            form.populate_obj(event)
            # Reset status to Pending Faculty on update
            event.status = EventStatus.Pending_Faculty
            
            db.session.commit()
            
            # AUDIT LOG
            log_action('EDIT', 'EVENT', event.id, f"Updated event: {event.title}")
            
            flash("Event updated and resubmitted.", "success")
            return redirect(url_for('events.confirmation', event_id=event.id))
        except Exception as e:
            db.session.rollback()
            flash(f"Update failed: {str(e)}", "danger")
    
    return render_template('events/edit.html', form=form, event=event)

@events_bp.route('/my-events')
@login_required
@role_required('Student')
def my_events():
    """Alias for student_dashboard."""
    return student_dashboard()

@events_bp.route('/new')
@login_required
@role_required('Student')
def create():
    """Alias for create_event."""
    return create_event()

@events_bp.route('/track-status/<int:event_id>')
@login_required
@role_required('Student')
def track_status(event_id):
    """View status of a specific event with progress focus."""
    event = Event.query.get_or_404(event_id)
    if event.created_by != current_user.id and current_user.role != 'Admin':
        flash("Unauthorized.", "danger")
        return redirect(url_for('events.student_dashboard'))
    
    return render_template('student/track_status.html', event=event)

@events_bp.route('/delete/<int:event_id>', methods=['POST'])
@login_required
def delete_event(event_id):
    """Delete a draft or rejected event."""
    event = Event.query.get_or_404(event_id)
    
    # Permission check
    if event.created_by != current_user.id and current_user.role != 'Admin':
        flash("Unauthorized.", "danger")
        return redirect(url_for('events.student_dashboard'))
    
    # Status check
    if event.status not in [EventStatus.Draft, EventStatus.Rejected]:
        flash("Only drafts or rejected events can be deleted.", "warning")
        return redirect(url_for('events.student_dashboard'))
    
    title = event.title
    db.session.delete(event)
    db.session.commit()
    
    log_action('DELETE', 'EVENT', event_id, f"Deleted event: {title}")
    flash(f"Event '{title}' deleted.", "success")
    return redirect(url_for('events.student_dashboard'))

@events_bp.route('/withdraw/<int:event_id>', methods=['POST'])
@login_required
def withdraw_event(event_id):
    """Withdraw a pending event back to draft."""
    event = Event.query.get_or_404(event_id)
    
    if event.created_by != current_user.id:
        flash("Unauthorized.", "danger")
        return redirect(url_for('events.student_dashboard'))
    
    if not event.is_pending:
        flash("Only pending events can be withdrawn.", "warning")
        return redirect(url_for('events.student_dashboard'))
    
    event.status = EventStatus.Draft
    db.session.commit()
    
    log_action('WITHDRAW', 'EVENT', event_id, f"Withdrew event: {event.title}")
    flash(f"Event '{event.title}' withdrawn to draft.", "info")
    return redirect(url_for('events.student_dashboard'))
