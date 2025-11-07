import React, { useState, useEffect } from 'react';

const TaskList = () => {
    const [tasks, setTasks] = useState([]);
    const [comments, setComments] = useState({});
    const [newTask, setNewTask] = useState({ title: '', description: '' });
    const [editingTask, setEditingTask] = useState(null);
    const [newComment, setNewComment] = useState('');

    // Fetch tasks on component mount
    useEffect(() => {
        fetchTasks();
    }, []);

    const fetchTasks = async () => {
        try {
            const response = await fetch('http://localhost:5000/api/tasks');
            const data = await response.json();
            setTasks(data);
            
            // Fetch comments for each task
            data.forEach(task => {
                fetchComments(task.id);
            });
        } catch (error) {
            console.error('Error fetching tasks:', error);
        }
    };

    const fetchComments = async (taskId) => {
        try {
            const response = await fetch(`http://localhost:5000/api/tasks/${taskId}/comments`);
            const data = await response.json();
            setComments(prev => ({ ...prev, [taskId]: data }));
        } catch (error) {
            console.error('Error fetching comments:', error);
        }
    };

    const createTask = async (e) => {
        e.preventDefault();
        try {
            const response = await fetch('http://localhost:5000/api/tasks', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(newTask),
            });
            
            if (response.ok) {
                setNewTask({ title: '', description: '' });
                fetchTasks();
            }
        } catch (error) {
            console.error('Error creating task:', error);
        }
    };

    const updateTask = async (e) => {
        e.preventDefault();
        try {
            const response = await fetch(`http://localhost:5000/api/tasks/${editingTask.id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(editingTask),
            });
            
            if (response.ok) {
                setEditingTask(null);
                fetchTasks();
            }
        } catch (error) {
            console.error('Error updating task:', error);
        }
    };

    const deleteTask = async (taskId) => {
        try {
            const response = await fetch(`http://localhost:5000/api/tasks/${taskId}`, {
                method: 'DELETE',
            });
            
            if (response.ok) {
                fetchTasks();
            }
        } catch (error) {
            console.error('Error deleting task:', error);
        }
    };

    const addComment = async (taskId) => {
        if (!newComment.trim()) return;
        
        try {
            const response = await fetch(`http://localhost:5000/api/tasks/${taskId}/comments`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ content: newComment }),
            });
            
            if (response.ok) {
                setNewComment('');
                fetchComments(taskId);
            }
        } catch (error) {
            console.error('Error adding comment:', error);
        }
    };

    const deleteComment = async (commentId, taskId) => {
        try {
            const response = await fetch(`http://localhost:5000/api/comments/${commentId}`, {
                method: 'DELETE',
            });
            
            if (response.ok) {
                fetchComments(taskId);
            }
        } catch (error) {
            console.error('Error deleting comment:', error);
        }
    };

    return (
        <div className="task-list">
            <h2>Task Management</h2>
            
            {/* Create Task Form */}
            <form onSubmit={createTask} className="task-form">
                <h3>Create New Task</h3>
                <input
                    type="text"
                    placeholder="Task Title"
                    value={newTask.title}
                    onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
                    required
                />
                <textarea
                    placeholder="Task Description"
                    value={newTask.description}
                    onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
                />
                <button type="submit">Create Task</button>
            </form>

            {/* Tasks List */}
            <div className="tasks">
                {tasks.map(task => (
                    <div key={task.id} className="task-item">
                        {editingTask?.id === task.id ? (
                            <form onSubmit={updateTask} className="edit-form">
                                <input
                                    type="text"
                                    value={editingTask.title}
                                    onChange={(e) => setEditingTask({ ...editingTask, title: e.target.value })}
                                    required
                                />
                                <textarea
                                    value={editingTask.description}
                                    onChange={(e) => setEditingTask({ ...editingTask, description: e.target.value })}
                                />
                                <button type="submit">Save</button>
                                <button type="button" onClick={() => setEditingTask(null)}>Cancel</button>
                            </form>
                        ) : (
                            <>
                                <h3>{task.title}</h3>
                                <p>{task.description}</p>
                                <div className="task-actions">
                                    <button onClick={() => setEditingTask(task)}>Edit</button>
                                    <button onClick={() => deleteTask(task.id)}>Delete</button>
                                </div>

                                {/* Comments Section */}
                                <div className="comments-section">
                                    <h4>Comments</h4>
                                    <div className="add-comment">
                                        <input
                                            type="text"
                                            placeholder="Add a comment..."
                                            value={newComment}
                                            onChange={(e) => setNewComment(e.target.value)}
                                            onKeyPress={(e) => e.key === 'Enter' && addComment(task.id)}
                                        />
                                        <button onClick={() => addComment(task.id)}>Add Comment</button>
                                    </div>
                                    
                                    <div className="comments-list">
                                        {(comments[task.id] || []).map(comment => (
                                            <div key={comment.id} className="comment-item">
                                                <p>{comment.content}</p>
                                                <button 
                                                    onClick={() => deleteComment(comment.id, task.id)}
                                                    className="delete-comment"
                                                >
                                                    Delete
                                                </button>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default TaskList;