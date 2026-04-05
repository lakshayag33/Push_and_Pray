from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.models import db, User

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    """Decorator: user must be admin."""
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/admin')
@admin_required
def panel():
    users = User.query.order_by(User.created_at.desc()).all()
    user_data = []
    for u in users:
        user_data.append({
            'id': u.id,
            'email': u.email,
            'name': u.display_name,
            'role': u.role,
            'reviewer_status': u.reviewer_status,
            'created_at': u.created_at.strftime('%B %d, %Y') if u.created_at else 'N/A'
        })

    pending_reviewers = User.query.filter_by(
        role='reviewer', reviewer_status='pending'
    ).all()
    pending_data = []
    for u in pending_reviewers:
        pending_data.append({
            'id': u.id,
            'email': u.email,
            'name': u.display_name,
            'created_at': u.created_at.strftime('%B %d, %Y') if u.created_at else 'N/A'
        })

    return render_template('admin/panel.html',
                           users=user_data,
                           pending_reviewers=pending_data)


@admin_bp.route('/admin/approve/<int:user_id>', methods=['POST'])
@admin_required
def approve_reviewer(user_id):
    user = User.query.get_or_404(user_id)
    if user.role != 'reviewer':
        flash('This user is not a reviewer.', 'danger')
        return redirect(url_for('admin.panel'))
    user.reviewer_status = 'active'
    db.session.commit()
    flash(f'Reviewer {user.display_name} approved!', 'success')
    return redirect(url_for('admin.panel'))


@admin_bp.route('/admin/reject/<int:user_id>', methods=['POST'])
@admin_required
def reject_reviewer(user_id):
    user = User.query.get_or_404(user_id)
    if user.role != 'reviewer':
        flash('This user is not a reviewer.', 'danger')
        return redirect(url_for('admin.panel'))
    user.reviewer_status = 'rejected'
    db.session.commit()
    flash(f'Reviewer {user.display_name} rejected.', 'info')
    return redirect(url_for('admin.panel'))
