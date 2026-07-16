import logging
from sqlalchemy import inspect, text
from app.extensions import db
from app.models.counter import Counter

logger = logging.getLogger("flask.app")

def initialize_database(app):
    """
    Ensures that the database schema exists.
    - Runs db.create_all() for development and testing environments.
    - Logs a warning in production if tables are missing, suggesting migrations.
    """
    env = app.config.get("ENV", "development")
    is_testing = app.config.get("TESTING", False)

    with app.app_context():
        if env == "development" or is_testing:
            logger.info(f"Environment is '{env}'. Ensuring database schema exists via db.create_all().")
            db.create_all()
        else:
            logger.info("Environment is 'production'. Checking database schema health...")
            try:
                inspector = inspect(db.engine)
                required_tables = ["users", "counters", "tokens"]
                missing_tables = [table for table in required_tables if not inspector.has_table(table)]
                
                if missing_tables:
                    logger.warning(
                        f"Database is missing tables: {missing_tables}. "
                        "Running db.create_all() as a fallback, but Alembic migrations "
                        "should ideally be the primary schema management mechanism in production."
                    )
                    db.create_all()
                else:
                    logger.info("All required database tables ('users', 'counters', 'tokens') exist.")
            except Exception as e:
                logger.error(f"Error verifying database schema: {e}", exc_info=True)

def seed_default_counters(app):
    """
    Seeds default counters if the counters table exists and is empty.
    Utilizes PostgreSQL transaction advisory locks to prevent race conditions
    when running multiple backend replicas in Kubernetes.
    """
    with app.app_context():
        try:
            inspector = inspect(db.engine)
            if not inspector.has_table("counters"):
                logger.warning("Counters table does not exist. Skipping seeding.")
                return

            # Start a transaction for concurrent-safe seeding
            # Using transaction advisory lock if database is PostgreSQL
            is_postgres = db.engine.dialect.name == "postgresql"
            
            if is_postgres:
                # 8734261 is a random unique 64-bit integer identifier for our advisory lock
                db.session.execute(text("SELECT pg_advisory_xact_lock(8734261)"))
                logger.debug("Acquired PostgreSQL advisory lock for seeding.")

            # Check if counters table is empty
            if Counter.query.count() == 0:
                logger.info("Counters table is empty. Seeding default counters...")
                
                # Seeding default counters with name, service_type, and status='open'
                # Note: "License Counter 1" and "Aadhaar Counter 1" requested for prod (instead of ... 2 and ... 3)
                default_counters = [
                    Counter(name="Passport Counter 1", service_type="Passport", status="open"),
                    Counter(name="License Counter 1", service_type="License", status="open"),
                    Counter(name="Aadhaar Counter 1", service_type="Aadhaar", status="open")
                ]
                
                db.session.add_all(default_counters)
                db.session.commit()
                logger.info("Database successfully seeded with default counters.")
            else:
                logger.info("Counters table is not empty. Skipping seeding.")
                
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to seed default counters: {e}", exc_info=True)
