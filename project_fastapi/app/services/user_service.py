from sqlalchemy.orm import Session
from app.models import UserModel

def search_user_by_name_email_or_status(
    db: Session,
    name: str | None = None,
    email: str | None = None,
    status: bool | None = None,
    skip: int = 0,
    limit: int  = 100
):
    the_list = db.query(UserModel)
    if name:
        the_list = the_list.filter(UserModel.full_name.ilike(f"%{name}%"))
    if email:
        the_list = the_list.filter(UserModel.email.ilike(f"%{email}%"))
        
    if status is not None:
        the_list = the_list.filter(UserModel.is_active == status)
    return  the_list.offset(skip).limit(limit).all()