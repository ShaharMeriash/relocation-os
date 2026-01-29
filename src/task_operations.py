"""
Database operations for Tasks
"""

from datetime import date
from models import Task, get_engine, get_session
from database import get_profile_by_id
from phase_operations import get_phase_by_id


def create_task(relocation_profile_id, phase_id, title, description=None, 
                status='not_started', critical=False, planned_date=None, notes=None):
    """
    Create a new task
    
    Args:
        relocation_profile_id: ID of the profile this task belongs to
        phase_id: ID of the phase this task belongs to
        title: Task title
        description: Optional detailed description
        status: not_started, in_progress, or completed
        critical: Is this task critical/important?
        planned_date: When you plan to do this task
        notes: Additional notes
    
    Returns:
        The created Task object
    """
    engine = get_engine()
    session = get_session(engine)
    
    try:
        task = Task(
            relocation_profile_id=relocation_profile_id,
            phase_id=phase_id,
            title=title,
            description=description,
            status=status,
            critical=critical,
            planned_date=planned_date,
            notes=notes
        )
        
        session.add(task)
        session.commit()
        
        print(f"✓ Created task: {task.title}")
        print(f"  ID: {task.id}")
        
        task_id = task.id
        
    except Exception as e:
        session.rollback()
        print(f"✗ Error creating task: {e}")
        raise
    finally:
        session.close()
    
    return get_task_by_id(task_id)


def get_all_tasks(relocation_profile_id=None, phase_id=None, status=None):
    """
    Get all tasks, optionally filtered
    
    Args:
        relocation_profile_id: Filter by profile
        phase_id: Filter by phase
        status: Filter by status (not_started, in_progress, completed)
    
    Returns:
        List of Task objects
    """
    engine = get_engine()
    session = get_session(engine)
    
    try:
        query = session.query(Task)
        
        if relocation_profile_id:
            query = query.filter_by(relocation_profile_id=relocation_profile_id)
        
        if phase_id:
            query = query.filter_by(phase_id=phase_id)
        
        if status:
            query = query.filter_by(status=status)
        
        # Order by: critical first, then by planned date
        tasks = query.order_by(Task.critical.desc(), Task.planned_date).all()
        
        # Load data while session is open
        result = []
        for task in tasks:
            _ = (task.id, task.title, task.status)
            result.append(task)
        
        return result
    finally:
        session.close()


def get_task_by_id(task_id):
    """Get a specific task by ID"""
    engine = get_engine()
    session = get_session(engine)
    
    try:
        task = session.query(Task).filter_by(id=task_id).first()
        if task:
            _ = (task.id, task.title, task.status)
        return task
    finally:
        session.close()


def update_task(task_id, **kwargs):
    """Update an existing task"""
    engine = get_engine()
    session = get_session(engine)
    
    try:
        task = session.query(Task).filter_by(id=task_id).first()
        
        if not task:
            print(f"❌ No task found with ID {task_id}")
            return None
        
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)
                print(f"  ✓ Updated {key}")
            else:
                print(f"  ⚠️  Unknown field: {key}")
        
        session.commit()
        print(f"\n✓ Task {task_id} updated successfully!")
        
        task_id_copy = task.id
        
    except Exception as e:
        session.rollback()
        print(f"✗ Error updating task: {e}")
        raise
    finally:
        session.close()
    
    return get_task_by_id(task_id_copy)


def delete_task(task_id):
    """Delete a task"""
    engine = get_engine()
    session = get_session(engine)
    
    try:
        task = session.query(Task).filter_by(id=task_id).first()
        
        if not task:
            print(f"❌ No task found with ID {task_id}")
            return False
        
        task_title = task.title
        
        session.delete(task)
        session.commit()
        
        print(f"✓ Deleted task: {task_title} (ID: {task_id})")
        return True
        
    except Exception as e:
        session.rollback()
        print(f"✗ Error deleting task: {e}")
        raise
    finally:
        session.close()


def mark_task_completed(task_id, completed_date=None):
    """
    Mark a task as completed
    
    Args:
        task_id: ID of the task
        completed_date: Date completed (defaults to today)
    
    Returns:
        Updated Task object
    """
    if completed_date is None:
        completed_date = date.today()
    
    return update_task(task_id, status='completed', completed_date=completed_date)


def display_task(task):
    """Pretty print a task"""
    if not task:
        print("No task found")
        return
    
    # Status emoji
    status_emoji = {
        'not_started': '⏸️',
        'in_progress': '🔄',
        'completed': '✅'
    }
    
    emoji = status_emoji.get(task.status, '❓')
    critical_mark = "🔴 CRITICAL" if task.critical else ""
    
    print("\n" + "-" * 50)
    print(f"{emoji} {task.title} {critical_mark}")
    print("-" * 50)
    print(f"ID: {task.id}")
    print(f"Status: {task.status.replace('_', ' ').title()}")
    
    if task.description:
        print(f"Description: {task.description}")
    
    if task.planned_date:
        print(f"Planned Date: {task.planned_date}")
    
    if task.completed_date:
        print(f"Completed Date: {task.completed_date}")
    
    print(f"Phase ID: {task.phase_id}")
    print(f"Profile ID: {task.relocation_profile_id}")
    
    if task.notes:
        print(f"Notes: {task.notes}")
    
    print("-" * 50 + "\n")