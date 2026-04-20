from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import db, Order, OrderItem, Cart, Menu, Restaurant
from datetime import datetime
import random
import string

order_bp = Blueprint('order', __name__, url_prefix='/orders')

def generate_order_number():
    return 'ORD' + datetime.now().strftime('%Y%m%d%H%M%S') + ''.join(random.choices(string.digits, k=4))

@order_bp.route('/')
@login_required
def my_orders():
    if current_user.role == 'student':
        orders = Order.query.filter_by(customer_id=current_user.id).order_by(Order.created_at.desc()).all()
    elif current_user.role == 'restaurant':
        restaurants = Restaurant.query.filter_by(owner_id=current_user.id).all()
        restaurant_ids = [r.id for r in restaurants]
        orders = Order.query.filter(Order.restaurant_id.in_(restaurant_ids)).order_by(Order.created_at.desc()).all()
    else:
        orders = []
    
    return render_template('order/list.html', orders=orders)

@order_bp.route('/<int:order_id>')
@login_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    
    # 权限检查
    if current_user.role == 'student' and order.customer_id != current_user.id:
        flash('无权访问', 'error')
        return redirect(url_for('order.my_orders'))
    
    return render_template('order/detail.html', order=order)

@order_bp.route('/create', methods=['POST'])
@login_required
def create_order():
    if current_user.role != 'student':
        return jsonify({'success': False, 'message': '只有学生可以下单'}), 403
    
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        return jsonify({'success': False, 'message': '购物车为空'}), 400
    
    # 获取餐厅信息（假设所有菜品来自同一家餐厅）
    first_item = cart_items[0]
    menu = Menu.query.get(first_item.menu_id)
    restaurant = Restaurant.query.get(menu.restaurant_id)
    
    # 计算总价
    total_amount = sum(item.menu.price * item.quantity for item in cart_items)
    delivery_fee = restaurant.delivery_fee
    
    if total_amount < restaurant.min_order:
        return jsonify({'success': False, 'message': f'未达到最低起送金额 {restaurant.min_order}元'}), 400
    
    delivery_address = request.form.get('delivery_address', current_user.address)
    special_instructions = request.form.get('special_instructions', '')
    
    # 创建订单
    order = Order(
        order_number=generate_order_number(),
        customer_id=current_user.id,
        restaurant_id=restaurant.id,
        total_amount=total_amount + delivery_fee,
        delivery_address=delivery_address,
        delivery_fee=delivery_fee,
        special_instructions=special_instructions,
        status='pending'
    )
    
    db.session.add(order)
    db.session.flush()
    
    # 创建订单项
    for cart_item in cart_items:
        menu = Menu.query.get(cart_item.menu_id)
        order_item = OrderItem(
            order_id=order.id,
            menu_id=menu.id,
            menu_name=menu.name,
            quantity=cart_item.quantity,
            unit_price=menu.price,
            subtotal=menu.price * cart_item.quantity
        )
        db.session.add(order_item)
        
        # 从购物车删除
        db.session.delete(cart_item)
    
    db.session.commit()
    
    return jsonify({'success': True, 'order_id': order.id, 'order_number': order.order_number})

@order_bp.route('/<int:order_id>/cancel', methods=['POST'])
@login_required
def cancel_order(order_id):
    order = Order.query.get_or_404(order_id)
    
    if order.customer_id != current_user.id:
        flash('无权操作', 'error')
        return redirect(url_for('order.my_orders'))
    
    if order.status not in ['pending', 'confirmed']:
        flash('订单无法取消', 'error')
        return redirect(url_for('order.order_detail', order_id=order_id))
    
    order.status = 'cancelled'
    db.session.commit()
    
    flash('订单已取消', 'success')
    return redirect(url_for('order.my_orders'))

@order_bp.route('/<int:order_id>/confirm', methods=['POST'])
@login_required
def confirm_order(order_id):
    order = Order.query.get_or_404(order_id)
    restaurant = Restaurant.query.get(order.restaurant_id)
    
    if current_user.role != 'restaurant' or restaurant.owner_id != current_user.id:
        flash('无权操作', 'error')
        return redirect(url_for('order.my_orders'))
    
    if order.status != 'pending':
        flash('订单状态不正确', 'error')
        return redirect(url_for('order.order_detail', order_id=order_id))
    
    order.status = 'confirmed'
    db.session.commit()
    
    flash('订单已确认', 'success')
    return redirect(url_for('order.my_orders'))

