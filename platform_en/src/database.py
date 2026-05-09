import time

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    create_engine,
    select,
)
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

ASYNC_DATABASE_URL = "sqlite+aiosqlite:///data/user_actions.db"
DATABASE_URL = "sqlite:///data/user_actions.db"

engine = create_engine(DATABASE_URL, echo=True)

async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession
)

Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class UserAction(Base):
    __tablename__ = "user_actions"

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    action = Column(String, nullable=False)
    timestamp = Column(Float, default=time.time)
    value = Column(JSON)
    deleted = Column(Boolean, default=False)


def create_database():
    Base.metadata.create_all(bind=engine)


async def async_create_database():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def async_add_user_action(username: str, action: str, value: dict):
    async with AsyncSessionLocal() as session:
        new_action = UserAction(
            username=username, action=action, value=value
        )  # Assume UserAction is defined
        session.add(new_action)
        await session.commit()


def add_user_action(username: str, action: str, value: dict = {}):
    with SessionLocal() as session:
        new_action = UserAction(username=username, action=action, value=value)
        session.add(new_action)
        session.commit()


async def async_add_user_action_wtime(
    username: str, action: str, value: dict, timestamp: int
):
    async with AsyncSessionLocal() as session:
        new_action = UserAction(
            username=username, action=action, value=value, timestamp=timestamp
        )
        session.add(new_action)
        await session.commit()


async def async_get_latest_action_value(username: str, action: str):
    async with AsyncSessionLocal() as session:  # Use async session
        result = await session.execute(
            select(UserAction)
            .filter_by(username=username, action=action, deleted=False)
            .order_by(UserAction.timestamp.desc())
            .limit(1)
        )
        latest_action = result.scalars().first()
        if latest_action is not None:
            return latest_action.value
        else:
            return None


def get_latest_action_value(username: str, action: str):
    with SessionLocal() as session:
        latest_action = (
            session.query(UserAction)
            .filter_by(username=username, action=action, deleted=False)
            .order_by(UserAction.timestamp.desc())
            .first()
        )
        if latest_action is not None:
            return latest_action.value
        else:
            return None


async def async_get_latest_action(username: str, action: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(UserAction)
            .filter_by(username=username, action=action, deleted=False)
            .order_by(UserAction.timestamp.desc())
            .limit(1)
        )
        latest_action = result.scalars().first()
        if latest_action is not None:
            return latest_action
        else:
            return None


def get_latest_action(username: str, action: str):
    with SessionLocal() as session:
        latest_action = (
            session.query(UserAction)
            .filter_by(username=username, action=action, deleted=False)
            .order_by(UserAction.timestamp.desc())
            .first()
        )
        if latest_action is not None:
            return latest_action
        else:
            return None


async def async_get_actions(username: str, action: str, descending: bool = True):
    async with AsyncSessionLocal() as session:
        if descending:
            result = await session.execute(
                select(UserAction)
                .filter_by(username=username, action=action, deleted=False)
                .order_by(UserAction.timestamp.desc())
                .limit(1)
            )
        else:
            result = await session.execute(
                select(UserAction)
                .filter_by(username=username, action=action, deleted=False)
                .order_by(UserAction.timestamp)
                .limit(1)
            )
        latest_action = result.scalars().all()
        if latest_action is not None:
            return latest_action
        else:
            return None


def get_actions(username: str, action: str, descending: bool = True):
    with SessionLocal() as session:
        if descending:
            actions = (
                session.query(UserAction)
                .filter_by(username=username, action=action, deleted=False)
                .order_by(UserAction.timestamp.desc())
                .all()
            )
        else:
            actions = (
                session.query(UserAction)
                .filter_by(username=username, action=action, deleted=False)
                .order_by(UserAction.timestamp)
                .all()
            )
        return actions


async def get_async_all_actions_sorted(username: str, descending: bool = True):
    # deleted actions with also be included
    async with AsyncSessionLocal() as session:
        if descending:
            result = await session.execute(
                select(UserAction)
                .filter_by(username=username)
                .order_by(UserAction.timestamp.desc())
            )
        else:
            result = await session.execute(
                select(UserAction)
                .filter_by(username=username)
                .order_by(UserAction.timestamp)
            )
        actions = result.scalars().all()
        return actions


def get_all_actions_sorted(username: str, descending: bool = True):
    # deleted actions with also be included
    with SessionLocal() as session:
        if descending:
            actions = (
                session.query(UserAction)
                .filter_by(username=username)
                .order_by(UserAction.timestamp.desc())
                .all()
            )
        else:
            actions = (
                session.query(UserAction)
                .filter_by(username=username)
                .order_by(UserAction.timestamp)
                .all()
            )
        return actions


def remove_action_by_id(action_id: int):
    with SessionLocal() as db_session:
        try:
            # Fetch the action to be deleted
            action_to_delete = (
                db_session.query(UserAction)
                .filter(UserAction.id == action_id)
                .one_or_none()
            )

            if action_to_delete:
                # Mark the action as deleted instead of removing it
                action_to_delete.deleted = True
                db_session.commit()
                print(f"Action with ID {action_id} has been marked as deleted.")
            else:
                print(f"No action found with ID {action_id}.")
        except Exception as e:
            db_session.rollback()
            print(f"An error occurred: {e}")


async def async_remove_action_by_id(action_id: int):
    async with AsyncSessionLocal() as async_db_session:
        try:
            # Fetch the action to be deleted
            async with async_db_session.begin():
                result = await async_db_session.execute(
                    select(UserAction).filter(UserAction.id == action_id)
                )
                action_to_delete = result.scalar_one_or_none()

                if action_to_delete:
                    # Mark the action as deleted instead of removing it
                    action_to_delete.deleted = True
                    await async_db_session.commit()
                    print(f"Action with ID {action_id} has been marked as deleted.")
                else:
                    print(f"No action found with ID {action_id}.")
        except Exception as e:
            await async_db_session.rollback()
            print(f"An error occurred: {e}")


def recover_item_by_id(item_id: int):
    with SessionLocal() as db_session:
        try:
            # Fetch the item to be recovered
            item_to_recover = (
                db_session.query(UserAction)
                .filter(UserAction.id == item_id)
                .one_or_none()
            )

            if item_to_recover:
                # Mark the item as not deleted to recover it
                item_to_recover.deleted = False
                db_session.commit()
                print(f"Item with ID {item_id} has been recovered.")
            else:
                print(f"No item found with ID {item_id}.")
        except Exception as e:
            db_session.rollback()
            print(f"An error occurred: {e}")


async def async_recover_item_by_id(item_id: int):
    async with AsyncSessionLocal() as async_db_session:
        try:
            # Fetch the item to be recovered
            async with async_db_session.begin():
                result = await async_db_session.execute(
                    select(UserAction).filter(UserAction.id == item_id)
                )
                item_to_recover = result.scalar_one_or_none()

                if item_to_recover:
                    # Mark the item as not deleted to recover it
                    item_to_recover.deleted = False
                    await async_db_session.commit()
                    print(f"Item with ID {item_id} has been recovered.")
                else:
                    print(f"No item found with ID {item_id}.")
        except Exception as e:
            await async_db_session.rollback()
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    async_create_database()

    all_value = get_all_actions_sorted(username="testmath0")
    for i in all_value:
        print(i.action, i.value, i.timestamp)
