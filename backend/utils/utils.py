from ..dependencies import SessionLocal

def get_db():
    """
    Dependency function that provides a database session.

    This function acts as a dependency for FastAPI routes. It creates a new SQLAlchemy
    session from the `SessionLocal` factory, yields it to the route function, and ensures
    that the session is closed after the route function completes.

    Returns:
        Session: The SQLAlchemy database session object.
    """
    db = SessionLocal()  # Create a new database session.
    try:
        yield db  # Yield the session to the FastAPI route.
    finally:
        db.close()  # Ensure the session is closed after the route function completes.

