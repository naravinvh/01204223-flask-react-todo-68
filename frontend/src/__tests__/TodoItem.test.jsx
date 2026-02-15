import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import TodoItem from "../TodoItem.jsx";

// TodoItem พื้นฐานสำหรับทดสอบ
const baseTodo = {
  id: 1,
  title: "Sample Todo",
  done: false,
  comments: [],
};

describe("TodoItem", () => {
  it("renders with no comments correctly", () => {
    render(<TodoItem todo={baseTodo} />);

    expect(screen.getByText("Sample Todo")).toBeInTheDocument();
    expect(screen.getByText("No comments")).toBeInTheDocument();
  });

  it("does not show no comments message when it has a comment", () => {
    const todoWithComment = {
      ...baseTodo,
      comments: [{ id: 1, message: "First comment" }],
    };

    render(<TodoItem todo={todoWithComment} />);

    expect(screen.queryByText("No comments")).not.toBeInTheDocument();
    expect(screen.getByText("First comment")).toBeInTheDocument();
  });

  it("renders with multiple comments correctly", () => {
    const todoWithComments = {
      ...baseTodo,
      comments: [
        { id: 1, message: "First comment" },
        { id: 2, message: "Another comment" },
      ],
    };

    render(<TodoItem todo={todoWithComments} />);

    expect(screen.getByText("Sample Todo")).toBeInTheDocument();
    expect(screen.getByText("First comment")).toBeInTheDocument();
    expect(screen.getByText("Another comment")).toBeInTheDocument();
  });
});
