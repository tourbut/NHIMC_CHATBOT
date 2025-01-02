from app.models import *
from app.src.schemas import users as user_schema
from sqlmodel import Session, select
from app.src.utils.security import get_password_hash, verify_password
from app.src.utils.fromOracle import get_isis_user

async def get_user_by_empl_no(*, session: Session, empl_no: str) -> user_schema.GetUserAndDept | None:
    statement = select(User.id,
                       User.empl_no,
                       User.name,
                       User.password,
                       User.is_admin,
                       User.is_active,
                       Dept.dept_cd,
                       Dept.dept_nm).where(User.empl_no == empl_no,
                                           UserDept.user_id == User.id,
                                           Dept.id == UserDept.dept_id)
    session_user = await session.exec(statement)
    return session_user.first()

async def authenticate(*, session: Session, empl_no: str, password: str) -> user_schema.GetUserAndDept | None:
    db_user = await get_user_by_empl_no(session=session, empl_no=empl_no)
    isis_user = await get_isis_user(empl_no)
    if not db_user:
        
        if isis_user:
            user = user_schema.UserCreate(empl_no=isis_user[0],
                                        password=isis_user[1],
                                        name=isis_user[2],)
            
            if await verify_password(password, user.password):
                db_user = User.model_validate(user)
                session.add(db_user)
                
                statement = select(Dept).where(Dept.dept_cd == isis_user[3])
                db_dept = await session.exec(statement)
                dept = db_dept.first()
                db_userdept = UserDept(user_id=db_user.id, dept_id=dept.id)
                session.add(db_userdept)
                            
                await session.commit()
                await session.refresh(db_user)
                
                rtn = user_schema.GetUserAndDept(id=db_user.id,
                                                 empl_no=db_user.empl_no,
                                                 name=db_user.name,
                                                 is_admin=db_user.is_admin,
                                                 is_active=db_user.is_active,
                                                 dept_cd=dept.dept_cd)
                
                return rtn
            else:
                return None
        else:    
            return None
    else: 
        if isis_user:
            if db_user.password != isis_user[1]:
                db_user.password = isis_user[1]
                await session.commit()
                await session.refresh(db_user)
                
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