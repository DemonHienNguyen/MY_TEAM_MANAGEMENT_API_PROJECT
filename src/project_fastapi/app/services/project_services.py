from sqlalchemy.orm import Session, joinedload, join
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone
from ..models import ProjectModel, UserModel, ProjectMemberModel, ProjectMemberRole, TaskModel
from ..schemas import ProjectInput, ProjectUpdate
from collections.abc import Callable

find_user_by_id: Callable[[Session, int], UserModel | None] = (
    lambda the_data, user_id: the_data.query(UserModel)
    .filter(UserModel.id == user_id)
    .first()
)

find_project_by_id: Callable[[Session, int], ProjectModel | None] = (
    lambda the_data, project_id: the_data.query(ProjectModel)
    .filter(ProjectModel.id == project_id)
    .first()
)

find_owner_project_by_id: Callable[[Session, int], ProjectMemberModel | None] = lambda the_data, user_id: the_data.query(ProjectMemberModel).filter(ProjectMemberModel.user_id == user_id, ProjectMemberModel.role == "OWNER").first()

def post_project(db: Session, project_in: ProjectInput, current: UserModel):
    user_find = find_user_by_id(db, int(current.id))
    if user_find is None:
        return "NOT FOUND USER !"
    the_project_duplicate_name = db.query(ProjectModel).filter(ProjectModel.name == project_in.name).first()
    if the_project_duplicate_name is not None:
        return "THE NAME PROJECT IS DUPLICATE !"
    try:
        new_project_data = ProjectModel(
            name=project_in.name,
            description=project_in.description,
            owner_id=user_find.id,
            create_at=datetime.now(timezone.utc),
        )
        db.add(new_project_data)
        db.flush()
        db.refresh(new_project_data)
        new_data_project_member = ProjectMemberModel(
            project_id=new_project_data.id,
            user_id=new_project_data.owner_id,
            role=ProjectMemberRole.OWNER,
            joined_at=new_project_data.create_at,
        )
        db.add(new_data_project_member)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise Exception("Lỗi liên quan đến Database")
    return new_project_data


def get_projects(db: Session, current_user: UserModel, keyword: str | None = None):
    the_projetct = (
        db.query(ProjectMemberModel)
        .join(ProjectMemberModel.project)
        .options(
            joinedload(ProjectMemberModel.project), joinedload(ProjectMemberModel.user)
        )
        .filter(ProjectMemberModel.user_id == current_user.id)
        .filter(ProjectModel.is_delete == False)
    )
    if keyword:
        the_projetct = the_projetct.filter(ProjectModel.name.ilike(f"%{keyword}%"))
    return [p.project for p in the_projetct.all()]


def get_detail_project(db: Session, current_user: UserModel, project_id: int):
    the_project = find_project_by_id(db, project_id)
    if the_project is None:
        return "NOT FOUND THE PROJECT !"
    if the_project.is_delete:
        return "THE PROJECT HAVE BEEN DELETE !"
    member_projetct = db.query(ProjectMemberModel).join(ProjectMemberModel.project).options(
        joinedload(ProjectMemberModel.project)
    ).filter(ProjectModel.id == the_project.id).all()
    the_user_in_project = [m.user_id for m in member_projetct]
    if current_user.id not in the_user_in_project:
        return "NOT PREMISSION TO SEE THE PROJECT"
    return the_project

def path_project(db:Session, id:int, current_user: UserModel, update_project: ProjectUpdate):
    the_project = find_project_by_id(db, id)
    if the_project is None:
        return "NOT FOUND THE PROJECT !"
    if current_user.id != the_project.owner_id:
        return "NOT PREMISSION TO UPDATE !"
    if the_project.is_delete:
        return "THE PROJECT HAVE BEEN DELETE !"
    the_project_duplicate_name = db.query(ProjectModel).filter(ProjectModel.name == update_project.name, ProjectModel.id != id).first()
    if the_project_duplicate_name is not None:
        return "THE NAME PROJECT IS DUPLICATE !"
    for key, value in update_project.model_dump(exclude_unset=True).items():
        setattr(the_project, key, value)
    db.commit()
    db.refresh(the_project)
    return the_project


def delete_project(db:Session, id: int, current_user: UserModel):
    the_project = find_project_by_id(db, id)
    if the_project is None:
        return "NOT FOUND THE PROJECT !"
    if the_project.owner_id != current_user.id:
        return "NOT PREMISSION TO DELETE !"
    if the_project.is_delete:
        return "THE PROJECT HAVE BEEN DELETED !"
    the_project.is_delete = True
    member_in_project = db.query(ProjectMemberModel).filter(ProjectMemberModel.project_id == the_project.id).all()
    for m in member_in_project:
        m.is_delete = True
    task_in_that_project = db.query(TaskModel).filter(TaskModel.project_id == the_project.id)
    for t in task_in_that_project:
        t.is_delete = True
    db.commit()
    return "DELETE SUCCESSFULL !"
    