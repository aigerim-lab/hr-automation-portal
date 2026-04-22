from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# путь к базе (SQLite файл)
DATABASE_URL = "sqlite:///./hr_portal.db"

# подключение к базе
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# сессия для работы с БД
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ВАЖНО: вот этого у тебя не хватает
Base = declarative_base()


# dependency для FastAPI (потом пригодится)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()