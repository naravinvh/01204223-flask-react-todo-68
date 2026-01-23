from flask import Flask, jsonify, request
from flask_cors import CORS

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

app = Flask(__name__)
CORS(app)

# ตั้งค่า database (sqlite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'

# base class สำหรับ model
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(app, model_class=Base)

# ===== Model แรก =====
class TodoItem(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    done: Mapped[bool] = mapped_column(default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "done": self.done
        }

# ===== สร้าง database + table (ชั่วคราว) =====
with app.app_context():
    db.create_all()

@app.route("/")
def index():
    return "Flask backend is running"

if __name__ == "__main__":
    app.run(debug=True, port=5001)
