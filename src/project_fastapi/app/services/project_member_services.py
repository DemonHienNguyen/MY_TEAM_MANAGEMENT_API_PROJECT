from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import case
from ..models import ProjectModel, UserModel, ProjectMemberModel, ProjectMemberRole
from ..schemas import ProjectMemberInput
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

find_list_of_member_in_the_project: Callable[
    [Session, int], list[ProjectMemberModel]
] = (
    lambda the_data, project_id: the_data.query(ProjectMemberModel)
    .filter(
        ProjectMemberModel.project_id == project_id,
        ProjectMemberModel.is_delete != True,
    )
    .all()
)


def create_member(
    db: Session,
    id: int,
    current_user: UserModel,
    data_in: ProjectMemberInput,
    role: str | None,
):
    member_role = role or ProjectMemberRole.VIEWER
    the_project_to_add_member = find_project_by_id(db, id)
    user_to_add_in_project = find_user_by_user_id(db, data_in.user_id)
    if the_project_to_add_member is None:
        return "NOT FOUND THE PROJECT !"
    # if the_project_to_add_member.owner_id != current_user.id:
    #     return "NOT PREMISSION TO DO THE PROJECT"
    if the_project_to_add_member.is_delete:
        return "THE PROJECT HAVE BEEN DELETE !"
    if user_to_add_in_project is None:
        return "NOT FOUND A USER !"
    if user_to_add_in_project.is_active == False:
        return "USER NOT ACTIVATE !"
    member_in_project = find_list_of_member_in_the_project(db, id)
    if len(member_in_project) >= 10:
        return "FULL OF MEMBER IN THE PROJECT"
    check_member_duplicate = find_member_in_project(db, id, data_in.user_id)
    if check_member_duplicate is None:
        try:
            new_data = ProjectMemberModel(
                project_id=id,
                user_id=data_in.user_id,
                role=member_role,
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
    role_case = case(
        (ProjectMemberModel.role == ProjectMemberRole.OWNER, 1),
        (ProjectMemberModel.role == ProjectMemberRole.MEMBER, 2),
        else_=3,
    )
    the_project_to_add_member = find_project_by_id(db, id)
    check_user_in_project = find_member_in_project(db, id, current_user.id)
    if the_project_to_add_member is None:
        return "NOT FOUND THE PROJECT !"
    if check_user_in_project is None:
        return "NOT PREMISSION TO SEE MEMBER IN THE PROJECT"
    if the_project_to_add_member.is_delete:
        return "THE PROJECT HAVE BEEN DELETE !"
    return (
        db.query(ProjectMemberModel)
        .options(joinedload(ProjectMemberModel.user))
        .filter(
            ProjectMemberModel.project_id == id, ProjectMemberModel.is_delete != True
        )
        .order_by(role_case)
        .all()
    )


def patch_member(
    db: Session, id: int, user_id: int, role: str, current_user: UserModel
):
    the_project_to_add_member = find_project_by_id(db, id)
    check_user_in_project = find_member_in_project(db, id, current_user.id)
    check_update_user_in_project = find_member_in_project(db, id, user_id)
    check_user_exists = find_user_by_user_id(db, user_id)
    if the_project_to_add_member is None:
        return "NOT FOUND THE PROJECT !"
    if check_user_in_project is None:
        return "USER NOT IN PROJECT !"
    if check_user_in_project.user_id != the_project_to_add_member.owner_id:
        return "NOT PREMISSION TO SEE MEMBER IN THE PROJECT"
    if the_project_to_add_member.is_delete:
        return "THE PROJECT HAVE BEEN DELETE !"
    if check_user_exists is None:
        return "USER IS NOT EXISTS !"
    if check_update_user_in_project is None:
        return "THIS MEMBER NOT IN THE PROJECT"
    check_update_user_in_project.role = role
    db.commit()
    db.refresh(check_update_user_in_project)
    return check_update_user_in_project


def delete_member(
    db: Session, id: int, user_id_to_delete: int, current_user: UserModel
):
    the_project_to_check = find_project_by_id(db, id)
    the_user_to_check = find_user_by_user_id(db, user_id_to_delete)
    check_user_in_that_project = find_member_in_project(db, id, user_id_to_delete)

    if the_project_to_check is None:
        return "NOT FOUND THE PROJECT !"
    if the_user_to_check is None:
        return "NOT FOUND USER !"
    # if the_project_to_check.owner_id != current_user.id:
    #     return "NOT PREMISSION TO DELETE THE MEMBER IN THE PROJECT"
    if the_project_to_check.is_delete:
        return "THE PROJECT HAVE BEEN DELETE !"
    if check_user_in_that_project is None:
        return "USER NOT IN THAT PROJECT !"
    if check_user_in_that_project.is_delete:
        return "THAT USER HAVE BEEN DELETED !"
    if check_user_in_that_project.role == ProjectMemberRole.OWNER:
        return "NOT DELETE THE OWNER OF PROJECT"
    check_user_in_that_project.is_delete = True
    db.commit()
    return "DELETE SUCCESSFULL !"
