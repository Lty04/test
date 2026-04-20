from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Restaurant, Menu, Review

restaurant_bp = Blueprint('restaurant', __name__, url_prefix='/restaurants')

@restaurant_bp.route('/')
def list_restaurants():
    restaurants = Restaurant.query.filter_by(is_open=True).all()
    return render_template('restaurant/list.html', restaurants=restaurants)

@restaurant_bp.route('/<int:restaurant_id>')
def restaurant_detail(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    menus = Menu.query.filter_by(restaurant_id=restaurant_id, is_available=True).all()
    reviews = Review.query.filter_by(restaurant_id=restaurant_id).order_by(Review.created_at.desc()).limit(10).all()
    return render_template('restaurant/detail.html', restaurant=restaurant, menus=menus, reviews=reviews)

@restaurant_bp.route('/<int:restaurant_id>/menu/<int:menu_id>')
def menu_detail(restaurant_id, menu_id):
    menu = Menu.query.get_or_404(menu_id)
    return render_template('restaurant/menu_detail.html', menu=menu)

@restaurant_bp.route('/manage')
@login_required
def manage_menu():
    if current_user.role != 'restaurant':
        flash('无权访问', 'error')
        return redirect(url_for('index'))
    
    restaurants = Restaurant.query.filter_by(owner_id=current_user.id).all()
    return render_template('restaurant/manage.html', restaurants=restaurants)

@restaurant_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_restaurant():
    if current_user.role != 'restaurant':
        flash('无权访问', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        location = request.form.get('location')
        phone = request.form.get('phone')
        delivery_fee = float(request.form.get('delivery_fee', 5.0))
        min_order = float(request.form.get('min_order', 15.0))
        
        restaurant = Restaurant(
            name=name,
            description=description,
            owner_id=current_user.id,
            location=location,
            phone=phone,
            delivery_fee=delivery_fee,
            min_order=min_order
        )
        
        db.session.add(restaurant)
        db.session.commit()
        
        flash('餐厅创建成功！', 'success')
        return redirect(url_for('restaurant.manage_menu'))
    
    return render_template('restaurant/add.html')

@restaurant_bp.route('/<int:restaurant_id>/add_menu', methods=['GET', 'POST'])
@login_required
def add_menu(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    
    if current_user.role != 'restaurant' or restaurant.owner_id != current_user.id:
        flash('无权访问', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = float(request.form.get('price'))
        category = request.form.get('category')
        
        menu = Menu(
            restaurant_id=restaurant_id,
            name=name,
            description=description,
            price=price,
            category=category
        )
        
        db.session.add(menu)
        db.session.commit()
        
        flash('菜品添加成功！', 'success')
        return redirect(url_for('restaurant.manage_menu'))
    
    return render_template('restaurant/add_menu.html', restaurant=restaurant)

@restaurant_bp.route('/menu/<int:menu_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_menu(menu_id):
    menu = Menu.query.get_or_404(menu_id)
    restaurant = Restaurant.query.get(menu.restaurant_id)
    
    if current_user.role != 'restaurant' or restaurant.owner_id != current_user.id:
        flash('无权访问', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        menu.name = request.form.get('name')
        menu.description = request.form.get('description')
        menu.price = float(request.form.get('price'))
        menu.category = request.form.get('category')
        menu.is_available = bool(request.form.get('is_available'))
        
        db.session.commit()
        
        flash('菜品更新成功！', 'success')
        return redirect(url_for('restaurant.manage_menu'))
    
    return render_template('restaurant/edit_menu.html', menu=menu, restaurant=restaurant)

@restaurant_bp.route('/menu/<int:menu_id>/delete', methods=['POST'])
@login_required
def delete_menu(menu_id):
    menu = Menu.query.get_or_404(menu_id)
    restaurant = Restaurant.query.get(menu.restaurant_id)
    
    if current_user.role != 'restaurant' or restaurant.owner_id != current_user.id:
        flash('无权访问', 'error')
        return redirect(url_for('index'))
    
    db.session.delete(menu)
    db.session.commit()
    
    flash('菜品已删除', 'success')
    return redirect(url_for('restaurant.manage_menu'))
