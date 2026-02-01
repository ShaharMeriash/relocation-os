"""
Interactive menu system for Relocation OS
Handles user input and navigation
"""

from datetime import datetime
from database import (
    create_relocation_profile, 
    get_all_profiles, 
    get_profile_by_id,
    display_profile,
    update_relocation_profile,
    delete_relocation_profile
)
from phase_operations import (
    create_phase,
    get_all_phases,
    get_phase_by_id,
    update_phase,
    delete_phase,
    display_phase
)
from task_operations import (
    create_task,
    get_all_tasks,
    get_task_by_id,
    update_task,
    delete_task,
    mark_task_completed,
    display_task
)
from expense_operations import (
    create_expense,
    get_all_expenses,
    get_expense_by_id,
    update_expense,
    delete_expense,
    mark_expense_paid,
    get_budget_summary,
    display_expense,
    display_budget_summary
)
from currency_service import get_exchange_rate, get_manual_exchange_rate, format_currency

def clear_screen():
    """Clear the terminal screen"""
    print("\n" * 50)  # Simple way to "clear" by printing blank lines


def print_header(title):
    """Print a nice header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def get_date_input(prompt):
    """
    Get a date from the user
    
    Args:
        prompt: The message to show the user
    
    Returns:
        date object or None if invalid
    """
    print(prompt)
    print("Format: YYYY-MM-DD (e.g., 2026-06-15)")
    date_str = input("Enter date: ").strip()
    
    try:
        # Parse the date string
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        return date_obj
    except ValueError:
        print("❌ Invalid date format. Please use YYYY-MM-DD")
        return None


def get_yes_no_input(prompt):
    """
    Get a yes/no answer from the user
    
    Args:
        prompt: The question to ask
    
    Returns:
        True for yes, False for no
    """
    while True:
        answer = input(f"{prompt} (y/n): ").strip().lower()
        if answer in ['y', 'yes']:
            return True
        elif answer in ['n', 'no']:
            return False
        else:
            print("Please enter 'y' or 'n'")
def get_currency_amount(prompt):
    """
    Get a currency amount from user and convert to cents
    
    Args:
        prompt: The message to show the user
    
    Returns:
        Amount in cents (integer) or None if invalid
    """
    try:
        amount_str = input(f"{prompt} (e.g., 123.45): ").strip()
        if not amount_str:
            return None
        
        # Convert to float, then to cents
        amount_float = float(amount_str)
        amount_cents = int(amount_float * 100)
        
        return amount_cents
    except ValueError:
        print("❌ Invalid amount format")
        return None

def menu_create_profile():
    """Interactive form to create a new relocation profile"""
    print_header("Create New Relocation Profile")
    
    # Get basic information
    relocation_name = input("Relocation name (e.g., 'Moving to Portugal'): ").strip()
    if not relocation_name:
        print("❌ Relocation name is required!")
        return
    
    origin_country = input("Origin country: ").strip()
    if not origin_country:
        print("❌ Origin country is required!")
        return
    
    destination_country = input("Destination country: ").strip()
    if not destination_country:
        print("❌ Destination country is required!")
        return
    
    # Get target arrival date
    target_date = None
    while not target_date:
        target_date = get_date_input("\nTarget arrival date:")
    
    # Get family details
    print("\nFamily Details:")
    try:
        family_size = int(input("Family size (number of people): ").strip() or "1")
        number_of_children = int(input("Number of children: ").strip() or "0")
    except ValueError:
        print("❌ Please enter valid numbers!")
        return
    
    pets = get_yes_no_input("Do you have pets?")
    
    # Get currency settings
    print("\nCurrency Settings:")
    primary_currency = input("Primary currency (3-letter code, e.g., USD, EUR): ").strip().upper() or "USD"
    secondary_currency = input("Secondary currency (optional, press Enter to skip): ").strip().upper()
    if not secondary_currency:
        secondary_currency = None
    
    # Get notes
    print("\nAdditional Information:")
    notes = input("Notes (optional): ").strip()
    if not notes:
        notes = None
    
    # Confirm before creating
    print("\n" + "-" * 60)
    print("REVIEW YOUR INFORMATION:")
    print(f"  Name: {relocation_name}")
    print(f"  Route: {origin_country} → {destination_country}")
    print(f"  Target Arrival: {target_date}")
    print(f"  Family Size: {family_size} ({number_of_children} children)")
    print(f"  Pets: {'Yes' if pets else 'No'}")
    print(f"  Primary Currency: {primary_currency}")
    if secondary_currency:
        print(f"  Secondary Currency: {secondary_currency}")
    if notes:
        print(f"  Notes: {notes}")
    print("-" * 60)
    
    if not get_yes_no_input("\nCreate this profile?"):
        print("❌ Profile creation cancelled")
        return
    
    # Create the profile
    try:
        profile = create_relocation_profile(
            relocation_name=relocation_name,
            origin_country=origin_country,
            destination_country=destination_country,
            target_arrival_date=target_date,
            family_size=family_size,
            number_of_children=number_of_children,
            pets=pets,
            primary_currency=primary_currency,
            secondary_currency=secondary_currency,
            notes=notes
        )
        print("\n✅ Profile created successfully!")
        display_profile(profile)
    except Exception as e:
        print(f"\n❌ Error creating profile: {e}")


def menu_view_all_profiles():
    """Display all relocation profiles"""
    print_header("All Relocation Profiles")
    
    profiles = get_all_profiles()
    
    if not profiles:
        print("No profiles found. Create one first!")
        return
    
    print(f"Total profiles: {len(profiles)}\n")
    
    for profile in profiles:
        display_profile(profile)


def menu_view_profile_by_id():
    """View a specific profile by ID"""
    print_header("View Profile by ID")
    
    try:
        profile_id = int(input("Enter profile ID: ").strip())
        profile = get_profile_by_id(profile_id)
        
        if profile:
            display_profile(profile)
        else:
            print(f"❌ No profile found with ID {profile_id}")
    except ValueError:
        print("❌ Please enter a valid number")
def menu_update_profile():
    """Update an existing profile"""
    print_header("Update Relocation Profile")
    
    # First, show all profiles so user knows the IDs
    profiles = get_all_profiles()
    if not profiles:
        print("No profiles found. Create one first!")
        return
    
    print("Available profiles:")
    for p in profiles:
        print(f"  ID {p.id}: {p.relocation_name} ({p.origin_country} → {p.destination_country})")
    
    print()
    
    # Get profile ID to update
    try:
        profile_id = int(input("Enter profile ID to update: ").strip())
    except ValueError:
        print("❌ Please enter a valid number")
        return
    
    # Check if profile exists
    profile = get_profile_by_id(profile_id)
    if not profile:
        print(f"❌ No profile found with ID {profile_id}")
        return
    
    # Show current profile
    print("\nCurrent profile:")
    display_profile(profile)
    
    # Ask what to update
    print("What would you like to update? (Press Enter to skip a field)")
    print("-" * 60)
    
    updates = {}
    
    # Relocation name
    new_name = input(f"Relocation name [{profile.relocation_name}]: ").strip()
    if new_name:
        updates['relocation_name'] = new_name
    
    # Origin country
    new_origin = input(f"Origin country [{profile.origin_country}]: ").strip()
    if new_origin:
        updates['origin_country'] = new_origin
    
    # Destination country
    new_dest = input(f"Destination country [{profile.destination_country}]: ").strip()
    if new_dest:
        updates['destination_country'] = new_dest
    
    # Target date
    print(f"Target arrival date [{profile.target_arrival_date}]")
    new_date = get_date_input("Enter new date or press Enter to skip:")
    if new_date:
        updates['target_arrival_date'] = new_date
    
    # Family size
    new_family = input(f"Family size [{profile.family_size}]: ").strip()
    if new_family:
        try:
            updates['family_size'] = int(new_family)
        except ValueError:
            print("⚠️  Invalid number for family size, skipping")
    
    # Children
    new_children = input(f"Number of children [{profile.number_of_children}]: ").strip()
    if new_children:
        try:
            updates['number_of_children'] = int(new_children)
        except ValueError:
            print("⚠️  Invalid number for children, skipping")
    
    # Pets
    current_pets = "Yes" if profile.pets else "No"
    if get_yes_no_input(f"Update pets? (currently: {current_pets})"):
        updates['pets'] = get_yes_no_input("Do you have pets?")
    
    # Primary currency
    new_currency = input(f"Primary currency [{profile.primary_currency}]: ").strip().upper()
    if new_currency:
        updates['primary_currency'] = new_currency
    
    # Secondary currency
    current_secondary = profile.secondary_currency or "None"
    new_secondary = input(f"Secondary currency [{current_secondary}]: ").strip().upper()
    if new_secondary:
        updates['secondary_currency'] = new_secondary if new_secondary != "NONE" else None
    
    # Notes
    print(f"Current notes: {profile.notes or 'None'}")
    if get_yes_no_input("Update notes?"):
        new_notes = input("Enter new notes: ").strip()
        updates['notes'] = new_notes if new_notes else None
    
    # Check if any updates were made
    if not updates:
        print("\n⚠️  No changes made")
        return
    
    # Confirm updates
    print("\n" + "-" * 60)
    print("FIELDS TO UPDATE:")
    for key, value in updates.items():
        print(f"  {key}: {value}")
    print("-" * 60)
    
    if not get_yes_no_input("\nApply these updates?"):
        print("❌ Update cancelled")
        return
    
    # Apply updates
    updated_profile = update_relocation_profile(profile_id, **updates)
    
    if updated_profile:
        print("\n✅ Profile updated successfully!")
        display_profile(updated_profile)


def menu_delete_profile():
    """Delete a profile"""
    print_header("Delete Relocation Profile")
    
    # Show all profiles
    profiles = get_all_profiles()
    if not profiles:
        print("No profiles found.")
        return
    
    print("Available profiles:")
    for p in profiles:
        print(f"  ID {p.id}: {p.relocation_name} ({p.origin_country} → {p.destination_country})")
    
    print()
    
    # Get profile ID to delete
    try:
        profile_id = int(input("Enter profile ID to delete: ").strip())
    except ValueError:
        print("❌ Please enter a valid number")
        return
    
    # Get and show the profile
    profile = get_profile_by_id(profile_id)
    if not profile:
        print(f"❌ No profile found with ID {profile_id}")
        return
    
    print("\nProfile to delete:")
    display_profile(profile)
    
    # Confirm deletion
    print("⚠️  WARNING: This cannot be undone!")
    if not get_yes_no_input("Are you sure you want to delete this profile?"):
        print("❌ Deletion cancelled")
        return
    
    # Double confirmation
    if not get_yes_no_input("Really delete? This is your last chance!"):
        print("❌ Deletion cancelled")
        return
    
    # Delete it
    if delete_relocation_profile(profile_id):
        print("\n✅ Profile deleted successfully")
    else:
        print("\n❌ Failed to delete profile")
def menu_create_phase():
    """Create a new phase for a relocation profile"""
    print_header("Create New Relocation Phase")
    
    # First, show all profiles so user can choose
    profiles = get_all_profiles()
    if not profiles:
        print("❌ No profiles found. Create a profile first!")
        return
    
    print("Available profiles:")
    for p in profiles:
        print(f"  ID {p.id}: {p.relocation_name}")
    
    print()
    
    # Get profile ID
    try:
        profile_id = int(input("Enter profile ID for this phase: ").strip())
    except ValueError:
        print("❌ Please enter a valid number")
        return
    
    # Verify profile exists
    profile = get_profile_by_id(profile_id)
    if not profile:
        print(f"❌ No profile found with ID {profile_id}")
        return
    
    print(f"\nCreating phase for: {profile.relocation_name}")
    print("-" * 60)
    
    # Get phase details
    name = input("Phase name (e.g., 'Pre-departure Planning'): ").strip()
    if not name:
        print("❌ Phase name is required!")
        return
    
    print("\nTimeline (in months relative to target arrival date):")
    print("  Example: -6 means 6 months before arrival")
    print("  Example: 0 means the arrival month")
    print("  Example: 3 means 3 months after arrival")
    
    try:
        start_month = int(input("Start month: ").strip())
        end_month = int(input("End month: ").strip())
        
        if start_month >= end_month:
            print("❌ Start month must be before end month!")
            return
        
        order_index = int(input("Order index (for sorting, e.g., 1, 2, 3...): ").strip())
        
    except ValueError:
        print("❌ Please enter valid numbers!")
        return
    
    description = input("Description (optional): ").strip()
    if not description:
        description = None
    
    # Confirm
    print("\n" + "-" * 60)
    print("REVIEW PHASE:")
    print(f"  Name: {name}")
    print(f"  Timeline: Month {start_month} to {end_month}")
    print(f"  Order: {order_index}")
    if description:
        print(f"  Description: {description}")
    print("-" * 60)
    
    if not get_yes_no_input("\nCreate this phase?"):
        print("❌ Phase creation cancelled")
        return
    
    # Create the phase
    try:
        phase = create_phase(
            relocation_profile_id=profile_id,
            name=name,
            relative_start_month=start_month,
            relative_end_month=end_month,
            order_index=order_index,
            description=description
        )
        print("\n✅ Phase created successfully!")
        display_phase(phase)
    except Exception as e:
        print(f"\n❌ Error creating phase: {e}")


def menu_view_all_phases():
    """View all phases, optionally filtered by profile"""
    print_header("View Relocation Phases")
    
    # Ask if they want to filter by profile
    if get_yes_no_input("Filter by specific profile?"):
        profiles = get_all_profiles()
        if not profiles:
            print("❌ No profiles found")
            return
        
        print("\nAvailable profiles:")
        for p in profiles:
            print(f"  ID {p.id}: {p.relocation_name}")
        
        try:
            profile_id = int(input("\nEnter profile ID: ").strip())
            phases = get_all_phases(relocation_profile_id=profile_id)
        except ValueError:
            print("❌ Invalid profile ID")
            return
    else:
        phases = get_all_phases()
    
    if not phases:
        print("No phases found.")
        return
    
    print(f"\nTotal phases: {len(phases)}\n")
    
    for phase in phases:
        display_phase(phase)


def menu_update_phase():
    """Update an existing phase"""
    print_header("Update Relocation Phase")
    
    # Show all phases
    phases = get_all_phases()
    if not phases:
        print("No phases found.")
        return
    
    print("Available phases:")
    for p in phases:
        print(f"  ID {p.id}: {p.name} (Profile ID: {p.relocation_profile_id})")
    
    print()
    
    # Get phase ID
    try:
        phase_id = int(input("Enter phase ID to update: ").strip())
    except ValueError:
        print("❌ Please enter a valid number")
        return
    
    # Get the phase
    phase = get_phase_by_id(phase_id)
    if not phase:
        print(f"❌ No phase found with ID {phase_id}")
        return
    
    # Show current phase
    print("\nCurrent phase:")
    display_phase(phase)
    
    # Ask what to update
    print("What would you like to update? (Press Enter to skip)")
    print("-" * 60)
    
    updates = {}
    
    # Name
    new_name = input(f"Phase name [{phase.name}]: ").strip()
    if new_name:
        updates['name'] = new_name
    
    # Start month
    new_start = input(f"Start month [{phase.relative_start_month}]: ").strip()
    if new_start:
        try:
            updates['relative_start_month'] = int(new_start)
        except ValueError:
            print("⚠️  Invalid number for start month, skipping")
    
    # End month
    new_end = input(f"End month [{phase.relative_end_month}]: ").strip()
    if new_end:
        try:
            updates['relative_end_month'] = int(new_end)
        except ValueError:
            print("⚠️  Invalid number for end month, skipping")
    
    # Order index
    new_order = input(f"Order index [{phase.order_index}]: ").strip()
    if new_order:
        try:
            updates['order_index'] = int(new_order)
        except ValueError:
            print("⚠️  Invalid number for order index, skipping")
    
    # Description
    print(f"Current description: {phase.description or 'None'}")
    if get_yes_no_input("Update description?"):
        new_desc = input("Enter new description: ").strip()
        updates['description'] = new_desc if new_desc else None
    
    # Check if any updates
    if not updates:
        print("\n⚠️  No changes made")
        return
    
    # Confirm
    print("\n" + "-" * 60)
    print("FIELDS TO UPDATE:")
    for key, value in updates.items():
        print(f"  {key}: {value}")
    print("-" * 60)
    
    if not get_yes_no_input("\nApply these updates?"):
        print("❌ Update cancelled")
        return
    
    # Apply updates
    updated_phase = update_phase(phase_id, **updates)
    
    if updated_phase:
        print("\n✅ Phase updated successfully!")
        display_phase(updated_phase)


def menu_delete_phase():
    """Delete a phase"""
    print_header("Delete Relocation Phase")
    
    # Show all phases
    phases = get_all_phases()
    if not phases:
        print("No phases found.")
        return
    
    print("Available phases:")
    for p in phases:
        print(f"  ID {p.id}: {p.name} (Profile ID: {p.relocation_profile_id})")
    
    print()
    
    # Get phase ID
    try:
        phase_id = int(input("Enter phase ID to delete: ").strip())
    except ValueError:
        print("❌ Please enter a valid number")
        return
    
    # Get and show the phase
    phase = get_phase_by_id(phase_id)
    if not phase:
        print(f"❌ No phase found with ID {phase_id}")
        return
    
    print("\nPhase to delete:")
    display_phase(phase)
    
    # Confirm deletion
    print("⚠️  WARNING: This cannot be undone!")
    if not get_yes_no_input("Are you sure you want to delete this phase?"):
        print("❌ Deletion cancelled")
        return
    
    # Delete it
    if delete_phase(phase_id):
        print("\n✅ Phase deleted successfully")
    else:
        print("\n❌ Failed to delete phase")

def menu_create_phase():
    """Create a new phase for a relocation profile"""
    print_header("Create New Relocation Phase")
    
    # First, show all profiles so user can choose
    profiles = get_all_profiles()
    if not profiles:
        print("❌ No profiles found. Create a profile first!")
        return
    
    print("Available profiles:")
    for p in profiles:
        print(f"  ID {p.id}: {p.relocation_name}")
    
    print()
    
    # Get profile ID
    try:
        profile_id = int(input("Enter profile ID for this phase: ").strip())
    except ValueError:
        print("❌ Please enter a valid number")
        return
    
    # Verify profile exists
    profile = get_profile_by_id(profile_id)
    if not profile:
        print(f"❌ No profile found with ID {profile_id}")
        return
    
    print(f"\nCreating phase for: {profile.relocation_name}")
    print("-" * 60)
    
    # Get phase details
    name = input("Phase name (e.g., 'Pre-departure Planning'): ").strip()
    if not name:
        print("❌ Phase name is required!")
        return
    
    print("\nTimeline (in months relative to target arrival date):")
    print("  Example: -6 means 6 months before arrival")
    print("  Example: 0 means the arrival month")
    print("  Example: 3 means 3 months after arrival")
    
    try:
        start_month = int(input("Start month: ").strip())
        end_month = int(input("End month: ").strip())
        
        if start_month >= end_month:
            print("❌ Start month must be before end month!")
            return
        
        order_index = int(input("Order index (for sorting, e.g., 1, 2, 3...): ").strip())
        
    except ValueError:
        print("❌ Please enter valid numbers!")
        return
    
    description = input("Description (optional): ").strip()
    if not description:
        description = None
    
    # Confirm
    print("\n" + "-" * 60)
    print("REVIEW PHASE:")
    print(f"  Name: {name}")
    print(f"  Timeline: Month {start_month} to {end_month}")
    print(f"  Order: {order_index}")
    if description:
        print(f"  Description: {description}")
    print("-" * 60)
    
    if not get_yes_no_input("\nCreate this phase?"):
        print("❌ Phase creation cancelled")
        return
    
    # Create the phase
    try:
        phase = create_phase(
            relocation_profile_id=profile_id,
            name=name,
            relative_start_month=start_month,
            relative_end_month=end_month,
            order_index=order_index,
            description=description
        )
        print("\n✅ Phase created successfully!")
        display_phase(phase)
    except Exception as e:
        print(f"\n❌ Error creating phase: {e}")


def menu_view_all_phases():
    """View all phases, optionally filtered by profile"""
    print_header("View Relocation Phases")
    
    # Ask if they want to filter by profile
    if get_yes_no_input("Filter by specific profile?"):
        profiles = get_all_profiles()
        if not profiles:
            print("❌ No profiles found")
            return
        
        print("\nAvailable profiles:")
        for p in profiles:
            print(f"  ID {p.id}: {p.relocation_name}")
        
        try:
            profile_id = int(input("\nEnter profile ID: ").strip())
            phases = get_all_phases(relocation_profile_id=profile_id)
        except ValueError:
            print("❌ Invalid profile ID")
            return
    else:
        phases = get_all_phases()
    
    if not phases:
        print("No phases found.")
        return
    
    print(f"\nTotal phases: {len(phases)}\n")
    
    for phase in phases:
        display_phase(phase)


def menu_update_phase():
    """Update an existing phase"""
    print_header("Update Relocation Phase")
    
    # Show all phases
    phases = get_all_phases()
    if not phases:
        print("No phases found.")
        return
    
    print("Available phases:")
    for p in phases:
        print(f"  ID {p.id}: {p.name} (Profile ID: {p.relocation_profile_id})")
    
    print()
    
    # Get phase ID
    try:
        phase_id = int(input("Enter phase ID to update: ").strip())
    except ValueError:
        print("❌ Please enter a valid number")
        return
    
    # Get the phase
    phase = get_phase_by_id(phase_id)
    if not phase:
        print(f"❌ No phase found with ID {phase_id}")
        return
    
    # Show current phase
    print("\nCurrent phase:")
    display_phase(phase)
    
    # Ask what to update
    print("What would you like to update? (Press Enter to skip)")
    print("-" * 60)
    
    updates = {}
    
    # Name
    new_name = input(f"Phase name [{phase.name}]: ").strip()
    if new_name:
        updates['name'] = new_name
    
    # Start month
    new_start = input(f"Start month [{phase.relative_start_month}]: ").strip()
    if new_start:
        try:
            updates['relative_start_month'] = int(new_start)
        except ValueError:
            print("⚠️  Invalid number for start month, skipping")
    
    # End month
    new_end = input(f"End month [{phase.relative_end_month}]: ").strip()
    if new_end:
        try:
            updates['relative_end_month'] = int(new_end)
        except ValueError:
            print("⚠️  Invalid number for end month, skipping")
    
    # Order index
    new_order = input(f"Order index [{phase.order_index}]: ").strip()
    if new_order:
        try:
            updates['order_index'] = int(new_order)
        except ValueError:
            print("⚠️  Invalid number for order index, skipping")
    
    # Description
    print(f"Current description: {phase.description or 'None'}")
    if get_yes_no_input("Update description?"):
        new_desc = input("Enter new description: ").strip()
        updates['description'] = new_desc if new_desc else None
    
    # Check if any updates
    if not updates:
        print("\n⚠️  No changes made")
        return
    
    # Confirm
    print("\n" + "-" * 60)
    print("FIELDS TO UPDATE:")
    for key, value in updates.items():
        print(f"  {key}: {value}")
    print("-" * 60)
    
    if not get_yes_no_input("\nApply these updates?"):
        print("❌ Update cancelled")
        return
    
    # Apply updates
    updated_phase = update_phase(phase_id, **updates)
    
    if updated_phase:
        print("\n✅ Phase updated successfully!")
        display_phase(updated_phase)


def menu_delete_phase():
    """Delete a phase"""
    print_header("Delete Relocation Phase")
    
    # Show all phases
    phases = get_all_phases()
    if not phases:
        print("No phases found.")
        return
    
    print("Available phases:")
    for p in phases:
        print(f"  ID {p.id}: {p.name} (Profile ID: {p.relocation_profile_id})")
    
    print()
    
    # Get phase ID
    try:
        phase_id = int(input("Enter phase ID to delete: ").strip())
    except ValueError:
        print("❌ Please enter a valid number")
        return
    
    # Get and show the phase
    phase = get_phase_by_id(phase_id)
    if not phase:
        print(f"❌ No phase found with ID {phase_id}")
        return
    
    print("\nPhase to delete:")
    display_phase(phase)
    
    # Confirm deletion
    print("⚠️  WARNING: This cannot be undone!")
    if not get_yes_no_input("Are you sure you want to delete this phase?"):
        print("❌ Deletion cancelled")
        return
    
    # Delete it
    if delete_phase(phase_id):
        print("\n✅ Phase deleted successfully")
    else:
        print("\n❌ Failed to delete phase")
def menu_create_task():
    """Create a new task"""
    print_header("Create New Task")
    
    # First, show all profiles
    profiles = get_all_profiles()
    if not profiles:
        print("❌ No profiles found. Create a profile first!")
        return
    
    print("Available profiles:")
    for p in profiles:
        print(f"  ID {p.id}: {p.relocation_name}")
    
    print()
    
    # Get profile ID
    try:
        profile_id = int(input("Enter profile ID for this task: ").strip())
    except ValueError:
        print("❌ Please enter a valid number")
        return
    
    # Verify profile exists
    profile = get_profile_by_id(profile_id)
    if not profile:
        print(f"❌ No profile found with ID {profile_id}")
        return
    
    # Get phases for this profile
    phases = get_all_phases(relocation_profile_id=profile_id)
    if not phases:
        print(f"❌ No phases found for this profile. Create a phase first!")
        return
    
    print(f"\nAvailable phases for '{profile.relocation_name}':")
    for p in phases:
        print(f"  ID {p.id}: {p.name} (Months {p.relative_start_month} to {p.relative_end_month})")
    
    print()
    
    # Get phase ID
    try:
        phase_id = int(input("Enter phase ID for this task: ").strip())
    except ValueError:
        print("❌ Please enter a valid number")
        return
    
    # Verify phase exists and belongs to this profile
    phase = get_phase_by_id(phase_id)
    if not phase or phase.relocation_profile_id != profile_id:
        print(f"❌ Invalid phase ID for this profile")
        return
    
    print(f"\nCreating task for phase: {phase.name}")
    print("-" * 60)
    
    # Get task details
    title = input("Task title: ").strip()
    if not title:
        print("❌ Task title is required!")
        return
    
    description = input("Description (optional): ").strip()
    if not description:
        description = None
    
    # Status
    print("\nStatus:")
    print("  1. Not started (default)")
    print("  2. In progress")
    print("  3. Completed")
    status_choice = input("Choose status (1-3, or Enter for default): ").strip()
    
    status_map = {
        '1': 'not_started',
        '2': 'in_progress',
        '3': 'completed',
        '': 'not_started'
    }
    status = status_map.get(status_choice, 'not_started')
    
    # Critical
    critical = get_yes_no_input("Is this task critical/important?")
    
    # Planned date
    print("\nPlanned date (optional):")
    planned_date = get_date_input("Enter planned date or press Enter to skip:")
    
    # Notes
    notes = input("Additional notes (optional): ").strip()
    if not notes:
        notes = None
    
    # Confirm
    print("\n" + "-" * 60)
    print("REVIEW TASK:")
    print(f"  Title: {title}")
    print(f"  Phase: {phase.name}")
    print(f"  Status: {status.replace('_', ' ').title()}")
    print(f"  Critical: {'Yes' if critical else 'No'}")
    if description:
        print(f"  Description: {description}")
    if planned_date:
        print(f"  Planned Date: {planned_date}")
    if notes:
        print(f"  Notes: {notes}")
    print("-" * 60)
    
    if not get_yes_no_input("\nCreate this task?"):
        print("❌ Task creation cancelled")
        return
    
    # Create the task
    try:
        task = create_task(
            relocation_profile_id=profile_id,
            phase_id=phase_id,
            title=title,
            description=description,
            status=status,
            critical=critical,
            planned_date=planned_date,
            notes=notes
        )
        print("\n✅ Task created successfully!")
        display_task(task)
    except Exception as e:
        print(f"\n❌ Error creating task: {e}")


def menu_view_all_tasks():
    """View all tasks with filtering options"""
    print_header("View Tasks")
    
    # Ask about filtering
    print("Filter options:")
    print("  1. View all tasks")
    print("  2. Filter by profile")
    print("  3. Filter by phase")
    print("  4. Filter by status")
    
    filter_choice = input("\nChoose filter (1-4): ").strip()
    
    profile_id = None
    phase_id = None
    status = None
    
    if filter_choice == '2':
        # Filter by profile
        profiles = get_all_profiles()
        if not profiles:
            print("❌ No profiles found")
            return
        
        print("\nAvailable profiles:")
        for p in profiles:
            print(f"  ID {p.id}: {p.relocation_name}")
        
        try:
            profile_id = int(input("\nEnter profile ID: ").strip())
        except ValueError:
            print("❌ Invalid profile ID")
            return
    
    elif filter_choice == '3':
        # Filter by phase
        phases = get_all_phases()
        if not phases:
            print("❌ No phases found")
            return
        
        print("\nAvailable phases:")
        for p in phases:
            print(f"  ID {p.id}: {p.name} (Profile ID: {p.relocation_profile_id})")
        
        try:
            phase_id = int(input("\nEnter phase ID: ").strip())
        except ValueError:
            print("❌ Invalid phase ID")
            return
    
    elif filter_choice == '4':
        # Filter by status
        print("\nStatus options:")
        print("  1. Not started")
        print("  2. In progress")
        print("  3. Completed")
        
        status_choice = input("\nChoose status (1-3): ").strip()
        status_map = {
            '1': 'not_started',
            '2': 'in_progress',
            '3': 'completed'
        }
        status = status_map.get(status_choice)
    
    # Get tasks
    tasks = get_all_tasks(
        relocation_profile_id=profile_id,
        phase_id=phase_id,
        status=status
    )
    
    if not tasks:
        print("\nNo tasks found.")
        return
    
    print(f"\nTotal tasks: {len(tasks)}\n")
    
    for task in tasks:
        display_task(task)


def menu_update_task():
    """Update an existing task"""
    print_header("Update Task")
    
    # Show all tasks
    tasks = get_all_tasks()
    if not tasks:
        print("No tasks found.")
        return
    
    print("Available tasks:")
    for t in tasks:
        status_emoji = {'not_started': '⏸️', 'in_progress': '🔄', 'completed': '✅'}
        emoji = status_emoji.get(t.status, '❓')
        critical = "🔴" if t.critical else ""
        print(f"  ID {t.id}: {emoji} {t.title} {critical}")
    
    print()
    
    # Get task ID
    try:
        task_id = int(input("Enter task ID to update: ").strip())
    except ValueError:
        print("❌ Please enter a valid number")
        return
    
    # Get the task
    task = get_task_by_id(task_id)
    if not task:
        print(f"❌ No task found with ID {task_id}")
        return
    
    # Show current task
    print("\nCurrent task:")
    display_task(task)
    
    # Ask what to update
    print("What would you like to update? (Press Enter to skip)")
    print("-" * 60)
    
    updates = {}
    
    # Title
    new_title = input(f"Title [{task.title}]: ").strip()
    if new_title:
        updates['title'] = new_title
    
    # Description
    print(f"Current description: {task.description or 'None'}")
    if get_yes_no_input("Update description?"):
        new_desc = input("Enter new description: ").strip()
        updates['description'] = new_desc if new_desc else None
    
    # Status
    print(f"\nCurrent status: {task.status.replace('_', ' ').title()}")
    if get_yes_no_input("Update status?"):
        print("  1. Not started")
        print("  2. In progress")
        print("  3. Completed")
        status_choice = input("Choose status (1-3): ").strip()
        status_map = {'1': 'not_started', '2': 'in_progress', '3': 'completed'}
        if status_choice in status_map:
            updates['status'] = status_map[status_choice]
            
            # If marking as completed, set completed date
            if status_map[status_choice] == 'completed':
                from datetime import date
                updates['completed_date'] = date.today()
    
    # Critical
    current_critical = "Yes" if task.critical else "No"
    if get_yes_no_input(f"Update critical status? (currently: {current_critical})"):
        updates['critical'] = get_yes_no_input("Is this task critical?")
    
    # Planned date
    print(f"Current planned date: {task.planned_date or 'None'}")
    if get_yes_no_input("Update planned date?"):
        new_date = get_date_input("Enter new planned date or press Enter to clear:")
        if new_date:
            updates['planned_date'] = new_date
    
    # Notes
    print(f"Current notes: {task.notes or 'None'}")
    if get_yes_no_input("Update notes?"):
        new_notes = input("Enter new notes: ").strip()
        updates['notes'] = new_notes if new_notes else None
    
    # Check if any updates
    if not updates:
        print("\n⚠️  No changes made")
        return
    
    # Confirm
    print("\n" + "-" * 60)
    print("FIELDS TO UPDATE:")
    for key, value in updates.items():
        print(f"  {key}: {value}")
    print("-" * 60)
    
    if not get_yes_no_input("\nApply these updates?"):
        print("❌ Update cancelled")
        return
    
    # Apply updates
    updated_task = update_task(task_id, **updates)
    
    if updated_task:
        print("\n✅ Task updated successfully!")
        display_task(updated_task)


def menu_mark_task_completed():
    """Quick action to mark a task as completed"""
    print_header("Mark Task as Completed")
    
    # Show incomplete tasks
    incomplete_tasks = get_all_tasks(status='not_started') + get_all_tasks(status='in_progress')
    
    if not incomplete_tasks:
        print("No incomplete tasks found. Great job! 🎉")
        return
    
    print("Incomplete tasks:")
    for t in incomplete_tasks:
        critical = "🔴" if t.critical else ""
        print(f"  ID {t.id}: {t.title} {critical} [{t.status.replace('_', ' ').title()}]")
    
    print()
    
    # Get task ID
    try:
        task_id = int(input("Enter task ID to mark as completed: ").strip())
    except ValueError:
        print("❌ Please enter a valid number")
        return
    
    # Get the task
    task = get_task_by_id(task_id)
    if not task:
        print(f"❌ No task found with ID {task_id}")
        return
    
    if task.status == 'completed':
        print(f"⚠️  This task is already completed on {task.completed_date}")
        return
    
    # Show task
    display_task(task)
    
    # Confirm
    if not get_yes_no_input("Mark this task as completed?"):
        print("❌ Cancelled")
        return
    
    # Mark completed
    updated_task = mark_task_completed(task_id)
    
    if updated_task:
        print("\n✅ Task marked as completed!")
        display_task(updated_task)


def menu_delete_task():
    """Delete a task"""
    print_header("Delete Task")
    
    # Show all tasks
    tasks = get_all_tasks()
    if not tasks:
        print("No tasks found.")
        return
    
    print("Available tasks:")
    for t in tasks:
        status_emoji = {'not_started': '⏸️', 'in_progress': '🔄', 'completed': '✅'}
        emoji = status_emoji.get(t.status, '❓')
        print(f"  ID {t.id}: {emoji} {t.title}")
    
    print()
    
    # Get task ID
    try:
        task_id = int(input("Enter task ID to delete: ").strip())
    except ValueError:
        print("❌ Please enter a valid number")
        return
    
    # Get and show the task
    task = get_task_by_id(task_id)
    if not task:
        print(f"❌ No task found with ID {task_id}")
        return
    
    print("\nTask to delete:")
    display_task(task)
    
    # Confirm deletion
    print("⚠️  WARNING: This cannot be undone!")
    if not get_yes_no_input("Are you sure you want to delete this task?"):
        print("❌ Deletion cancelled")
        return
    
    # Delete it
    if delete_task(task_id):
        print("\n✅ Task deleted successfully")
    else:
        print("\n❌ Failed to delete task")
def menu_create_expense():
    """Create a new expense"""
    print_header("Create New Expense")
    
    # Get profile
    profiles = get_all_profiles()
    if not profiles:
        print("❌ No profiles found. Create a profile first!")
        return
    
    print("Available profiles:")
    for p in profiles:
        print(f"  ID {p.id}: {p.relocation_name}")
    
    print()
    
    try:
        profile_id = int(input("Enter profile ID: ").strip())
    except ValueError:
        print("❌ Please enter a valid number")
        return
    
    profile = get_profile_by_id(profile_id)
    if not profile:
        print(f"❌ No profile found with ID {profile_id}")
        return
    
    # Get phase
    phases = get_all_phases(relocation_profile_id=profile_id)
    if not phases:
        print("❌ No phases found. Create a phase first!")
        return
    
    print(f"\nAvailable phases for '{profile.relocation_name}':")
    for p in phases:
        print(f"  ID {p.id}: {p.name}")
    
    print()
    
    try:
        phase_id = int(input("Enter phase ID: ").strip())
    except ValueError:
        print("❌ Please enter a valid number")
        return
    
    phase = get_phase_by_id(phase_id)
    if not phase or phase.relocation_profile_id != profile_id:
        print("❌ Invalid phase ID")
        return
    
    print(f"\nCreating expense for phase: {phase.name}")
    print("-" * 60)
    
    # Get expense details
    title = input("Expense title (e.g., 'Visa application fee'): ").strip()
    if not title:
        print("❌ Title is required!")
        return
    
    category = input("Category (e.g., 'Legal', 'Housing', 'Transportation'): ").strip()
    if not category:
        category = None
    
    # Currency
    print(f"\nPrimary currency for profile: {profile.primary_currency}")
    currency = input(f"Expense currency (or Enter for {profile.primary_currency}): ").strip().upper()
    if not currency:
        currency = profile.primary_currency
    
    # Get exchange rate if different currency
    exchange_rate = None
    if currency != profile.primary_currency:
        print(f"\nFetching exchange rate from {currency} to {profile.primary_currency}...")
        exchange_rate = get_exchange_rate(currency, profile.primary_currency)
        
        if exchange_rate is None:
            # API failed, offer manual entry
            exchange_rate = get_manual_exchange_rate()
            
        if exchange_rate:
            rate_display = exchange_rate / 10000
            print(f"  Using rate: 1 {currency} = {rate_display:.4f} {profile.primary_currency}")
    
    # Estimated amount
    print("\nEstimated amount:")
    estimated_amount = get_currency_amount("Enter estimated amount")
    if estimated_amount is None:
        print("❌ Estimated amount is required!")
        return
    
    # Actual amount (optional)
    if get_yes_no_input("\nDo you know the actual amount already?"):
        actual_amount = get_currency_amount("Enter actual amount")
    else:
        actual_amount = None
    
    # Cost certainty
    print("\nCost certainty:")
    print("  1. Unknown")
    print("  2. Estimated (default)")
    print("  3. Confirmed")
    certainty_choice = input("Choose (1-3, or Enter for default): ").strip()
    certainty_map = {
        '1': 'unknown',
        '2': 'estimated',
        '3': 'confirmed',
        '': 'estimated'
    }
    cost_certainty = certainty_map.get(certainty_choice, 'estimated')
    
    # Payment status
    payment_status = 'paid' if get_yes_no_input("\nHas this been paid already?") else 'unpaid'
    
    # Due date (if unpaid)
    due_date = None
    if payment_status == 'unpaid':
        print("\nPayment due date (optional):")
        due_date = get_date_input("Enter due date or press Enter to skip:")
    
    # Budget flags
    include_in_budget = get_yes_no_input("\nInclude in budget calculations?")
    one_time_cost = get_yes_no_input("Is this a one-time relocation cost?")
    
    # Related task (optional)
    if get_yes_no_input("\nLink to a task?"):
        tasks = get_all_tasks(relocation_profile_id=profile_id)
        if tasks:
            print("\nAvailable tasks:")
            for t in tasks:
                print(f"  ID {t.id}: {t.title}")
            try:
                related_task_id = int(input("\nEnter task ID: ").strip())
            except ValueError:
                related_task_id = None
        else:
            print("No tasks found")
            related_task_id = None
    else:
        related_task_id = None
    
    # Notes
    notes = input("\nAdditional notes (optional): ").strip()
    if not notes:
        notes = None
    
    # Confirm
    print("\n" + "-" * 60)
    print("REVIEW EXPENSE:")
    print(f"  Title: {title}")
    print(f"  Category: {category or 'None'}")
    print(f"  Phase: {phase.name}")
    est_display = estimated_amount / 100
    print(f"  Estimated: {est_display:.2f} {currency}")
    if actual_amount:
        act_display = actual_amount / 100
        print(f"  Actual: {act_display:.2f} {currency}")
    print(f"  Cost Certainty: {cost_certainty}")
    print(f"  Payment Status: {payment_status}")
    if due_date:
        print(f"  Due Date: {due_date}")
    print(f"  Include in Budget: {'Yes' if include_in_budget else 'No'}")
    print(f"  One-time Cost: {'Yes' if one_time_cost else 'No'}")
    print("-" * 60)
    
    if not get_yes_no_input("\nCreate this expense?"):
        print("❌ Expense creation cancelled")
        return
    
    # Create expense
    try:
        expense = create_expense(
            relocation_profile_id=profile_id,
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
            one_time_relocation_cost=one_time_cost,
            due_date=due_date,
            related_task_id=related_task_id,
            notes=notes
        )
        print("\n✅ Expense created successfully!")
        display_expense(expense)
    except Exception as e:
        print(f"\n❌ Error creating expense: {e}")


def menu_view_all_expenses():
    """View all expenses with filtering"""
    print_header("View Expenses")
    
    print("Filter options:")
    print("  1. View all expenses")
    print("  2. Filter by profile")
    print("  3. Filter by phase")
    print("  4. Filter by payment status")
    
    filter_choice = input("\nChoose filter (1-4): ").strip()
    
    profile_id = None
    phase_id = None
    payment_status = None
    
    if filter_choice == '2':
        profiles = get_all_profiles()
        if not profiles:
            print("❌ No profiles found")
            return
        
        print("\nAvailable profiles:")
        for p in profiles:
            print(f"  ID {p.id}: {p.relocation_name}")
        
        try:
            profile_id = int(input("\nEnter profile ID: ").strip())
        except ValueError:
            print("❌ Invalid profile ID")
            return
    
    elif filter_choice == '3':
        phases = get_all_phases()
        if not phases:
            print("❌ No phases found")
            return
        
        print("\nAvailable phases:")
        for p in phases:
            print(f"  ID {p.id}: {p.name}")
        
        try:
            phase_id = int(input("\nEnter phase ID: ").strip())
        except ValueError:
            print("❌ Invalid phase ID")
            return
    
    elif filter_choice == '4':
        print("\nPayment status:")
        print("  1. Unpaid")
        print("  2. Paid")
        
        status_choice = input("\nChoose (1-2): ").strip()
        payment_status = 'unpaid' if status_choice == '1' else 'paid'
    
    # Get expenses
    expenses = get_all_expenses(
        relocation_profile_id=profile_id,
        phase_id=phase_id,
        payment_status=payment_status
    )
    
    if not expenses:
        print("\nNo expenses found.")
        return
    
    print(f"\nTotal expenses: {len(expenses)}\n")
    
    for expense in expenses:
        display_expense(expense)


def menu_update_expense():
    """Update an existing expense"""
    print_header("Update Expense")
    
    expenses = get_all_expenses()
    if not expenses:
        print("No expenses found.")
        return
    
    print("Available expenses:")
    for e in expenses:
        amount = (e.actual_amount if e.actual_amount else e.estimated_amount) / 100
        status = "✅" if e.payment_status == 'paid' else "💰"
        print(f"  ID {e.id}: {status} {e.title} ({amount:.2f} {e.currency})")
    
    print()
    
    try:
        expense_id = int(input("Enter expense ID to update: ").strip())
    except ValueError:
        print("❌ Please enter a valid number")
        return
    
    expense = get_expense_by_id(expense_id)
    if not expense:
        print(f"❌ No expense found with ID {expense_id}")
        return
    
    print("\nCurrent expense:")
    display_expense(expense)
    
    print("What would you like to update? (Press Enter to skip)")
    print("-" * 60)
    
    updates = {}
    
    # Title
    new_title = input(f"Title [{expense.title}]: ").strip()
    if new_title:
        updates['title'] = new_title
    
    # Category
    new_category = input(f"Category [{expense.category or 'None'}]: ").strip()
    if new_category:
        updates['category'] = new_category
    
    # Estimated amount
    print(f"Current estimated: {expense.estimated_amount/100:.2f} {expense.currency}")
    if get_yes_no_input("Update estimated amount?"):
        new_est = get_currency_amount("Enter new estimated amount")
        if new_est:
            updates['estimated_amount'] = new_est
    
    # Actual amount
    current_actual = f"{expense.actual_amount/100:.2f}" if expense.actual_amount else "None"
    print(f"Current actual: {current_actual}")
    if get_yes_no_input("Update actual amount?"):
        new_act = get_currency_amount("Enter actual amount (or 0 to clear)")
        if new_act is not None:
            updates['actual_amount'] = new_act if new_act > 0 else None
    
    # Payment status
    if expense.payment_status == 'unpaid':
        if get_yes_no_input(f"\nMark as paid?"):
            updates['payment_status'] = 'paid'
    else:
        if get_yes_no_input(f"\nMark as unpaid?"):
            updates['payment_status'] = 'unpaid'
    
    # Cost certainty
    print(f"Current cost certainty: {expense.cost_certainty}")
    if get_yes_no_input("Update cost certainty?"):
        print("  1. Unknown")
        print("  2. Estimated")
        print("  3. Confirmed")
        cert_choice = input("Choose (1-3): ").strip()
        cert_map = {'1': 'unknown', '2': 'estimated', '3': 'confirmed'}
        if cert_choice in cert_map:
            updates['cost_certainty'] = cert_map[cert_choice]
    
    # Due date
    if get_yes_no_input(f"\nUpdate due date? (current: {expense.due_date or 'None'})"):
        new_due = get_date_input("Enter new due date:")
        if new_due:
            updates['due_date'] = new_due
    
    # Notes
    if get_yes_no_input("\nUpdate notes?"):
        new_notes = input("Enter new notes: ").strip()
        updates['notes'] = new_notes if new_notes else None
    
    if not updates:
        print("\n⚠️  No changes made")
        return
    
    # Confirm
    print("\n" + "-" * 60)
    print("FIELDS TO UPDATE:")
    for key, value in updates.items():
        if key in ['estimated_amount', 'actual_amount'] and value:
            print(f"  {key}: {value/100:.2f}")
        else:
            print(f"  {key}: {value}")
    print("-" * 60)
    
    if not get_yes_no_input("\nApply these updates?"):
        print("❌ Update cancelled")
        return
    
    updated_expense = update_expense(expense_id, **updates)
    
    if updated_expense:
        print("\n✅ Expense updated successfully!")
        display_expense(updated_expense)


def menu_mark_expense_paid():
    """Quick action to mark expense as paid"""
    print_header("Mark Expense as Paid")
    
    unpaid = get_all_expenses(payment_status='unpaid')
    
    if not unpaid:
        print("No unpaid expenses. Great! 🎉")
        return
    
    print("Unpaid expenses:")
    for e in unpaid:
        amount = (e.actual_amount if e.actual_amount else e.estimated_amount) / 100
        overdue = " ⚠️ OVERDUE" if e.is_overdue else ""
        print(f"  ID {e.id}: {e.title} ({amount:.2f} {e.currency}){overdue}")
    
    print()
    
    try:
        expense_id = int(input("Enter expense ID to mark as paid: ").strip())
    except ValueError:
        print("❌ Please enter a valid number")
        return
    
    expense = get_expense_by_id(expense_id)
    if not expense:
        print(f"❌ No expense found with ID {expense_id}")
        return
    
    if expense.payment_status == 'paid':
        print("⚠️  This expense is already marked as paid")
        return
    
    display_expense(expense)
    
    if not get_yes_no_input("Mark this expense as paid?"):
        print("❌ Cancelled")
        return
    
    updated = mark_expense_paid(expense_id)
    
    if updated:
        print("\n✅ Expense marked as paid!")
        display_expense(updated)


def menu_delete_expense():
    """Delete an expense"""
    print_header("Delete Expense")
    
    expenses = get_all_expenses()
    if not expenses:
        print("No expenses found.")
        return
    
    print("Available expenses:")
    for e in expenses:
        amount = (e.actual_amount if e.actual_amount else e.estimated_amount) / 100
        print(f"  ID {e.id}: {e.title} ({amount:.2f} {e.currency})")
    
    print()
    
    try:
        expense_id = int(input("Enter expense ID to delete: ").strip())
    except ValueError:
        print("❌ Please enter a valid number")
        return
    
    expense = get_expense_by_id(expense_id)
    if not expense:
        print(f"❌ No expense found with ID {expense_id}")
        return
    
    print("\nExpense to delete:")
    display_expense(expense)
    
    print("⚠️  WARNING: This cannot be undone!")
    if not get_yes_no_input("Are you sure you want to delete this expense?"):
        print("❌ Deletion cancelled")
        return
    
    if delete_expense(expense_id):
        print("\n✅ Expense deleted successfully")
    else:
        print("\n❌ Failed to delete expense")


def menu_view_budget_summary():
    """View budget summary for a profile"""
    print_header("Budget Summary")
    
    profiles = get_all_profiles()
    if not profiles:
        print("❌ No profiles found")
        return
    
    print("Available profiles:")
    for p in profiles:
        print(f"  ID {p.id}: {p.relocation_name}")
    
    print()
    
    try:
        profile_id = int(input("Enter profile ID: ").strip())
    except ValueError:
        print("❌ Please enter a valid number")
        return
    
    profile = get_profile_by_id(profile_id)
    if not profile:
        print(f"❌ No profile found with ID {profile_id}")
        return
    
    summary = get_budget_summary(profile_id)
    display_budget_summary(summary)
def show_main_menu():
    """Display the main menu and get user choice"""
    print_header("RELOCATION OS - Main Menu")
    print("RELOCATION PROFILES:")
    print("  1. Create new relocation profile")
    print("  2. View all profiles")
    print("  3. View specific profile by ID")
    print("  4. Update a profile")
    print("  5. Delete a profile")
    print("\nRELOCATION PHASES:")
    print("  6. Create new phase")
    print("  7. View all phases")
    print("  8. Update a phase")
    print("  9. Delete a phase")
    print("\nTASKS:")
    print("  10. Create new task")
    print("  11. View all tasks")
    print("  12. Update a task")
    print("  13. Mark task as completed ✅")
    print("  14. Delete a task")
    print("\nEXPENSES:")
    print("  15. Create new expense")
    print("  16. View all expenses")
    print("  17. Update an expense")
    print("  18. Mark expense as paid 💰")
    print("  19. Delete an expense")
    print("  20. View budget summary 📊")
    print("\nOTHER:")
    print("  0. Exit")
    print()
    
    choice = input("Enter your choice: ").strip()
    return choice

def run_menu():
    """Main menu loop"""
    from models import init_database
    
    # Initialize database on startup
    print_header("Starting Relocation OS")
    print("Initializing database...")
    init_database()
    print("✓ Ready!\n")
    
    while True:
        choice = show_main_menu()
        
        # Profile management
        if choice == '1':
            menu_create_profile()
        elif choice == '2':
            menu_view_all_profiles()
        elif choice == '3':
            menu_view_profile_by_id()
        elif choice == '4':
            menu_update_profile()
        elif choice == '5':
            menu_delete_profile()
        
        # Phase management
        elif choice == '6':
            menu_create_phase()
        elif choice == '7':
            menu_view_all_phases()
        elif choice == '8':
            menu_update_phase()
        elif choice == '9':
            menu_delete_phase()
        
        # Task management
        elif choice == '10':
            menu_create_task()
        elif choice == '11':
            menu_view_all_tasks()
        elif choice == '12':
            menu_update_task()
        elif choice == '13':
            menu_mark_task_completed()
        elif choice == '14':
            menu_delete_task()
        
        # Expense management
        elif choice == '15':
            menu_create_expense()
        elif choice == '16':
            menu_view_all_expenses()
        elif choice == '17':
            menu_update_expense()
        elif choice == '18':
            menu_mark_expense_paid()
        elif choice == '19':
            menu_delete_expense()
        elif choice == '20':
            menu_view_budget_summary()

        # Exit
        elif choice == '0':
            print("\n👋 Goodbye! Your data is saved.\n")
            break
        else:
            print("❌ Invalid choice. Please enter a valid option")
        
        # Wait for user to press Enter before showing menu again
        input("\nPress Enter to continue...")