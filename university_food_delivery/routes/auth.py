from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.is_active:
            login_user(user)
            next_page = request.args.get('next')
            flash('登录成功！', 'success')
            
            if next_page:
                return redirect(next_page)
            
            # 根据角色跳转到不同页面
            if user.role == 'student':
                return redirect(url_for('restaurant.list_restaurants'))
            elif user.role == 'restaurant':
                return redirect(url_for('restaurant.manage_menu'))
            elif user.role == 'delivery':
                return redirect(url_for('order.delivery_orders'))
            elif user.role == 'admin':
                return redirect(url_for('user.admin_dashboard'))
        
        flash('用户名或密码错误', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        phone = request.form.get('phone')
        address = request.form.get('address')
        
        # 验证用户是否存在
        if User.query.filter_by(username=username).first():
            flash('用户名已存在', 'error')
            return render_template('auth/register.html')
        
        if User.query.filter_by(email=email).first():
            flash('邮箱已被注册', 'error')
            return render_template('auth/register.html')
        
        # 创建新用户
        user = User(
            username=username,
            email=email,
            role=role,
            phone=phone,
            address=address
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('注册成功，请登录', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已退出登录', 'info')
    return redirect(url_for('auth.login'))
