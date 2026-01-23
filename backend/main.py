from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import TodoItem, Comment, db

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todos.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
migrate = Migrate(app, db)


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
