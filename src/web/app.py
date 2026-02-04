"""
Flask Web Application for Relocation OS
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import our modules
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime, date

# Import our existing operations
from database import (
    create_relocation_profile,
    get_all_profiles,
    get_profile_by_id,
    update_relocation_profile,
    delete_relocation_profile
)
from phase_operations import (
    create_phase,
    get_all_phases,
    get_phase_by_id,
    delete_phase
)
from task_operations import (
    create_task,
    get_all_tasks,
    get_task_by_id,
    update_task,
    delete_task,
    mark_task_completed
)
from expense_operations import (
    create_expense,
    get_all_expenses,
    get_expense_by_id,
    update_expense,
    delete_expense,
    mark_expense_paid,
    get_budget_summary
)
from category_operations import (
    create_expense_category,
    get_all_categories,
    delete_expense_category
)
from models import init_database

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'

# Initialize database on startup
with app.app_context():
    init_database()


@app.route('/')
def index():
    """Home page - Dashboard"""
    profiles = get_all_profiles()
    
    # Get summary data
    total_profiles = len(profiles)
    total_tasks = len(get_all_tasks())
    total_expenses = len(get_all_expenses())
    
    # Get incomplete tasks
    incomplete_tasks = [t for t in get_all_tasks() if t.status != 'completed']
    
    # Get unpaid expenses
    unpaid_expenses = get_all_expenses(payment_status='unpaid')
    
    return render_template('index.html',
                        profiles=profiles,
                        total_profiles=total_profiles,
                        total_tasks=total_tasks,
                        total_expenses=total_expenses,
                        incomplete_tasks=incomplete_tasks[:5],  # Show 5 most recent
                        unpaid_expenses=unpaid_expenses[:5])


@app.route('/profiles')
def profiles_list():
    """List all profiles"""
    profiles = get_all_profiles()
    return render_template('profiles_list.html', profiles=profiles)


@app.route('/profile/<int:profile_id>')
def profile_detail(profile_id):
    """View a single profile with all its data"""
    profile = get_profile_by_id(profile_id)
    if not profile:
        flash('Profile not found', 'error')
        return redirect(url_for('profiles_list'))
    
    phases = get_all_phases(relocation_profile_id=profile_id)
    tasks = get_all_tasks(relocation_profile_id=profile_id)
    expenses = get_all_expenses(relocation_profile_id=profile_id)
    budget_summary = get_budget_summary(profile_id)
    categories = get_all_categories(relocation_profile_id=profile_id)
    
    return render_template('profile_detail.html',
                        profile=profile,
                        phases=phases,
                        tasks=tasks,
                        expenses=expenses,
                        budget_summary=budget_summary,
                        categories=categories)
    
    return render_template('profile_detail.html',
                        profile=profile,
                        phases=phases,
                        tasks=tasks,
                        expenses=expenses,
                        budget_summary=budget_summary)


@app.route('/profile/create', methods=['GET', 'POST'])
def profile_create():
    """Create a new profile"""
    if request.method == 'POST':
        try:
            # Parse the date
            target_date = datetime.strptime(request.form['target_arrival_date'], '%Y-%m-%d').date()
            
            profile = create_relocation_profile(
                relocation_name=request.form['relocation_name'],
                origin_country=request.form['origin_country'],
                destination_country=request.form['destination_country'],
                target_arrival_date=target_date,
                family_size=int(request.form.get('family_size', 1)),
                number_of_children=int(request.form.get('number_of_children', 0)),
                pets=request.form.get('pets') == 'on',
                primary_currency=request.form.get('primary_currency', 'USD'),
                secondary_currency=request.form.get('secondary_currency') or None,
                notes=request.form.get('notes') or None
            )
            
            flash(f'Profile "{profile.relocation_name}" created successfully!', 'success')
            return redirect(url_for('profile_detail', profile_id=profile.id))
            
        except Exception as e:
            flash(f'Error creating profile: {str(e)}', 'error')
    
    return render_template('profile_form.html', profile=None)


@app.route('/profile/<int:profile_id>/delete', methods=['POST'])
def profile_delete(profile_id):
    """Delete a profile"""
    if delete_relocation_profile(profile_id):
        flash('Profile deleted successfully', 'success')
    else:
        flash('Error deleting profile', 'error')
    
    return redirect(url_for('profiles_list'))


@app.route('/tasks')
def tasks_list():
    """List all tasks"""
    status_filter = request.args.get('status')
    tasks = get_all_tasks(status=status_filter)
    
    return render_template('tasks_list.html', tasks=tasks, status_filter=status_filter)


@app.route('/task/<int:task_id>/complete', methods=['POST'])
def task_complete(task_id):
    """Mark task as completed"""
    mark_task_completed(task_id)
    flash('Task marked as completed!', 'success')
    
    # Redirect back to referring page or task list
    return redirect(request.referrer or url_for('tasks_list'))


@app.route('/task/<int:task_id>/delete', methods=['POST'])
def task_delete(task_id):
    """Delete a task"""
    if delete_task(task_id):
        flash('Task deleted successfully', 'success')
    else:
        flash('Error deleting task', 'error')
    
    return redirect(request.referrer or url_for('tasks_list'))


@app.route('/expenses')
def expenses_list():
    """List all expenses"""
    payment_filter = request.args.get('payment_status')
    expenses = get_all_expenses(payment_status=payment_filter)
    
    return render_template('expenses_list.html', expenses=expenses, payment_filter=payment_filter)


@app.route('/expense/<int:expense_id>/pay', methods=['POST'])
def expense_pay(expense_id):
    """Mark expense as paid"""
    mark_expense_paid(expense_id)
    flash('Expense marked as paid!', 'success')
    
    return redirect(request.referrer or url_for('expenses_list'))


@app.route('/expense/<int:expense_id>/delete', methods=['POST'])
def expense_delete(expense_id):
    """Delete an expense"""
    if delete_expense(expense_id):
        flash('Expense deleted successfully', 'success')
    else:
        flash('Error deleting expense', 'error')
    
    return redirect(request.referrer or url_for('expenses_list'))


# Template filters
@app.template_filter('currency')
def currency_filter(amount_cents, currency='USD'):
    """Format currency amount"""
    if amount_cents is None:
        return 'N/A'
    
    amount = amount_cents / 100
    symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'JPY': '¥',
        'CAD': 'C$',
        'AUD': 'A$',
    }
    
    symbol = symbols.get(currency, currency + ' ')
    return f"{symbol}{amount:,.2f}"


@app.template_filter('date_format')
def date_format_filter(date_obj):
    """Format date"""
    if not date_obj:
        return 'N/A'
    return date_obj.strftime('%b %d, %Y')

@app.route('/profile/<int:profile_id>/phase/create', methods=['GET', 'POST'])
def phase_create(profile_id):
    """Create a new phase for a profile"""
    profile = get_profile_by_id(profile_id)
    if not profile:
        flash('Profile not found', 'error')
        return redirect(url_for('profiles_list'))
    
    if request.method == 'POST':
        try:
            phase = create_phase(
                relocation_profile_id=profile_id,
                name=request.form['name'],
                relative_start_month=int(request.form['relative_start_month']),
                relative_end_month=int(request.form['relative_end_month']),
                order_index=int(request.form['order_index']),
                description=request.form.get('description') or None
            )
            
            flash(f'Phase "{phase.name}" created successfully!', 'success')
            return redirect(url_for('profile_detail', profile_id=profile_id))
            
        except Exception as e:
            flash(f'Error creating phase: {str(e)}', 'error')
    
    # Get existing phases to suggest next order_index
    existing_phases = get_all_phases(relocation_profile_id=profile_id)
    next_order = len(existing_phases) + 1
    
    return render_template('phase_form.html', profile=profile, next_order=next_order)


@app.route('/profile/<int:profile_id>/task/create', methods=['GET', 'POST'])
def task_create(profile_id):
    """Create a new task for a profile"""
    profile = get_profile_by_id(profile_id)
    if not profile:
        flash('Profile not found', 'error')
        return redirect(url_for('profiles_list'))
    
    phases = get_all_phases(relocation_profile_id=profile_id)
    if not phases:
        flash('Please create at least one phase first!', 'error')
        return redirect(url_for('profile_detail', profile_id=profile_id))
    
    if request.method == 'POST':
        try:
            # Parse planned date if provided
            planned_date = None
            if request.form.get('planned_date'):
                planned_date = datetime.strptime(request.form['planned_date'], '%Y-%m-%d').date()
            
            task = create_task(
                relocation_profile_id=profile_id,
                phase_id=int(request.form['phase_id']),
                title=request.form['title'],
                description=request.form.get('description') or None,
                status=request.form.get('status', 'not_started'),
                critical=request.form.get('critical') == 'on',
                planned_date=planned_date,
                notes=request.form.get('notes') or None
            )
            
            flash(f'Task "{task.title}" created successfully!', 'success')
            return redirect(url_for('profile_detail', profile_id=profile_id))
            
        except Exception as e:
            flash(f'Error creating task: {str(e)}', 'error')
    
    return render_template('task_form.html', profile=profile, phases=phases, task=None)


@app.route('/profile/<int:profile_id>/expense/create', methods=['GET', 'POST'])
def expense_create(profile_id):
    """Create a new expense for a profile"""
    profile = get_profile_by_id(profile_id)
    if not profile:
        flash('Profile not found', 'error')
        return redirect(url_for('profiles_list'))
    
    phases = get_all_phases(relocation_profile_id=profile_id)
    if not phases:
        flash('Please create at least one phase first!', 'error')
        return redirect(url_for('profile_detail', profile_id=profile_id))
    
    tasks = get_all_tasks(relocation_profile_id=profile_id)
    
    if request.method == 'POST':
        try:
            # Parse amounts (convert dollars to cents)
            estimated = float(request.form['estimated_amount']) * 100
            
            actual = None
            if request.form.get('actual_amount'):
                actual = float(request.form['actual_amount']) * 100
            
            # Parse due date if provided
            due_date = None
            if request.form.get('due_date'):
                due_date = datetime.strptime(request.form['due_date'], '%Y-%m-%d').date()
            
            # Get exchange rate if currency differs from profile
            currency = request.form.get('currency', profile.primary_currency)
            exchange_rate = None
            
            if currency != profile.primary_currency:
                from currency_service import get_exchange_rate
                exchange_rate = get_exchange_rate(currency, profile.primary_currency)
            
            # Related task (optional)
            related_task_id = request.form.get('related_task_id')
            if related_task_id:
                related_task_id = int(related_task_id)
            else:
                related_task_id = None
            
            expense = create_expense(
                relocation_profile_id=profile_id,
                phase_id=int(request.form['phase_id']),
                title=request.form['title'],
                category=request.form.get('category') or None,
                estimated_amount=int(estimated),
                actual_amount=int(actual) if actual else None,
                currency=currency,
                exchange_rate=exchange_rate,
                cost_certainty=request.form.get('cost_certainty', 'estimated'),
                payment_status=request.form.get('payment_status', 'unpaid'),
                include_in_budget=request.form.get('include_in_budget') == 'on',
                one_time_relocation_cost=request.form.get('one_time_relocation_cost') == 'on',
                due_date=due_date,
                related_task_id=related_task_id,
                notes=request.form.get('notes') or None
            )
            
            flash(f'Expense "{expense.title}" created successfully!', 'success')
            return redirect(url_for('profile_detail', profile_id=profile_id))
            
        except Exception as e:
            flash(f'Error creating expense: {str(e)}', 'error')
    
    return render_template('expense_form.html', profile=profile, phases=phases, tasks=tasks, expense=None)
@app.route('/profile/<int:profile_id>/category/create', methods=['GET', 'POST'])
def category_create(profile_id):
    """Create a new expense category"""
    profile = get_profile_by_id(profile_id)
    if not profile:
        flash('Profile not found', 'error')
        return redirect(url_for('profiles_list'))
    
    if request.method == 'POST':
        try:
            category = create_expense_category(
                relocation_profile_id=profile_id,
                name=request.form['name'],
                description=request.form.get('description') or None
            )
            
            flash(f'Category "{category.name}" created successfully!', 'success')
            return redirect(url_for('profile_detail', profile_id=profile_id))
            
        except Exception as e:
            flash(f'Error creating category: {str(e)}', 'error')
    
    return render_template('category_form.html', profile=profile)


@app.route('/category/<int:category_id>/delete', methods=['POST'])
def category_delete(category_id):
    """Delete a category"""
    if delete_expense_category(category_id):
        flash('Category deleted successfully', 'success')
    else:
        flash('Error deleting category', 'error')
    
    return redirect(request.referrer or url_for('index'))


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False') == 'True'
    app.run(host='0.0.0.0', port=port, debug=debug)