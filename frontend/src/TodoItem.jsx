import './App.css'
import { useState } from 'react'

function TodoItem({todo, toggleDone, deleteTodo, addNewComment, deleteComment}) {
    const [newComment, setNewComment] = useState("");      // เพิ่ม state newComment
    return (
        <li>
            <span className={todo.done ? "done" : ""}>{todo.title}</span>
            <button onClick={() => {toggleDone(todo.id)}}>Toggle</button>
            <button onClick={() => {deleteTodo(todo.id)}}>❌</button>
            {todo.comments && todo.comments.length > 0 ? (
            <>
                 <b>{todo.comments.length} comments:</b>
                <ul>
                {todo.comments.map(comment => (
                    <li key={comment.id}>
                      {comment.message}{' '}
                      {deleteComment && (
                        <button onClick={() => deleteComment(comment.id)}>🗑</button>
                      )}
                    </li>
                ))}
                </ul>
            </>
            ) : (
            <p>No comments</p>
            )}          
            <div className="new-comment-forms">
              <input
                type="text"
                value={newComment}
                onChange={(e) => {
                  const value = e.target.value;
                  setNewComment(value);
                }}
              />

              <button onClick={() => {                         // แก้ส่วนนี้
                addNewComment(todo.id, newComment);
                setNewComment("");
              }}>Add Comment</button>
            </div>
        </li>
    )
}

export default TodoItem