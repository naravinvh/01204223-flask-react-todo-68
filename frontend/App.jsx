import { useEffect, useState } from "react";
import TodoItem from "./TodoItem.jsx";
import "./App.css";

const TODOLIST_API_URL = "http://127.0.0.1:5000/api/todos/";

function App() {
  const [todoList, setTodoList] = useState([]);

  // โหลด todo ทั้งหมด
  async function fetchTodoList() {
    const res = await fetch(TODOLIST_API_URL);
    const data = await res.json();
    setTodoList(data);
  }

  useEffect(() => {
    fetchTodoList();
  }, []);

  async function toggleDone(todoId) {
    await fetch(`${TODOLIST_API_URL}${todoId}/toggle/`, {
      method: "PATCH",
    });
    fetchTodoList();
  }

  async function deleteTodo(todoId) {
    await fetch(`${TODOLIST_API_URL}${todoId}/`, {
      method: "DELETE",
    });
    fetchTodoList();
  }

  // ✅ ฟังก์ชันที่คุณแก้ — ถูกต้องแล้ว แค่วางให้ถูกที่
  async function addNewComment(todoId, newComment) {
    try {
      const url = `${TODOLIST_API_URL}${todoId}/comments/`;
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: newComment }),
      });
      if (response.ok) {
        await fetchTodoList();
      }
    } catch (error) {
      console.error("Error adding new comment:", error);
    }
  }

  // ✅ JSX ต้องอยู่ใน return
  return (
    <div className="App">
      <h1>Todo App</h1>

      <ul>
        {todoList.map((todo) => (
          <TodoItem
            key={todo.id}
            todo={todo}
            toggleDone={toggleDone}
            deleteTodo={deleteTodo}
            addNewComment={addNewComment}
          />
        ))}
      </ul>
    </div>
  );
}

export default App;
