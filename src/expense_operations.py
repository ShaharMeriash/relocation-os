"""
Database operations for Expenses
"""

from datetime import date
from models import Expense, get_engine, get_session


def create_expense(relocation_profile_id, phase_id, title, category=None,
                   estimated_amount=0, actual_amount=None, currency='USD',
                   exchange_rate=None, cost_certainty='estimated',
                   payment_status='unpaid', include_in_budget=True,
                   one_time_relocation_cost=True, due_date=None,
                   related_task_id=None, notes=None):
    """
    Create a new expense
    
    Args:
        relocation_profile_id: ID of the profile
        phase_id: ID of the phase
        title: Expense title
        category: Category (e.g., "Housing", "Transportation")
        estimated_amount: Estimated cost in cents (e.g., 12345 for $123.45)
        actual_amount: Actual cost in cents
        currency: 3-letter currency code
        exchange_rate: Exchange rate to primary currency (in cents, e.g., 9200 for 0.92)
        cost_certainty: unknown, estimated, or confirmed
        payment_status: unpaid or paid
        include_in_budget: Include in budget calculations
        one_time_relocation_cost: Is this a one-time cost?
        due_date: Payment due date
        related_task_id: Optional link to a task
        notes: Additional notes
    
    Returns:
        The created Expense object
    """
    engine = get_engine()
    session = get_session(engine)
    
    try:
        expense = Expense(
            relocation_profile_id=relocation_profile_id,
            phase_id=phase_id,
            title=title,
            category=category,
            estimated_amount=estimated_amount,
            actual_amount=actual_amount,
            currency=currency,
            exchange_rate=exchange_rate,
            cost_certainty=cost_certainty,
            payment_status=payment_status,
            include_in_budget=include_in_budget,
            one_time_relocation_cost=one_time_relocation_cost,
            due_date=due_date,
            related_task_id=related_task_id,
            notes=notes
        )
        
        session.add(expense)
        session.commit()
        
        amount_display = estimated_amount / 100
        print(f"✓ Created expense: {expense.title}")
        print(f"  ID: {expense.id}")
        print(f"  Amount: {amount_display:.2f} {currency}")
        
        expense_id = expense.id
        
    except Exception as e:
        session.rollback()
        print(f"✗ Error creating expense: {e}")
        raise
    finally:
        session.close()
    
    return get_expense_by_id(expense_id)


def get_all_expenses(relocation_profile_id=None, phase_id=None, 
                     payment_status=None, cost_certainty=None):
    """
    Get all expenses, optionally filtered
    
    Args:
        relocation_profile_id: Filter by profile
        phase_id: Filter by phase
        payment_status: Filter by payment status
        cost_certainty: Filter by cost certainty
    
    Returns:
        List of Expense objects
    """
    engine = get_engine()
    session = get_session(engine)
    
    try:
        query = session.query(Expense)
        
        if relocation_profile_id:
            query = query.filter_by(relocation_profile_id=relocation_profile_id)
        
        if phase_id:
            query = query.filter_by(phase_id=phase_id)
        
        if payment_status:
            query = query.filter_by(payment_status=payment_status)
        
        if cost_certainty:
            query = query.filter_by(cost_certainty=cost_certainty)
        
        expenses = query.order_by(Expense.due_date, Expense.title).all()
        
        # Load data while session is open
        result = []
        for expense in expenses:
            _ = (expense.id, expense.title, expense.currency)
            result.append(expense)
        
        return result
    finally:
        session.close()


def get_expense_by_id(expense_id):
    """Get a specific expense by ID"""
    engine = get_engine()
    session = get_session(engine)
    
    try:
        expense = session.query(Expense).filter_by(id=expense_id).first()
        if expense:
            _ = (expense.id, expense.title, expense.currency)
        return expense
    finally:
        session.close()


def update_expense(expense_id, **kwargs):
    """Update an existing expense"""
    engine = get_engine()
    session = get_session(engine)
    
    try:
        expense = session.query(Expense).filter_by(id=expense_id).first()
        
        if not expense:
            print(f"❌ No expense found with ID {expense_id}")
            return None
        
        for key, value in kwargs.items():
            if hasattr(expense, key):
                setattr(expense, key, value)
                print(f"  ✓ Updated {key}")
            else:
                print(f"  ⚠️  Unknown field: {key}")
        
        session.commit()
        print(f"\n✓ Expense {expense_id} updated successfully!")
        
        expense_id_copy = expense.id
        
    except Exception as e:
        session.rollback()
        print(f"✗ Error updating expense: {e}")
        raise
    finally:
        session.close()
    
    return get_expense_by_id(expense_id_copy)


