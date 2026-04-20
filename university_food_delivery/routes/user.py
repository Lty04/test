from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, User, Restaurant, Order, Review

user_bp = Blueprint('user', __name__, url_prefix='/users')

@user_bp.route('/profile')
@login_required
def profile():
    return render_template('user/profile.html', user=current_user)

@user_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        current_user.phone = request.form.get('phone')
        current_user.address = request.form.get('address')
        
        db.session.commit()
        
        flash('个人信息已更新', 'success')
        return redirect(url_for('user.profile'))
    
    return render_template('user/edit.html', user=current_user)

@user_bp.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('无权访问', 'error')
        return redirect(url_for('index'))
    
    # 统计数据
    total_users = User.query.count()
    total_students = User.query.filter_by(role='student').count()
    total_restaurants = Restaurant.query.count()
    total_orders = Order.query.count()
    
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    
    return render_template('user/admin.html', 
                         total_users=total_users,
                         total_students=total_students,
                         total_restaurants=total_restaurants,
                         total_orders=total_orders,
                         recent_orders=recent_orders)

@user_bp.route('/<int:user_id>/reviews')
def user_reviews(user_id):
    user = User.query.get_or_404(user_id)
    reviews = Review.query.filter_by(user_id=user_id).order_by(Review.created_at.desc()).all()
    return render_template('user/reviews.html', user=user, reviews=reviews)
