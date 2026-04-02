import asyncio
import uuid
from sqlalchemy import select
from app.core.database import async_session_factory
from app.models.user import User, UserRole
from app.models.financial_record import FinancialRecord  # Required for relationship mapping

async def seed_admin():
    async with async_session_factory() as session:
        # Checking if admin already exists
        result = await session.execute(select(User).where(User.role == UserRole.ADMIN))
        if result.scalar_one_or_none():
            print("[-] An admin user already exists. Skipping bootstrap.")
            return

        admin_id = uuid.uuid4()
        admin = User(
            id=admin_id,
            name="Initial Admin",
            email="admin@zorvyn.test",
            role=UserRole.ADMIN,
            is_active=True
        )
        session.add(admin)
        await session.commit()
        
        print("[+] Bootstrap complete!")
        print(f"    Name:  {admin.name}")
        print(f"    Email: {admin.email}")
        print(f"    ID:    {admin_id}  <-- USE THIS IN Swagger 'X-User-Id' header")

if __name__ == "__main__":
    asyncio.run(seed_admin())
