from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
import click
from models import User
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    JWTManager
)

app.config['JWT_SECRET_KEY'] = 'your-secret-key'
jwt = JWTManager(app)

from models import TodoItem, Comment, db

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todos.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
migrate = Migrate(app, db)

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

@app.route('/api/login/', methods=['POST'])
def login():
    data = request.get_json()

    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Username and password are required'}), 400

    user = User.query.filter_by(username=data['username']).first()
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401

    return jsonify({'message': 'Login successful'})

@app.route('/api/login/', methods=['POST'])
def login():
    data = request.get_json()

    user = User.query.filter_by(username=data['username']).first()
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401

    access_token = create_access_token(identity=user.username)
    return jsonify(access_token=access_token)

@app.route('/api/todos/', methods=['GET'])
@jwt_required()
def get_todos():
    todos = TodoItem.query.all()
    return jsonify([todo.to_dict() for todo in todos])
# ======================
# Todo APIs
# ======================

@app.route("/api/todos/", methods=["GET"])
def get_todos():
    todos = TodoItem.query.all()
    return jsonify([t.to_dict() for t in todos])


@app.route("/api/todos/", methods=["POST"])
def create_todo():
    data = request.get_json()

    if not data or "title" not in data:
        return jsonify({"error": "Title is required"}), 400

    todo = TodoItem(
        title=data["title"],
        done=data.get("done", False)
    )
    db.session.add(todo)
    db.session.commit()

    return jsonify(todo.to_dict()), 201


@app.route("/api/todos/<int:id>/toggle/", methods=["PATCH"])
def toggle_todo(id):
    todo = TodoItem.query.get_or_404(id)
    todo.done = not todo.done
    db.session.commit()
    return jsonify(todo.to_dict())


@app.route("/api/todos/<int:id>/", methods=["DELETE"])
def delete_todo(id):
    todo = TodoItem.query.get_or_404(id)

    # cascade="all, delete" จะลบ comment ให้เอง
    db.session.delete(todo)
    db.session.commit()

    return jsonify({"message": "Todo deleted"})


# ======================
# Comment APIs
# ======================

@app.route("/api/todos/<int:todo_id>/comments/", methods=["POST"])
def add_comment(todo_id):
    todo = TodoItem.query.get_or_404(todo_id)

    data = request.get_json()
    if not data or "message" not in data or not data["message"].strip():
        return jsonify({"error": "Comment message is required"}), 400

    comment = Comment(
        message=data["message"],
        todo=todo
    )

    db.session.add(comment)
    db.session.commit()

    return jsonify(comment.to_dict()), 201


# ======================
# Run App
# ======================

if __name__ == "__main__":
    app.run(debug=True)
