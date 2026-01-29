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
    def __repr__(self):
        """
        String representation of the object
        Helpful for debugging - shows you what's in the object
        """
        return f"<RelocationProfile(name='{self.relocation_name}', {self.origin_country} → {self.destination_country})>"
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
    
    def __repr__(self):
        """String representation for debugging"""
        return f"<RelocationPhase(name='{self.name}', months={self.relative_start_month} to {self.relative_end_month})>"

# Database setup functions
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