from sqlalchemy import create_engine

def get_engine():
    """
    creates a connection (Engine) to the sqlite database.
    earthquakes.db is created alongside the project.
    """
    return create_engine("sqlite:///earthquakes.db", future = True)