@order_bp.route('/<int:order_id>/prepare', methods=['POST'])
@login_required
def prepare_order(order_id):
    order = Order.query.get_or_404(order_id)
    restaurant = Restaurant.query.get(order.restaurant_id)
    
    if current_user.role != 'restaurant' or restaurant.owner_id != current_user.id:
        flash('无权操作', 'error')
        return redirect(url_for('order.my_orders'))
    
    if order.status != 'confirmed':
        flash('订单状态不正确', 'error')
        return redirect(url_for('order.order_detail', order_id=order_id))
    
    order.status = 'preparing'
    db.session.commit()
    
    flash('订单制作中', 'success')
    return redirect(url_for('order.my_orders'))

@order_bp.route('/<int:order_id>/deliver', methods=['POST'])
@login_required
def deliver_order(order_id):
    order = Order.query.get_or_404(order_id)
    
    if current_user.role not in ['restaurant', 'delivery']:
        flash('无权操作', 'error')
        return redirect(url_for('order.my_orders'))
    
    if order.status != 'preparing':
        flash('订单状态不正确', 'error')
        return redirect(url_for('order.order_detail', order_id=order_id))
    
    order.status = 'delivering'
    if current_user.role == 'delivery':
        order.delivery_person_id = current_user.id
    
    db.session.commit()
    
    flash('订单配送中', 'success')
    return redirect(url_for('order.my_orders'))

@order_bp.route('/<int:order_id>/complete', methods=['POST'])
@login_required
def complete_order(order_id):
    order = Order.query.get_or_404(order_id)
    
    if current_user.role != 'delivery' or order.delivery_person_id != current_user.id:
        flash('无权操作', 'error')
        return redirect(url_for('order.my_orders'))
    
    if order.status != 'delivering':
        flash('订单状态不正确', 'error')
        return redirect(url_for('order.order_detail', order_id=order_id))
    
    order.status = 'delivered'
    db.session.commit()
    
    flash('订单已完成', 'success')
    return redirect(url_for('order.my_orders'))

@order_bp.route('/delivery')
@login_required
def delivery_orders():
    if current_user.role != 'delivery':
        flash('无权访问', 'error')
        return redirect(url_for('index'))
    
    # 显示可配送的订单和已接单的订单
    orders = Order.query.filter(
        Order.status.in_(['preparing', 'delivering'])
    ).order_by(Order.created_at.desc()).all()
    
    return render_template('order/delivery.html', orders=orders)

@order_bp.route('/cart')
@login_required
def cart():
    if current_user.role != 'student':
        flash('无权访问', 'error')
        return redirect(url_for('index'))
    
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    
    # 按餐厅分组
    restaurant_cart = {}
    for item in cart_items:
        menu = Menu.query.get(item.menu_id)
        restaurant = Restaurant.query.get(menu.restaurant_id)
        
        if restaurant.id not in restaurant_cart:
            restaurant_cart[restaurant.id] = {
                'restaurant': restaurant,
                'items': [],
                'total': 0
            }
        
        restaurant_cart[restaurant.id]['items'].append({
            'cart_item': item,
            'menu': menu,
            'subtotal': menu.price * item.quantity
        })
        restaurant_cart[restaurant.id]['total'] += menu.price * item.quantity
    
    return render_template('order/cart.html', restaurant_cart=restaurant_cart)

@order_bp.route('/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    if current_user.role != 'student':
        return jsonify({'success': False, 'message': '只有学生可以添加购物车'}), 403
    
    menu_id = request.form.get('menu_id')
    quantity = int(request.form.get('quantity', 1))
    
    menu = Menu.query.get(menu_id)
    if not menu:
        return jsonify({'success': False, 'message': '菜品不存在'}), 404
    
    # 检查是否已在购物车
    existing = Cart.query.filter_by(user_id=current_user.id, menu_id=menu_id).first()
    if existing:
        existing.quantity += quantity
    else:
        cart_item = Cart(
            user_id=current_user.id,
            menu_id=menu_id,
            quantity=quantity
        )
        db.session.add(cart_item)
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': '已添加到购物车'})

@order_bp.route('/cart/remove/<int:cart_id>', methods=['POST'])
@login_required
def remove_from_cart(cart_id):
    cart_item = Cart.query.get_or_404(cart_id)
    
    if cart_item.user_id != current_user.id:
        return jsonify({'success': False, 'message': '无权操作'}), 403
    
    db.session.delete(cart_item)
    db.session.commit()
    
    return jsonify({'success': True, 'message': '已从购物车移除'})

@order_bp.route('/cart/update/<int:cart_id>', methods=['POST'])
@login_required
def update_cart(cart_id):
    cart_item = Cart.query.get_or_404(cart_id)
    
    if cart_item.user_id != current_user.id:
        return jsonify({'success': False, 'message': '无权操作'}), 403
    
    quantity = int(request.form.get('quantity', 1))
    if quantity <= 0:
        db.session.delete(cart_item)
    else:
        cart_item.quantity = quantity
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': '购物车已更新'})
