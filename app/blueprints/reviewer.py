from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.models import db, User, ReviewerInvite

reviewer_bp = Blueprint('reviewer', __name__)


def reviewer_required(f):
    """Decorator: user must be an active reviewer."""
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if current_user.role != 'reviewer' or current_user.reviewer_status != 'active':
            abort(403)
        return f(*args, **kwargs)
    return decorated


def reviewer_access_required(f):
    """Decorator: reviewer must have an accepted invite for the requested user_id."""
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if current_user.role != 'reviewer' or current_user.reviewer_status != 'active':
            abort(403)
        user_id = kwargs.get('user_id')
        invite = ReviewerInvite.query.filter_by(
            user_id=user_id,
            reviewer_id=current_user.id,
            status='accepted'
        ).first()
        if not invite:
            abort(403)
        return f(*args, **kwargs)
    return decorated


@reviewer_bp.route('/reviewer')
@reviewer_required
def dashboard():
    # Accepted invitations
    accepted = ReviewerInvite.query.filter_by(
        reviewer_id=current_user.id, status='accepted'
    ).all()
    accepted_data = []
    for inv in accepted:
        user = User.query.get(inv.user_id)
        if user:
            accepted_data.append({
                'user_id': user.id,
                'username': user.display_name,
                'created_at': inv.created_at
            })

    # Pending invitations
    pending = ReviewerInvite.query.filter_by(
        reviewer_id=current_user.id, status='pending'
    ).all()
    pending_data = []
    for inv in pending:
        user = User.query.get(inv.user_id)
        if user:
            pending_data.append({
                'id': inv.id,
                'user_id': user.id,
                'username': user.display_name,
                'created_at': inv.created_at
            })

    return render_template('reviewer/dashboard.html',
                           accepted=accepted_data,
                           pending=pending_data)


@reviewer_bp.route('/reviewer/accept/<int:invite_id>', methods=['POST'])
@reviewer_required
def accept_invite(invite_id):
    invite = ReviewerInvite.query.get_or_404(invite_id)
    if invite.reviewer_id != current_user.id:
        abort(403)
    invite.status = 'accepted'
    db.session.commit()
    flash('Invitation accepted!', 'success')
    return redirect(url_for('reviewer.dashboard'))


@reviewer_bp.route('/reviewer/decline/<int:invite_id>', methods=['POST'])
@reviewer_required
def decline_invite(invite_id):
    invite = ReviewerInvite.query.get_or_404(invite_id)
    if invite.reviewer_id != current_user.id:
        abort(403)
    invite.status = 'revoked'
    db.session.commit()
    flash('Invitation declined.', 'info')
    return redirect(url_for('reviewer.dashboard'))


@reviewer_bp.route('/reviewer/charts/<int:user_id>')
@reviewer_access_required
def charts(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('reviewer/charts.html',
                           target_user_id=user.id,
                           target_username=user.display_name)
