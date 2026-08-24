from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from app.models import ProjectModel, UserModel, ProjectMemberModel, ProjectMemberRole
from app.schemas import ProjectMemberInput
from collections.abc import Callable
from datetime import datetime, timezone

find_member_in_project: Callable[[Session, int, int], ProjectMemberModel | None] = (
    lambda the_data, project_id, member_id: the_data.query(ProjectMemberModel)
    .filter(
        ProjectMemberModel.user_id == member_id,
        ProjectMemberModel.project_id == project_id,
    )
    .first()
)

find_project_by_id: Callable[[Session, int], ProjectModel | None] = (
    lambda the_data, project_id: the_data.query(ProjectModel)
    .filter(ProjectModel.id == project_id)
    .first()
)

find_user_by_user_id: Callable[[Session, int], UserModel | None] = (
    lambda the_data, user_id: the_data.query(UserModel)
    .filter(UserModel.id == user_id)
    .first()
)


def create_member(
    db: Session, id: int, current_user: UserModel, data_in: ProjectMemberInput
):
    the_project_to_add_member = find_project_by_id(db, id)
    user_to_add_in_project = find_user_by_user_id(db, data_in.user_id)
    if user_to_add_in_project is None:
        return "NOT FOUND A USER !"
    if the_project_to_add_member is None:
        return "NOT FOUND THE PROJECT !"
    if the_project_to_add_member.owner_id != current_user.id:
        return "NOT PREMISSION TO DO THE PROJECT"
    if the_project_to_add_member.is_delete:
        return "THE PROJECT HAVE BEEN DELETE !"
    check_member_duplicate = find_member_in_project(db, id, data_in.user_id)
    if check_member_duplicate is None:
        try:
            new_data = ProjectMemberModel(
                project_id=id,
                user_id=data_in.user_id,
                role="MEMBER",
                joined_at=datetime.now(timezone.utc),
            )
            db.add(new_data)
            db.commit()
            db.refresh(new_data)
        except IntegrityError:
            db.rollback()
            raise Exception("Lỗi liên quan đến Database")
        return new_data
    
    if check_member_duplicate.is_delete:
        check_member_duplicate.is_delete = False
        db.commit()
        return check_member_duplicate
    return "THE USER HAVE IN THE PROJECT !"
    


def get_members(db: Session, id: int, current_user: UserModel):
    the_project_to_add_member = find_project_by_id(db, id)
    check_user_in_project = find_member_in_project(
        db,id, current_user.id
    )
    if the_project_to_add_member is None:
        return "NOT FOUND THE PROJECT !"
    if check_user_in_project is None:
        return "NOT PREMISSION TO SEE MEMBER IN THE PROJECT"
    if the_project_to_add_member.is_delete:
        return "THE PROJECT HAVE BEEN DELETE !"
    return db.query(ProjectMemberModel).options(joinedload(ProjectMemberModel.user)).filter(ProjectMemberModel.project_id == id, ProjectMemberModel.is_delete != True).all()


def delete_member(db: Session, id: int, user_id_to_delete: int, current_user: UserModel):
    the_project_to_check = find_project_by_id(db, id)
    the_user_to_check = find_user_by_user_id(db, user_id_to_delete)
    check_user_in_that_project = find_member_in_project(db, id, user_id_to_delete)
    
    if the_project_to_check is None:
        return "NOT FOUND THE PROJECT !"
    if the_user_to_check is None:
        return "NOT FOUND USER !"
    if the_project_to_check.is_delete:
        return "THE PROJECT HAVE BEEN DELETE !"
    if the_project_to_check.owner_id != current_user.id:
        return "NOT PREMISSION TO DELETE THE MEMBER IN THE PROJECT"
    if check_user_in_that_project is None:
        return "USER NOT IN THAT PROJECT !"
    if check_user_in_that_project.role == ProjectMemberRole.OWNER or check_user_in_that_project.user_id == current_user.id:
        return "NOT DELETE THE OWNER OF PROJECT"
    check_user_in_that_project.is_delete = True
    db.commit()
    return "DELETE SUCCESSFULL !"
    