def delete_expense(expense_id):
    """Delete an expense"""
    engine = get_engine()
    session = get_session(engine)
    
    try:
        expense = session.query(Expense).filter_by(id=expense_id).first()
        
        if not expense:
            print(f"❌ No expense found with ID {expense_id}")
            return False
        
        expense_title = expense.title
        
        session.delete(expense)
        session.commit()
        
        print(f"✓ Deleted expense: {expense_title} (ID: {expense_id})")
        return True
        
    except Exception as e:
        session.rollback()
        print(f"✗ Error deleting expense: {e}")
        raise
    finally:
        session.close()


def mark_expense_paid(expense_id):
    """Mark an expense as paid"""
    return update_expense(expense_id, payment_status='paid')


def display_budget_summary(summary):
    """Pretty print budget summary"""
    print("\n" + "=" * 60)
    print("BUDGET SUMMARY")
    print("=" * 60)
    print(f"Total Estimated: ${summary['total_estimated']:,.2f}")
    if summary['total_actual'] > 0:
        print(f"Total Actual: ${summary['total_actual']:,.2f}")
    print(f"Total Paid: ${summary['total_paid']:,.2f}")
    print(f"Remaining: ${summary['remaining']:,.2f}")
    print(f"Budget Progress: {summary['budget_progress_pct']:.1f}%")
    print(f"Total Expenses: {summary['total_expenses']}")
    
    # Warnings
    if summary['overdue_count'] > 0:
        print(f"\n⚠️  {summary['overdue_count']} overdue unpaid expense(s)")
    if summary['unknown_count'] > 0:
        print(f"⚠️  {summary['unknown_count']} expense(s) with unknown cost")
    if summary['over_budget_count'] > 0:
        print(f"⚠️  {summary['over_budget_count']} over-budget expense(s)")
    
    print("=" * 60 + "\n")
def get_budget_summary(relocation_profile_id):
    """
    Get budget summary for a profile
    
    Returns:
        Dictionary with budget statistics
    """
    expenses = get_all_expenses(relocation_profile_id=relocation_profile_id)
    
    # Filter to only expenses included in budget
    budget_expenses = [e for e in expenses if e.include_in_budget]
    
    total_estimated = sum(e.estimated_amount for e in budget_expenses) / 100
    total_actual = sum(e.actual_amount for e in budget_expenses if e.actual_amount) / 100
    total_paid = sum(
        (e.actual_amount if e.actual_amount else e.estimated_amount) 
        for e in budget_expenses if e.payment_status == 'paid'
    ) / 100
    
    remaining = total_estimated - total_paid
    
    # Count issues
    overdue_count = sum(1 for e in budget_expenses if e.is_overdue)
    unknown_count = sum(1 for e in budget_expenses if e.cost_certainty == 'unknown')
    over_budget_count = sum(
        1 for e in budget_expenses 
        if e.variance and e.variance > 0
    )
    
    return {
        'total_estimated': total_estimated,
        'total_actual': total_actual,
        'total_paid': total_paid,
        'remaining': remaining,
        'budget_progress_pct': (total_paid / total_estimated * 100) if total_estimated > 0 else 0,
        'overdue_count': overdue_count,
        'unknown_count': unknown_count,
        'over_budget_count': over_budget_count,
        'total_expenses': len(budget_expenses)
    }
def display_expense(expense):
    """Pretty print an expense"""
    if not expense:
        print("No expense found")
        return
    
    # Payment status emoji
    status_emoji = {
        'unpaid': '💰',
        'paid': '✅'
    }
    
    emoji = status_emoji.get(expense.payment_status, '❓')
    
    # Check if overdue
    overdue_flag = " ⚠️ OVERDUE" if expense.is_overdue else ""
    
    print("\n" + "-" * 60)
    print(f"{emoji} {expense.title}{overdue_flag}")
    print("-" * 60)
    print(f"ID: {expense.id}")
    
    if expense.category:
        print(f"Category: {expense.category}")
    
    # Amounts
    est_display = expense.estimated_amount / 100
    print(f"Estimated: {est_display:.2f} {expense.currency}")
    
    if expense.actual_amount:
        act_display = expense.actual_amount / 100
        print(f"Actual: {act_display:.2f} {expense.currency}")
        
        if expense.variance:
            var_display = expense.variance
            var_symbol = "+" if var_display > 0 else ""
            print(f"Variance: {var_symbol}{var_display:.2f} {expense.currency}")
    
    # Status
    print(f"Cost Certainty: {expense.cost_certainty.title()}")
    print(f"Payment Status: {expense.payment_status.title()}")
    
    # Dates
    if expense.due_date:
        print(f"Due Date: {expense.due_date}")
    
    # Budget flags
    print(f"Include in Budget: {'Yes' if expense.include_in_budget else 'No'}")
    print(f"One-time Cost: {'Yes' if expense.one_time_relocation_cost else 'No'}")
    
    # References
    print(f"Phase ID: {expense.phase_id}")
    if expense.related_task_id:
        print(f"Related Task ID: {expense.related_task_id}")
    
    if expense.notes:
        print(f"Notes: {expense.notes}")
    
    print("-" * 60 + "\n")