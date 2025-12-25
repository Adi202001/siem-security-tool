"""
Initialize database with sample data for testing
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import init_db, AsyncSessionLocal
from app.models.user import User
from app.models.rule import DetectionRule
from app.core.security import get_password_hash


async def create_sample_data():
    """Create sample users and detection rules"""
    async with AsyncSessionLocal() as db:
        # Create admin user
        admin = User(
            email="admin@siem.local",
            username="admin",
            full_name="SIEM Administrator",
            hashed_password=get_password_hash("admin123"),
            is_superuser=True,
            is_active=True
        )
        db.add(admin)

        # Create analyst user
        analyst = User(
            email="analyst@siem.local",
            username="analyst",
            full_name="Security Analyst",
            hashed_password=get_password_hash("analyst123"),
            is_superuser=False,
            is_active=True
        )
        db.add(analyst)

        # Create sample detection rules
        rules = [
            DetectionRule(
                name="Failed SSH Login Attempts",
                description="Detects multiple failed SSH login attempts",
                rule_type="signature",
                severity="high",
                created_by="admin",
                is_active=True,
                conditions={
                    "field_contains": {
                        "message": "Failed password"
                    },
                    "event_type": "authentication_failure"
                }
            ),
            DetectionRule(
                name="Suspicious Port Scan",
                description="Detects potential port scanning activity",
                rule_type="behavioral",
                severity="high",
                created_by="admin",
                is_active=True,
                conditions={
                    "port_range": {
                        "min": 1,
                        "max": 1024
                    },
                    "min_severity": "medium"
                }
            ),
            DetectionRule(
                name="Firewall Block High Severity",
                description="Firewall blocked connection with high severity",
                rule_type="signature",
                severity="medium",
                created_by="admin",
                is_active=True,
                conditions={
                    "field_matches": {
                        "action": "deny"
                    },
                    "min_severity": "high"
                }
            ),
            DetectionRule(
                name="Brute Force Attack",
                description="Multiple authentication failures from same IP",
                rule_type="correlation",
                severity="critical",
                created_by="admin",
                is_active=True,
                conditions={
                    "failed_attempts": {
                        "count": 5,
                        "timeframe_minutes": 5
                    },
                    "event_type": "authentication_failure"
                }
            )
        ]

        for rule in rules:
            db.add(rule)

        await db.commit()
        print("✓ Sample data created successfully!")
        print("\nDefault users:")
        print("  - admin@siem.local / admin123 (Administrator)")
        print("  - analyst@siem.local / analyst123 (Analyst)")
        print("\nDetection rules created: 4")


async def main():
    """Initialize database and create sample data"""
    print("Initializing database...")
    await init_db()
    print("✓ Database initialized")

    print("\nCreating sample data...")
    await create_sample_data()


if __name__ == "__main__":
    asyncio.run(main())
