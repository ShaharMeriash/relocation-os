"""
Database operations for Relocation OS
Functions to create, read, update, and delete data
"""

from datetime import date
from models import RelocationProfile, get_engine, get_session, init_database


def create_relocation_profile(
    relocation_name,
    origin_country,
    destination_country,
    target_arrival_date,
    family_size=1,
    number_of_children=0,
    pets=False,
    primary_currency='USD',
    secondary_currency=None,
    notes=None
):
    """
    Create a new relocation profile and save it to the database
    
    Args:
        relocation_name: Name for this relocation (e.g., "Moving to Portugal")
        origin_country: Where you're moving from
        destination_country: Where you're moving to
        target_arrival_date: When you plan to arrive (date object)
        family_size: Number of people relocating
        number_of_children: How many are children
        pets: True if bringing pets
        primary_currency: Main currency for budgeting (3-letter code)
        secondary_currency: Optional secondary currency
        notes: Any additional notes
    
    Returns:
        The created RelocationProfile object
    """
    # Get database connection
    engine = get_engine()
    session = get_session(engine)
    
    try:
        # Create new profile object
        profile = RelocationProfile(
            relocation_name=relocation_name,
            origin_country=origin_country,
            destination_country=destination_country,
            target_arrival_date=target_arrival_date,
            family_size=family_size,
            number_of_children=number_of_children,
            pets=pets,
            primary_currency=primary_currency,
            secondary_currency=secondary_currency,
            notes=notes
        )
        
        # Add to database
        session.add(profile)
        session.commit()  # Save changes
        
        print(f"✓ Created relocation profile: {profile.relocation_name}")
        print(f"  ID: {profile.id}")
        
        return profile
        
    except Exception as e:
        session.rollback()  # Undo changes if error
        print(f"✗ Error creating profile: {e}")
        raise
    finally:
        session.close()  # Always close the connection


def get_all_profiles():
    """
    Retrieve all relocation profiles from the database
    
    Returns:
        List of all RelocationProfile objects
    """
    engine = get_engine()
    session = get_session(engine)
    
    try:
        profiles = session.query(RelocationProfile).all()
        return profiles
    finally:
        session.close()


def get_profile_by_id(profile_id):
    """
    Get a specific relocation profile by its ID
    
    Args:
        profile_id: The ID of the profile to retrieve
    
    Returns:
        RelocationProfile object or None if not found
    """
    engine = get_engine()
    session = get_session(engine)
    
    try:
        profile = session.query(RelocationProfile).filter_by(id=profile_id).first()
        return profile
    finally:
        session.close()


def display_profile(profile):
    """
    Pretty print a relocation profile
    
    Args:
        profile: RelocationProfile object to display
    """
    if not profile:
        print("No profile found")
        return
    
    print("\n" + "=" * 60)
    print(f"RELOCATION PROFILE: {profile.relocation_name}")
    print("=" * 60)
    print(f"ID: {profile.id}")
    print(f"Route: {profile.origin_country} → {profile.destination_country}")
    print(f"Target Arrival: {profile.target_arrival_date}")
    print(f"Family Size: {profile.family_size} person(s)")
    print(f"Children: {profile.number_of_children}")
    print(f"Pets: {'Yes' if profile.pets else 'No'}")
    print(f"Primary Currency: {profile.primary_currency}")
    if profile.secondary_currency:
        print(f"Secondary Currency: {profile.secondary_currency}")
    if profile.notes:
        print(f"\nNotes: {profile.notes}")
    print("=" * 60 + "\n")