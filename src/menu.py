"""
Interactive menu system for Relocation OS
Handles user input and navigation
"""

from datetime import datetime
from database import (
    create_relocation_profile, 
    get_all_profiles, 
    get_profile_by_id,
    display_profile
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


def show_main_menu():
    """Display the main menu and get user choice"""
    print_header("RELOCATION OS - Main Menu")
    print("1. Create new relocation profile")
    print("2. View all profiles")
    print("3. View specific profile by ID")
    print("4. Exit")
    print()
    
    choice = input("Enter your choice (1-4): ").strip()
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
        
        if choice == '1':
            menu_create_profile()
        elif choice == '2':
            menu_view_all_profiles()
        elif choice == '3':
            menu_view_profile_by_id()
        elif choice == '4':
            print("\n👋 Goodbye! Your data is saved.\n")
            break
        else:
            print("❌ Invalid choice. Please enter 1-4")
        
        # Wait for user to press Enter before showing menu again
        input("\nPress Enter to continue...")