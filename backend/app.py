import os
import sys
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_cors import CORS

# Add both project root and backend directory to sys.path to allow imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
for p in (project_root, current_dir):
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from backend.models import db, Task, Comment
except ModuleNotFoundError:
    # Fallback when running as a script directly inside backend/
    from models import db, Task, Comment


def create_app():
    app = Flask(__name__)

    # Configuration
    # Use absolute path to ensure database is created in backend directory
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', f'sqlite:///{db_path}')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    Migrate(app, db)
    CORS(app)

    # Create tables
    with app.app_context():
        db.create_all()

    return app


app = create_app()


# Comment CRUD Routes
@app.route('/api/tasks/<int:task_id>/comments', methods=['GET'])
def get_comments(task_id):
    try:
        comments = Comment.query.filter_by(task_id=task_id).all()
        return jsonify([{
            'id': comment.id,
            'content': comment.content,
            'created_at': comment.created_at.isoformat(),
            'updated_at': comment.updated_at.isoformat(),
            'task_id': comment.task_id
        } for comment in comments])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/tasks/<int:task_id>/comments', methods=['POST'])
def create_comment(task_id):
    try:
        data = request.get_json()

        # Validate task exists
        task = Task.query.get(task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404

        if not data.get('content'):
            return jsonify({'error': 'Content is required'}), 400

        comment = Comment(
            content=data['content'],
            task_id=task_id
        )

        db.session.add(comment)
        db.session.commit()

        return jsonify({
            'id': comment.id,
            'content': comment.content,
            'created_at': comment.created_at.isoformat(),
            'updated_at': comment.updated_at.isoformat(),
            'task_id': comment.task_id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/comments/<int:comment_id>', methods=['PUT'])
def update_comment(comment_id):
    try:
        comment = Comment.query.get(comment_id)
        if not comment:
            return jsonify({'error': 'Comment not found'}), 404

        data = request.get_json()
        if not data.get('content'):
            return jsonify({'error': 'Content is required'}), 400

        comment.content = data['content']
        db.session.commit()

        return jsonify({
            'id': comment.id,
            'content': comment.content,
            'created_at': comment.created_at.isoformat(),
            'updated_at': comment.updated_at.isoformat(),
            'task_id': comment.task_id
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/comments/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    try:
        comment = Comment.query.get(comment_id)
        if not comment:
            return jsonify({'error': 'Comment not found'}), 404

        db.session.delete(comment)
        db.session.commit()

        return jsonify({'message': 'Comment deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# Task CRUD Routes
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    try:
        tasks = Task.query.all()
        return jsonify([{
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'created_at': task.created_at.isoformat(),
            'updated_at': task.updated_at.isoformat()
        } for task in tasks])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/tasks', methods=['POST'])
def create_task():
    try:
        data = request.get_json()

        if not data.get('title'):
            return jsonify({'error': 'Title is required'}), 400

        task = Task(
            title=data['title'],
            description=data.get('description', '')
        )

        db.session.add(task)
        db.session.commit()

        return jsonify({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'created_at': task.created_at.isoformat(),
            'updated_at': task.updated_at.isoformat()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    try:
        task = Task.query.get(task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404

        data = request.get_json()
        if not data.get('title'):
            return jsonify({'error': 'Title is required'}), 400

        task.title = data['title']
        task.description = data.get('description', task.description)
        db.session.commit()

        return jsonify({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'created_at': task.created_at.isoformat(),
            'updated_at': task.updated_at.isoformat()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    try:
        task = Task.query.get(task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404

        db.session.delete(task)
        db.session.commit()

        return jsonify({'message': 'Task deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Disable reloader so it stays attached to parent process
    app.run(debug=True, use_reloader=False)


