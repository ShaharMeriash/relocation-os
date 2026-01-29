"""
Database operations for Relocation Phases
"""

from models import RelocationPhase, get_engine, get_session
from database import get_profile_by_id


def create_phase(relocation_profile_id, name, relative_start_month, relative_end_month, 
                 order_index, description=None):
    """
    Create a new relocation phase
    
    Args:
        relocation_profile_id: ID of the profile this phase belongs to
        name: Name of the phase
        relative_start_month: Start month relative to arrival (negative = before)
        relative_end_month: End month relative to arrival
        order_index: Sort order for this phase
        description: Optional description of what happens in this phase
    
    Returns:
        The created RelocationPhase object
    """
    engine = get_engine()
    session = get_session(engine)
    
    try:
        # Verify the profile exists
        profile = session.query(RelocationPhase).filter_by(id=relocation_profile_id).first()
        # Note: We're not using get_profile_by_id here because it closes its own session
        
        phase = RelocationPhase(
            relocation_profile_id=relocation_profile_id,
            name=name,
            relative_start_month=relative_start_month,
            relative_end_month=relative_end_month,
            order_index=order_index,
            description=description
        )
        
        session.add(phase)
        session.commit()
        
        print(f"✓ Created phase: {phase.name}")
        print(f"  ID: {phase.id}")
        
        phase_id = phase.id
        
    except Exception as e:
        session.rollback()
        print(f"✗ Error creating phase: {e}")
        raise
    finally:
        session.close()
    
    return get_phase_by_id(phase_id)


def get_all_phases(relocation_profile_id=None):
    """
    Get all phases, optionally filtered by profile
    
    Args:
        relocation_profile_id: Optional - only get phases for this profile
    
    Returns:
        List of RelocationPhase objects, sorted by order_index
    """
    engine = get_engine()
    session = get_session(engine)
    
    try:
        query = session.query(RelocationPhase)
        
        if relocation_profile_id:
            query = query.filter_by(relocation_profile_id=relocation_profile_id)
        
        phases = query.order_by(RelocationPhase.order_index).all()
        
        # Load the data while session is open
        result = []
        for phase in phases:
            # Access attributes to load them
            _ = (phase.id, phase.name, phase.relocation_profile_id)
            result.append(phase)
        
        return result
    finally:
        session.close()


def get_phase_by_id(phase_id):
    """Get a specific phase by ID"""
    engine = get_engine()
    session = get_session(engine)
    
    try:
        phase = session.query(RelocationPhase).filter_by(id=phase_id).first()
        if phase:
            # Load attributes before session closes
            _ = (phase.id, phase.name, phase.relocation_profile_id)
        return phase
    finally:
        session.close()


def update_phase(phase_id, **kwargs):
    """Update an existing phase"""
    engine = get_engine()
    session = get_session(engine)
    
    try:
        phase = session.query(RelocationPhase).filter_by(id=phase_id).first()
        
        if not phase:
            print(f"❌ No phase found with ID {phase_id}")
            return None
        
        for key, value in kwargs.items():
            if hasattr(phase, key):
                setattr(phase, key, value)
                print(f"  ✓ Updated {key}")
            else:
                print(f"  ⚠️  Unknown field: {key}")
        
        session.commit()
        print(f"\n✓ Phase {phase_id} updated successfully!")
        
        phase_id_copy = phase.id
        
    except Exception as e:
        session.rollback()
        print(f"✗ Error updating phase: {e}")
        raise
    finally:
        session.close()
    
    return get_phase_by_id(phase_id_copy)


def delete_phase(phase_id):
    """Delete a phase"""
    engine = get_engine()
    session = get_session(engine)
    
    try:
        phase = session.query(RelocationPhase).filter_by(id=phase_id).first()
        
        if not phase:
            print(f"❌ No phase found with ID {phase_id}")
            return False
        
        phase_name = phase.name
        
        session.delete(phase)
        session.commit()
        
        print(f"✓ Deleted phase: {phase_name} (ID: {phase_id})")
        return True
        
    except Exception as e:
        session.rollback()
        print(f"✗ Error deleting phase: {e}")
        raise
    finally:
        session.close()


def display_phase(phase):
    """Pretty print a phase"""
    if not phase:
        print("No phase found")
        return
    
    print("\n" + "-" * 50)
    print(f"PHASE: {phase.name}")
    print("-" * 50)
    print(f"ID: {phase.id}")
    print(f"Timeline: Month {phase.relative_start_month} to {phase.relative_end_month}")
    print(f"Order: {phase.order_index}")
    if phase.description:
        print(f"Description: {phase.description}")
    print(f"Profile ID: {phase.relocation_profile_id}")
    print("-" * 50 + "\n")