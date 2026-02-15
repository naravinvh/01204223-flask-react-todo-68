import { render, screen, fireEvent, within } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import userEvent from '@testing-library/user-event';
import TodoItem from '../TodoItem.jsx';

const baseTodo = {
  id: 1,
  title: 'Sample Todo',
  done: false,
  comments: [],
};

describe('TodoItem', () => {
  it('renders with no comments correctly', () => {
    render(<TodoItem todo={baseTodo} />);

    expect(screen.getByText('Sample Todo')).toBeInTheDocument();
    expect(screen.getByText('No comments')).toBeInTheDocument();
  });

  it('renders with comments correctly', () => {
    const todoWithComments = {
      ...baseTodo,
      comments: [
        { id: 1, message: 'First comment' },
        { id: 2, message: 'Another comment' },
      ],
    };

    render(<TodoItem todo={todoWithComments} />);

    expect(screen.getByText('Sample Todo')).toBeInTheDocument();
    expect(screen.getByText('First comment')).toBeInTheDocument();
    expect(screen.getByText('Another comment')).toBeInTheDocument();

    const list = screen.getByRole('list'); // <ul>
    const items = within(list).getAllByRole('listitem');

    expect(items).toHaveLength(2);
  });

  it('does not show no comments message when it has a comment', () => {
    const todoWithComment = {
      ...baseTodo,
      comments: [{ id: 1, message: 'First comment' }],
    };

    render(<TodoItem todo={todoWithComment} />);
    expect(screen.queryByText('No comments')).not.toBeInTheDocument();
  });

  it('makes callback to toggleDone when Toggle button is clicked', () => {
    const onToggleDone = vi.fn();

    render(<TodoItem todo={baseTodo} toggleDone={onToggleDone} />);
    fireEvent.click(screen.getByRole('button', { name: /toggle/i }));

    expect(onToggleDone).toHaveBeenCalledWith(baseTodo.id);
  });

  it('makes callback to deleteTodo when delete button is clicked', () => {
    const onDeleteTodo = vi.fn();

    render(<TodoItem todo={baseTodo} deleteTodo={onDeleteTodo} />);
    fireEvent.click(screen.getByRole('button', { name: '❌' }));

    expect(onDeleteTodo).toHaveBeenCalledWith(baseTodo.id);
  });

  it('makes callback to addNewComment when a new comment is added', async () => {
    const onAddNewComment = vi.fn();

    render(<TodoItem todo={baseTodo} addNewComment={onAddNewComment} />);

    await userEvent.type(screen.getByRole('textbox'), 'New comment');
    fireEvent.click(screen.getByRole('button', { name: /add comment/i }));

    expect(onAddNewComment).toHaveBeenCalledWith(baseTodo.id, 'New comment');
  });
});
