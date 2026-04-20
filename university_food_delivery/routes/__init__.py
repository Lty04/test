from .auth import auth_bp
from .restaurant import restaurant_bp
from .order import order_bp
from .user import user_bp

__all__ = ['auth_bp', 'restaurant_bp', 'order_bp', 'user_bp']
