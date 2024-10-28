from app.models import *
from app.src.schemas import users as user_schema
from sqlmodel import Session, select
from app.src.utils.security import get_password_hash, verify_password


async def get_user_by_empl_no(*, session: Session, empl_no: str) -> User | None:
    statement = select(User).where(User.empl_no == empl_no)
    session_user = await session.exec(statement)
    return session_user.first()

async def authenticate(*, session: Session, empl_no: str, password: str) -> User | None:
    db_user = await get_user_by_empl_no(session=session, empl_no=empl_no)
    if not db_user:
        return None
    if not await verify_password(password, db_user.password):
        return None
    return db_user

async def create_user(*, session: Session, user_create: user_schema.UserCreate) -> User:
    
    db_obj = User.model_validate(
        user_create, update={"password": await get_password_hash(user_create.password)})
    
    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)
    return db_obj


async def update_detail(*, session: Session, user_detail: user_schema.UserDetail, user_id: uuid.UUID) -> User:
    detail = await session.get(User, user_id)
    
    if not detail:
        return None
    else:
        update_dict = user_detail.model_dump(exclude_unset=True)
        detail.sqlmodel_update(update_dict)
        detail.update_date = datetime.now()
        session.add(detail)
        await session.commit()
        await session.refresh(detail)

    return detail