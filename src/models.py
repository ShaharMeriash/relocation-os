"""
Database Models for Relocation OS
Defines the structure of our data
"""

from datetime import date
from sqlalchemy import create_engine, Column, Integer, String, Date, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Create base class for our models
Base = declarative_base()


class RelocationProfile(Base):
    """
    Represents a single relocation project
    This is the main entity that everything else relates to
    """
    __tablename__ = 'relocation_profiles'
    
    # Primary key - unique ID for each relocation
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Basic information
    relocation_name = Column(String(200), nullable=False)
    origin_country = Column(String(100), nullable=False)
    destination_country = Column(String(100), nullable=False)
    target_arrival_date = Column(Date, nullable=False)
    
    # Family details
    family_size = Column(Integer, default=1)
    number_of_children = Column(Integer, default=0)
    pets = Column(Boolean, default=False)
    
    # Currency settings
    primary_currency = Column(String(3), default='USD')  # e.g., 'USD', 'EUR'
    secondary_currency = Column(String(3), nullable=True)  # Optional
    
    # Additional info
    notes = Column(Text, nullable=True)
    # Relationship - easy access to all phases for this profile
    phases = relationship("RelocationPhase", back_populates="relocation_profile", cascade="all, delete-orphan")
    # Relationship - easy access to all tasks for this profile
    tasks = relationship("Task", back_populates="relocation_profile", cascade="all, delete-orphan")
    def __repr__(self):
        """
        String representation of the object
        Helpful for debugging - shows you what's in the object
        """
        return f"<RelocationProfile(name='{self.relocation_name}', {self.origin_country} → {self.destination_country})>"
    # Relationship - all expenses for this profile
    expenses = relationship("Expense", back_populates="relocation_profile", cascade="all, delete-orphan")
class RelocationPhase(Base):
    """
    Represents a phase/stage in the relocation timeline
    Phases help organize tasks and expenses by time period
    """
    __tablename__ = 'relocation_phases'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Phase details
    name = Column(String(200), nullable=False)
    relative_start_month = Column(Integer, nullable=False)  # Months relative to arrival (negative = before)
    relative_end_month = Column(Integer, nullable=False)    # Months relative to arrival
    order_index = Column(Integer, nullable=False)           # For sorting phases
    description = Column(Text, nullable=True)
    
    # Foreign key - links to RelocationProfile
    relocation_profile_id = Column(Integer, ForeignKey('relocation_profiles.id'), nullable=False)
    
    # Relationship - easy access to the parent profile
    relocation_profile = relationship("RelocationProfile", back_populates="phases")
    # Relationship - easy access to all tasks in this phase
    tasks = relationship("Task", back_populates="phase", cascade="all, delete-orphan")
    def __repr__(self):
        """String representation for debugging"""
        return f"<RelocationPhase(name='{self.name}', months={self.relative_start_month} to {self.relative_end_month})>"
    # Relationship - expenses in this phase
    expenses = relationship("Expense", back_populates="phase", cascade="all, delete-orphan")
class Task(Base):
    """
    Represents a task/action item in the relocation process
    Tasks belong to phases and help track what needs to be done
    """
    __tablename__ = 'tasks'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Task details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default='not_started')  # not_started, in_progress, completed
    critical = Column(Boolean, default=False)  # Is this task critical/important?
    
    # Dates
    planned_date = Column(Date, nullable=True)
    completed_date = Column(Date, nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Foreign keys
    phase_id = Column(Integer, ForeignKey('relocation_phases.id'), nullable=False)
    relocation_profile_id = Column(Integer, ForeignKey('relocation_profiles.id'), nullable=False)
    
    # Relationships
    phase = relationship("RelocationPhase", back_populates="tasks")
    relocation_profile = relationship("RelocationProfile", back_populates="tasks")
    
    def __repr__(self):
        """String representation for debugging"""
        return f"<Task(title='{self.title}', status='{self.status}', critical={self.critical})>"
    # Database setup functions
    # Relationship - expenses related to this task
    expenses = relationship("Expense", back_populates="related_task")
class Expense(Base):
    """
    Represents an expense/cost in the relocation process
    Tracks estimated vs actual costs with multi-currency support
    """
    __tablename__ = 'expenses'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Identity
    title = Column(String(200), nullable=False)
    category = Column(String(100), nullable=True)  # e.g., "Housing", "Transportation", "Legal"
    
    # Cost information
    estimated_amount = Column(Integer, default=0)  # Store as cents/smallest unit
    actual_amount = Column(Integer, nullable=True)  # Store as cents/smallest unit
    currency = Column(String(3), default='USD')  # 3-letter currency code
    exchange_rate = Column(Integer, nullable=True)  # Rate to primary currency (stored as cents)
    
    # State
    cost_certainty = Column(String(20), default='estimated')  # unknown, estimated, confirmed
    payment_status = Column(String(20), default='unpaid')  # unpaid, paid
    
    # Budget flags
    include_in_budget = Column(Boolean, default=True)
    one_time_relocation_cost = Column(Boolean, default=True)
    
    # Dates
    due_date = Column(Date, nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Foreign keys
    phase_id = Column(Integer, ForeignKey('relocation_phases.id'), nullable=False)
    relocation_profile_id = Column(Integer, ForeignKey('relocation_profiles.id'), nullable=False)
    related_task_id = Column(Integer, ForeignKey('tasks.id'), nullable=True)  # Optional link to task
    
    # Relationships
    phase = relationship("RelocationPhase", back_populates="expenses")
    relocation_profile = relationship("RelocationProfile", back_populates="expenses")
    related_task = relationship("Task", back_populates="expenses")
    
    def __repr__(self):
        """String representation for debugging"""
        amount = self.actual_amount if self.actual_amount else self.estimated_amount
        return f"<Expense(title='{self.title}', amount={amount/100:.2f} {self.currency}, status='{self.payment_status}')>"
    
    @property
    def total_primary_currency(self):
        """Calculate total in primary currency using exchange rate"""
        amount = self.actual_amount if self.actual_amount else self.estimated_amount
        if self.exchange_rate:
            return (amount * self.exchange_rate) / 10000  # Divide by 10000 because both are in cents
        return amount / 100  # If no exchange rate, assume same currency
    
    @property
    def variance(self):
        """Calculate variance between estimated and actual"""
        if self.actual_amount is None:
            return None
        return (self.actual_amount - self.estimated_amount) / 100
    
    @property
    def is_overdue(self):
        """Check if expense is overdue"""
        if not self.due_date or self.payment_status == 'paid':
            return False
        from datetime import date
        return date.today() > self.due_date
def get_engine(db_path=None):
    """
    Creates a connection to the database
    If the database doesn't exist, it will be created
    """
    if db_path is None:
        # Get the absolute path to the project root
        import os
        from pathlib import Path
        
        # Get the directory where this file (models.py) is located
        current_file = Path(__file__)
        src_dir = current_file.parent
        project_root = src_dir.parent
        data_dir = project_root / 'data'
        
        # Create data directory if it doesn't exist
        data_dir.mkdir(exist_ok=True)
        
        db_path = data_dir / 'relocation.db'
    
    return create_engine(f'sqlite:///{db_path}', echo=True)


def init_database(db_path='data/relocation.db'):
    """
    Initialize the database - creates all tables
    Call this once when setting up the app
    """
    engine = get_engine(db_path)
    Base.metadata.create_all(engine)
    print(f"✓ Database initialized at {db_path}")
    return engine


def get_session(engine):
    """
    Creates a session to interact with the database
    Think of it as opening a conversation with your database
    """
    Session = sessionmaker(bind=engine)
    return Session()