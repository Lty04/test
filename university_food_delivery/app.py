from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager
from config import Config
from models import db, User

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 初始化扩展
    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # 注册蓝图
    from routes.auth import auth_bp
    from routes.restaurant import restaurant_bp
    from routes.order import order_bp
    from routes.user import user_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(restaurant_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(user_bp)
    
    # 首页路由
    @app.route('/')
    def index():
        return render_template('index.html')
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
        
        # 创建默认管理员账号（如果不存在）
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@university.edu',
                role='admin',
                phone='1234567890'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            
            # 创建示例学生账号
            student = User(
                username='student',
                email='student@university.edu',
                role='student',
                phone='1234567891',
                address='学生宿舍 A 栋 101'
            )
            student.set_password('student123')
            db.session.add(student)
            
            # 创建示例商家账号
            restaurant_owner = User(
                username='restaurant',
                email='restaurant@university.edu',
                role='restaurant',
                phone='1234567892'
            )
            restaurant_owner.set_password('restaurant123')
            db.session.add(restaurant_owner)
            
            # 创建示例配送员账号
            delivery = User(
                username='delivery',
                email='delivery@university.edu',
                role='delivery',
                phone='1234567893'
            )
            delivery.set_password('delivery123')
            db.session.add(delivery)
            
            db.session.commit()
            
            # 创建示例餐厅
            from models import Restaurant, Menu
            
            if not Restaurant.query.first():
                rest_owner = User.query.filter_by(username='restaurant').first()
                restaurant = Restaurant(
                    name='校园美食城',
                    description='提供各类美味快餐，价格实惠，送货上门',
                    owner_id=rest_owner.id,
                    location='学校食堂一楼',
                    phone='1234567892',
                    delivery_fee=3.0,
                    min_order=15.0,
                    rating=4.5
                )
                db.session.add(restaurant)
                db.session.commit()
                
                # 创建示例菜品
                menus = [
                    Menu(restaurant_id=restaurant.id, name='宫保鸡丁饭', description='经典川菜，香辣可口', price=15.8, category='主食'),
                    Menu(restaurant_id=restaurant.id, name='鱼香肉丝饭', description='酸甜适中，开胃下饭', price=14.8, category='主食'),
                    Menu(restaurant_id=restaurant.id, name='红烧狮子头', description='肉质鲜嫩，入口即化', price=18.8, category='主食'),
                    Menu(restaurant_id=restaurant.id, name='清炒时蔬', description='新鲜蔬菜，健康美味', price=8.8, category='素菜'),
                    Menu(restaurant_id=restaurant.id, name='可乐', description='冰镇可乐', price=3.0, category='饮料'),
                    Menu(restaurant_id=restaurant.id, name='豆浆', description='现磨豆浆', price=2.5, category='饮料'),
                ]
                
                for menu in menus:
                    db.session.add(menu)
                
                db.session.commit()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
