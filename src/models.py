from datetime import datetime
from typing import AsyncGenerator, List
from uuid import uuid4, UUID


from sqlalchemy import TIMESTAMP, Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Mapped, MappedColumn, relationship

from config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER
from generics import GUID

UUID_ID = UUID
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

Base = declarative_base()

engine = create_async_engine(DATABASE_URL)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
        
    
class User(Base):
    __tablename__ = "user"
    
    id: Mapped[UUID_ID] = MappedColumn(GUID, primary_key=True, default=uuid4)
    username:  Mapped[str] = MappedColumn(String, nullable=False)
    email: Mapped[str] = MappedColumn(String, nullable=False)
    registered_at = MappedColumn(TIMESTAMP, default=datetime.utcnow)

    image_url: Mapped[str] = MappedColumn(String, nullable=False)
    config: Mapped[dict] = MappedColumn(JSON, nullable=True)
    
    twitch_user_id: Mapped[str] = MappedColumn(String, nullable=False)
    twitch_access_token: Mapped[str] = MappedColumn(String, nullable=False)
    twitch_refresh_token: Mapped[str] = MappedColumn(String, nullable=False)
    is_active: Mapped[bool] = MappedColumn(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = MappedColumn(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = MappedColumn(Boolean, default=False, nullable=False)
    
    order: Mapped[List["Order"]] = relationship()
    
    
class Order(Base):
    __tablename__ = "order"
    id: Mapped[UUID_ID] = MappedColumn(GUID, primary_key=True, default=uuid4)
    url: Mapped[str] 
    sendler: Mapped[str] 
    time_created = MappedColumn(TIMESTAMP, default=datetime.utcnow)
    user_id: Mapped[UUID_ID] = MappedColumn(ForeignKey('user.id'))
    