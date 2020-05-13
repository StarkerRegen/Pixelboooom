from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin

#定义登录用户查询方法
@login_manager.user_loader
def  load_user(user_id):
    return User.query.get(int(user_id))

#用户模型
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(100),nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}','{self.email}')"

class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    style = db.Column(db.String(10), nullable=False)
    imglist = db.Column(db.String(300), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self): 
        return f"Post('{self.title}','{self.category}','{self.style}','{self.imglist}','{self.date_posted}')"

# db.drop_all()
# db.create_all()