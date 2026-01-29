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
    print("\nOTHER:")
    print("  0. Exit")
    print()
    
    choice = input("Enter your choice (0-9): ").strip()
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
        
        # Exit
        elif choice == '0':
            print("\n👋 Goodbye! Your data is saved.\n")
            break
        else:
            print("❌ Invalid choice. Please enter 0-9")
        
        # Wait for user to press Enter before showing menu again
        input("\nPress Enter to continue...")