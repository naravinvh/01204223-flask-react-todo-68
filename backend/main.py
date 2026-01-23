from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todos.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy()
db.init_app(app)

migrate = Migrate(app, db)

class TodoItem(db.Model):
    __tablename__ = "todo_item"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    done = db.Column(db.Boolean, default=False)

    comments = relationship(
        "Comment",
        back_populates="todo",
        cascade="all, delete"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "done": self.done,
            "comments": [c.to_dict() for c in self.comments]
        }


class Comment(db.Model):
    __tablename__ = "comment"

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(250), nullable=False)

    todo_id = db.Column(
        db.Integer,
        db.ForeignKey("todo_item.id"),
        nullable=False
    )

    todo = relationship("TodoItem", back_populates="comments")

    def to_dict(self):
        return {
            "id": self.id,
            "message": self.message,
            "todo_id": self.todo_id
        }


INITIAL_TODOS = [
    TodoItem(title='Learn Flask'),
    TodoItem(title='Build a Flask App'),
]

with app.app_context():
    if TodoItem.query.count() == 0:
        for item in INITIAL_TODOS:
            db.session.add(item)
        db.session.commit()


@app.route("/api/todos/", methods=["GET"])
def get_todos():
    todos = TodoItem.query.all()
    return jsonify([t.to_dict() for t in todos])


@app.route("/api/todos/", methods=["POST"])
def create_todo():
    data = request.get_json()
    todo = TodoItem(title=data["title"], done=data.get("done", False))
    db.session.add(todo)
    db.session.commit()
    return jsonify(todo.to_dict())


@app.route("/api/todos/<int:id>/toggle/", methods=["PATCH"])
def toggle_todo(id):
    todo = TodoItem.query.get_or_404(id)
    todo.done = not todo.done
    db.session.commit()
    return jsonify(todo.to_dict())


@app.route("/api/todos/<int:id>/", methods=["DELETE"])
def delete_todo(id):
    todo = TodoItem.query.get_or_404(id)
    db.session.delete(todo)
    db.session.commit()
    return jsonify({"message": "Todo deleted"})

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