from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from app import db
from app.models.user import User, UserRole
from app.forms.auth_form import LoginForm, RegistrationForm
from app.utils.audit_helper import log_action

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data, 
            email=form.email.data,
            role=UserRole.Student,
            department=form.department.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        # Log the user in directly after registration
        login_user(user)
        
        # AUDIT LOG
        log_action('CREATE', 'USER', user.id, f"Registered new user: {user.username}")
        
        flash('Registration successful!', 'success')
        return redirect(url_for('events.student_dashboard'))
    
    return render_template('auth/register.html', title='Register', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter((User.username == form.username.data) | (User.email == form.username.data)).first()
        
        if user is None or not user.check_password(form.password.data):
            # Log failed login attempt if user exists (optional, let's skip for now or log as system)
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember.data)
        
        # AUDIT LOG
        log_action('LOGIN', 'USER', user.id, f"User logged in: {user.username}")
        
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            if user.role.value == 'Admin':
                next_page = url_for('admin.dashboard')
            elif user.role.value == 'Department Head':
                next_page = url_for('dept_head.dashboard')
            elif user.role.value == 'Faculty':
                next_page = url_for('faculty.dashboard')
            else:
                next_page = url_for('events.student_dashboard')
            
        flash(f'Logged in successfully as {user.role.value}.', 'success')
        return redirect(next_page)
        
    return render_template('auth/login.html', title='Sign In', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    # AUDIT LOG (before logging out so current_user is available)
    log_action('LOGOUT', 'USER', current_user.id, f"User logged out: {current_user.username}")
    
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/profile-settings')
@login_required
def profile_settings():
    """Update user profile and password."""
    return render_template('auth/profile_settings.html')
