import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import App from '../App';

const todoItem1 = {
  id: 1,
  title: 'First todo',
  done: false,
  comments: [],
};

const todoItem2 = {
  id: 2,
  title: 'Second todo',
  done: false,
  comments: [
    { id: 1, message: 'First comment' },
    { id: 2, message: 'Second comment' },
  ],
};

const originalTodoList = [
  todoItem1,
  todoItem2,
];

const mockResponse = (data) =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve(data),
  });

describe('App', () => {
  beforeEach(() => {
    global.fetch = vi.fn();
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  it('renders correctly', async () => {
    global.fetch.mockImplementationOnce(() =>
      mockResponse(originalTodoList)
    );

    render(<App />);

    expect(await screen.findByText('First todo')).toBeInTheDocument();
    expect(await screen.findByText('Second todo')).toBeInTheDocument();
  });

  it('toggles done on a todo item', async () => {
    const toggledTodoItem1 = {
      ...todoItem1,
      done: true,
    };

    global.fetch
      .mockImplementationOnce(() => mockResponse(originalTodoList))
      .mockImplementationOnce(() => mockResponse(toggledTodoItem1));

    render(<App />);

    const firstTodo = await screen.findByText('First todo');
    expect(firstTodo).not.toHaveClass('done');

    const toggleButtons = await screen.findAllByRole('button', { name: /toggle/i });
    toggleButtons[0].click();

    expect(await screen.findByText('First todo')).toHaveClass('done');

    expect(global.fetch).toHaveBeenLastCalledWith(
      expect.stringMatching(/1\/toggle/),
      { method: 'PATCH' }
    );
  });
});
