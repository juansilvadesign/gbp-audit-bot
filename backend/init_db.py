"""
GBP Audit Bot - Database Initialization Script

Creates all database tables based on SQLAlchemy models.
Run this once after setting up your PostgreSQL database.

Usage:
    python init_db.py
"""
import asyncio
import sys

from app.database import engine
from app.models.models import Base


async def init_db():
    """Create all database tables."""
    print("🔄 Conectando ao banco de dados...")
    
    try:
        async with engine.begin() as conn:
            print("📦 Criando tabelas...")
            await conn.run_sync(Base.metadata.create_all)
        
        print("✅ Banco de dados inicializado com sucesso!")
        print("\nTabelas criadas:")
        for table in Base.metadata.tables.keys():
            print(f"  • {table}")
            
    except Exception as e:
        print(f"❌ Erro ao criar banco de dados: {e}")
        sys.exit(1)


async def drop_all():
    """Drop all tables (use with caution!)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    print("⚠️  Todas as tabelas foram removidas!")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--drop":
        confirm = input("⚠️  Isso irá APAGAR todos os dados! Digite 'sim' para confirmar: ")
        if confirm.lower() == "sim":
            asyncio.run(drop_all())
        else:
            print("Operação cancelada.")
    else:
        asyncio.run(init_db())
