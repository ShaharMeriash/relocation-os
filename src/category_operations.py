"""
Database operations for Expense Categories
"""

from models import ExpenseCategory, get_engine, get_session


def create_expense_category(relocation_profile_id, name, description=None):
    """Create a new expense category"""
    engine = get_engine()
    session = get_session(engine)
    
    try:
        category = ExpenseCategory(
            relocation_profile_id=relocation_profile_id,
            name=name,
            description=description
        )
        
        session.add(category)
        session.commit()
        
        print(f"✓ Created category: {category.name}")
        
        category_id = category.id
        
    except Exception as e:
        session.rollback()
        print(f"✗ Error creating category: {e}")
        raise
    finally:
        session.close()
    
    return get_category_by_id(category_id)


def get_all_categories(relocation_profile_id=None):
    """Get all expense categories, optionally filtered by profile"""
    engine = get_engine()
    session = get_session(engine)
    
    try:
        query = session.query(ExpenseCategory)
        
        if relocation_profile_id:
            query = query.filter_by(relocation_profile_id=relocation_profile_id)
        
        categories = query.order_by(ExpenseCategory.name).all()
        
        result = []
        for cat in categories:
            _ = (cat.id, cat.name)
            result.append(cat)
        
        return result
    finally:
        session.close()


def get_category_by_id(category_id):
    """Get a specific category by ID"""
    engine = get_engine()
    session = get_session(engine)
    
    try:
        category = session.query(ExpenseCategory).filter_by(id=category_id).first()
        if category:
            _ = (category.id, category.name)
        return category
    finally:
        session.close()


def delete_expense_category(category_id):
    """Delete a category"""
    engine = get_engine()
    session = get_session(engine)
    
    try:
        category = session.query(ExpenseCategory).filter_by(id=category_id).first()
        
        if not category:
            print(f"❌ No category found with ID {category_id}")
            return False
        
        category_name = category.name
        
        session.delete(category)
        session.commit()
        
        print(f"✓ Deleted category: {category_name}")
        return True
        
    except Exception as e:
        session.rollback()
        print(f"✗ Error deleting category: {e}")
        raise
    finally:
        session.close()