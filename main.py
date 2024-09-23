from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# Configure the SQLite database
basedir=os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(basedir,'todo.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY']="star/cloud/0821"
db = SQLAlchemy(app)


# Task model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    due_date = db.Column(db.DateTime, nullable=True)
    complete = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Initialize the database
with app.app_context():
    db.create_all()

# Route to display tasks
@app.route('/')
def index():
    tasks = Task.query.order_by(Task.created_at).all()
    return render_template('index.html', tasks=tasks)

# Route to add or update a task
@app.route('/add_or_update', methods=['POST'])
def add_or_update_task():
    task_id = request.form.get('task_id')
    task_title = request.form.get('title')
    task_due_date = request.form.get('due_date')

    
     # Convert due_date to datetime object
    try:
        due_date = datetime.strptime(task_due_date, '%Y-%m-%dT%H:%M')
    except ValueError:
        flash("Invalid date format. Please use the correct date and time format.")
        return redirect(url_for('index'))

    # Check if the due date is today or in the future
    if due_date < datetime.now():
        flash("Cannot add a task with a past due date.")
        return redirect(url_for('index'))

    if task_id:  # If task_id is present, update the task
        task = Task.query.get(task_id)
        task.title = task_title
        task.due_date = due_date

    else:  # Otherwise, create a new task
        new_task = Task(title=task_title, due_date=due_date)
        db.session.add(new_task)
    
    
    db.session.commit()
    return redirect(url_for('index'))

# Route to toggle task completion status
@app.route('/toggle/<int:task_id>')
def toggle_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.complete = not task.complete
    db.session.commit()
    return redirect(url_for('index'))

# Route to delete a task
@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    task_to_delete = Task.query.get_or_404(task_id)
    db.session.delete(task_to_delete)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)