"""
Database Models for Relocation OS
Defines the structure of our data
"""

from datetime import date
from sqlalchemy import create_engine, Column, Integer, String, Date, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

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
    
    def __repr__(self):
        """
        String representation of the object
        Helpful for debugging - shows you what's in the object
        """
        return f"<RelocationProfile(name='{self.relocation_name}', {self.origin_country} → {self.destination_country})>"


# Database setup functions
def get_engine(db_path='data/relocation.db'):
    """
    Creates a connection to the database
    If the database doesn't exist, it will be created
    """
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