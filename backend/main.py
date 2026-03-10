from pprint import pp
import os
import sys
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import Mapped, mapped_column
from flask_migrate import Migrate
from sqlalchemy import Integer, String, ForeignKey                            # เพิ่ม import Foreignkey
from sqlalchemy.orm import Mapped, mapped_column, relationship                # เพิ่ม import relatiohship
from models import TodoItem, Comment, db,User
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from flask_jwt_extended import JWTManager

import click


# Load environment variables from .env during local development (optional)
try:
    from dotenv import load_dotenv

    load_dotenv(dotenv_path=Path(__file__).with_name(".env"))
except Exception:
    # Keep working even if python-dotenv isn't available
    pass

# Load local_config for deployment / non-env defaults
try:
    from local_config import CONFIG_DB_URI, CONFIG_JWT_SECRET
except Exception:
    CONFIG_DB_URI = "sqlite:///todos.db"
    CONFIG_JWT_SECRET = "dev-secret-change-me"


app = Flask(__name__)
CORS(app)

# During pytest, force an in-memory sqlite database to avoid hitting MySQL
if "pytest" in sys.modules or "PYTEST_CURRENT_TEST" in os.environ:
    db_uri = "sqlite:///:memory:"
else:
    db_uri = os.getenv("SQLALCHEMY_DATABASE_URI", CONFIG_DB_URI)

app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
app.config["JWT_SECRET_KEY"] = os.getenv(
    "JWT_SECRET_KEY",
    CONFIG_JWT_SECRET,
)

class Base(DeclarativeBase):
  pass

db.init_app(app)                                                     # แก้จาก db = SQLAlchemy(app, model_class=Base)
migrate = Migrate(app, db)
jwt = JWTManager(app)

"""
class TodoItem(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    done: Mapped[bool] = mapped_column(default=False)

    ##### เพิ่มส่วน relationship  ซึ่งตรงนี้จะไม่กระทบ schema database เลย (เพราะว่าไม่มีการ map ไปยังคอลัมน์ใดๆ)
    comments: Mapped[list["Comment"]] = relationship(back_populates="todo")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "done": self.done,
            "comments": [
                comment.to_dict() for comment in self.comments
            ]
        }
"""
"""
class Comment(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    message: Mapped[str] = mapped_column(String(250))
    todo_id: Mapped[int] = mapped_column(ForeignKey('todo_item.id'))

    todo: Mapped["TodoItem"] = relationship(back_populates="comments")

    def to_dict(self):
        return {
            "id": self.id,
            "message": self.message,
            "todo_id": self.todo_id
        }
"""

if 'pytest' not in sys.modules and 'PYTEST_CURRENT_TEST' not in os.environ:
    with app.app_context():
        db.create_all()
"""
INITIAL_TODOS = [
    TodoItem(title='Learn Flask'),
    TodoItem(title='Build a Flask App'),
]

with app.app_context():
    if TodoItem.query.count() == 0:
         for item in INITIAL_TODOS:
             db.session.add(item)
         db.session.commit()
"""

todo_list = [
    { "id": 1,
      "title": 'Learn Flask',
      "done": True },
    { "id": 2,
      "title": 'Build a Flask App',
      "done": False },
]

@app.route('/api/todos/', methods=['GET'])
@jwt_required()
def get_todos():
    todos = TodoItem.query.all()
    return jsonify([todo.to_dict() for todo in todos])


def new_todo(data):
    return TodoItem(title=data['title'], 
                    done=data.get('done', False))


@app.route('/api/todos/', methods=['POST'])
def add_todo():
    data = request.get_json()
    todo = new_todo(data)
    if todo:
        db.session.add(todo)                       # บรรทัดที่ปรับใหม่
        db.session.commit()                        # บรรทัดที่ปรับใหม่ 
        return jsonify(todo.to_dict())             # บรรทัดที่ปรับใหม่
    else:
        # return http response code 400 for bad requests
        return (jsonify({'error': 'Invalid todo data'}), 400) 
    

@app.route('/api/todos/<int:id>/toggle/', methods=['PATCH'])
def toggle_todo(id):
    todo = TodoItem.query.get_or_404(id)
    todo.done = not todo.done
    db.session.commit()
    return jsonify(todo.to_dict())


@app.route('/api/todos/<int:id>/', methods=['DELETE'])
def delete_todo(id):
    todo = TodoItem.query.get_or_404(id)
    db.session.delete(todo)
    db.session.commit()
    return jsonify({'message': 'Todo deleted successfully'})

@app.route('/api/todos/<int:todo_id>/comments/', methods=['POST'])
def add_comment(todo_id):
    todo_item = TodoItem.query.get_or_404(todo_id)

    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'Comment message is required'}), 400

    comment = Comment(
        message=data['message'],
        todo_id=todo_item.id
    )
    db.session.add(comment)
    db.session.commit()
 
    return jsonify(comment.to_dict())


@app.route('/api/login/', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Username and password are required'}), 400

    user = User.query.filter_by(username=data['username']).first()
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401

    access_token = create_access_token(identity=user.username)
    return jsonify(access_token=access_token)

@app.cli.command("create-user")
@click.argument("username")
@click.argument("full_name")
@click.argument("password")
def create_user(username, full_name, password):
    user = User.query.filter_by(username=username).first()
    if user:
        click.echo("User already exists.")
        return
    user = User(username=username, full_name=full_name)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    click.echo(f"User {username} created successfully.")


# Serve built React frontend from backend/frontend-static
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    static_dir = os.path.join(app.root_path, "frontend-static")
    requested_path = os.path.join(static_dir, path)

    if path and os.path.isfile(requested_path):
        return send_from_directory("frontend-static", path)

    return send_from_directory("frontend-static", "index.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))