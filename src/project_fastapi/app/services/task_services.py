from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_, Null
from ..schemas import TaskInput, TaskUpdate, CommentCreate
from ..models import (
    UserModel,
    ProjectMemberModel,
    ProjectModel,
    TaskModel,
    CommnentModel,
    AttachmentModel,
    TaskStatus,
)
from collections.abc import Callable
from datetime import datetime, timezone
from fastapi import UploadFile
from ..utils import save_a_file
from typing import Any

find_member_in_project: Callable[[Session, int, int], ProjectMemberModel | None] = (
    lambda the_data, project_id, member_id: the_data.query(ProjectMemberModel)
    .options(joinedload(ProjectMemberModel.user))
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

find_attachment_by_id: Callable[[Session, int], list[AttachmentModel]] = (
    lambda the_data, task_id: the_data.query(AttachmentModel)
    .filter(AttachmentModel.task_id == task_id)
    .all()
)

find_comment_by_id: Callable[[Session, int], list[CommnentModel]] = (
    lambda the_data, task_id: the_data.query(CommnentModel)
    .filter(CommnentModel.task_id == task_id)
    .all()
)

find_user_by_user_id: Callable[[Session, int], UserModel | None] = (
    lambda the_data, user_id: the_data.query(UserModel)
    .filter(UserModel.id == user_id)
    .first()
)

find_task_by_task_id_and_user_id: Callable[[Session, int], TaskModel | None] = (
    lambda the_data, task_id: the_data.query(TaskModel)
    .filter(TaskModel.id == task_id)
    .first()
)


def post_a_task_in_project(
    db: Session, id: int, data: TaskInput, curren_user: UserModel
):
    if data.assignee_id is None:
        data.assignee_id = curren_user.id
    check_project = find_project_by_id(db, id)
    check_member = find_member_in_project(db, id, curren_user.id)
    check_user = find_user_by_user_id(db, data.assignee_id)

    check_assignee_in_project = find_member_in_project(db, id, data.assignee_id)
    if check_project is None:
        return "NOT FOUND THE PROJECT ! "
    if check_member is None:
        return "USER NOT IN THAT PROJECT !"
    if check_user is None:
        return "NOT FOUND USER !"
    if check_project.is_delete:
        return "THE PROJECT HAVE BEEN DELETE !"
    if check_assignee_in_project is None:
        return "ASSIGNEE NOT IN THE PROJECT !"
    if not check_user.is_active:
        return "THAT ASSIGNEE IS NOT ACTIVATE"
    try:
        new_data = TaskModel(
            project_id=id,
            title=data.title,
            description=data.description,
            assignee_id=data.assignee_id,
            status=data.status,
            priority=data.priority,
            due_date=data.due_date,
            create_at=data.create_at,
            create_by=curren_user.id,
        )
        db.add(new_data)
        db.commit()
        db.refresh(new_data)
    except IntegrityError:
        db.rollback()
        raise Exception("Lỗi liên quan đến database !")
    return new_data


def get_all_task_in_project(
    db: Session,
    project_id: int,
    current_user: UserModel,
    status: str | None,
    priority: str | None,
    assignee: int | None,
    title: str | None,
    limit: int | None,
    offset: int | None,
    sort_by: str | None,
    is_overdue: bool,
    sort_by_priority: bool
):
    check_project = find_project_by_id(db, project_id)
    check_member_in_project = find_member_in_project(db, project_id, current_user.id)

    if check_project is None:
        return "NOT FOUND THE PROJECT ! "
    if check_project.is_delete:
        return "THE PROJECT HAVE BEEN DELETE !"
    if check_member_in_project is None:
        return "USER NOT IN THAT PROJECT !"

    the_task = (
        db.query(TaskModel)
        .options(joinedload(TaskModel.comments))
        .options(joinedload(TaskModel.attachments))
        .filter(TaskModel.project_id == project_id, TaskModel.is_delete != True)
    )

    if status is not None:
        the_task = the_task.filter(TaskModel.status == status)
    if priority is not None:
        the_task = the_task.filter(TaskModel.priority == priority)
    if assignee is not None:
        the_task = the_task.filter(TaskModel.assignee_id == assignee)
    if title is not None:
        the_task = the_task.filter(
            or_(
                TaskModel.description.ilike(f"%{title}%"),
                TaskModel.title.ilike(f"%{title}%")
            
            )
        )

    if is_overdue:
        the_task = the_task.filter(TaskModel.due_date < datetime.now(timezone.utc), TaskModel.status != TaskStatus.DONE)
    order_conditions:list[TaskModel] = []
    if sort_by_priority:
        order_conditions.append(TaskModel.priority_num.asc())

    if sort_by == "asc":
        order_conditions.append(TaskModel.create_at.asc())
    elif sort_by == "desc":
        order_conditions.append(TaskModel.create_at.desc())

    if order_conditions:
        the_task = the_task.order_by(*order_conditions)
    if limit is not None:
        if limit > 20:
            limit = 20
        the_task = the_task.limit(limit=limit)
    if offset is not None:
        the_task = the_task.offset(offset=offset)
    return the_task.all()
def get_all_task_you_assign_in_project(db:Session, current_user: UserModel):
    return db.query(TaskModel).filter(TaskModel.assignee_id == current_user.id).all()

def count_task_in_project(db: Session, current_user: UserModel, id: int):
    check_user_in_project = find_member_in_project(db, id, current_user.id)
    if check_user_in_project is None:
        return "YOU DONT HAVE IN THIS PROJECT"
    done_task = 0
    the_task = db.query(TaskModel).filter(TaskModel.project_id == id).all()
    for t in the_task:
        if t.status == TaskStatus.DONE:
            done_task += 1
    return {
        "total_tasks": len(the_task),
        "done_tasks": done_task
    }
            
def get_detail_task_by_task_id(db: Session, task_id: int, current_user: UserModel) -> dict[str, Any] | str:
    check_task_exists = find_task_by_task_id_and_user_id(db, task_id)
    if check_task_exists is None:
        return "NOT FOUND THAT TASK !"
    if check_task_exists.is_delete:
        return "THIS TASK IS DELETED !"
    check_user_in_project = find_member_in_project(
        db, check_task_exists.project_id, current_user.id
    )
    if check_user_in_project is None:
        return "USER NOT IN PROJECT !"
    check_project_exists = find_project_by_id(db, check_user_in_project.project_id)
    if check_project_exists is None:
        return "PROJECT NOT EXISTS !"
    if check_project_exists.is_delete:
        return "PROJECT HAVE DELETED !"
    return {
        "id": check_task_exists.id,
        "project_id": check_task_exists.project_id,
        "title": check_task_exists.title,
        "description": check_task_exists.description,
        "comments": check_task_exists.comments,
        "attachments": check_task_exists.attachments,
        "assign": find_user_by_user_id(db, check_task_exists.assignee_id),
        "status": check_task_exists.status,
        "priority": check_task_exists.priority,
        "due_date": check_task_exists.due_date,
        "create_at": check_task_exists.create_at,
        "create": find_user_by_user_id(db, check_task_exists.create_by)
    }


def patch_task(
    db: Session, task_id: int, current_user: UserModel, data_update: TaskUpdate
):
    check_task_exists = find_task_by_task_id_and_user_id(db, task_id)
    if check_task_exists is None:
        return "NOT FOUND THAT TASK !"
    if check_task_exists.is_delete:
        return "THIS TASK IS DELETED !"
    check_user_in_project = find_member_in_project(
        db, check_task_exists.project_id, current_user.id
    )
    if check_user_in_project is None:
        return "USER NOT IN PROJECT !"
    check_project_exists = find_project_by_id(db, check_user_in_project.project_id)
    if check_project_exists is None:
        return "PROJECT NOT EXISTS !"
    if check_project_exists.is_delete:
        return "PROJECT HAVE DELETED !"

    if (
        check_task_exists.assignee_id != current_user.id
        and check_project_exists.owner_id != current_user.id
    ):
        return "USER NOT HAVE PREMISSION TO UPDATE TASK !"
    if check_project_exists.owner_id == current_user.id:
        if data_update.assignee_id is None:
            data_update.assignee_id = current_user.id
        check_assignee_exists = find_user_by_user_id(db, data_update.assignee_id)
        if check_assignee_exists is None:
            return "ASSIGNEE NOT EXISTS !"
        if not check_assignee_exists.is_active:
            return "THAT ASSIGNEE IS NOT ACTIVATE"
        check_assignee_in_project = find_member_in_project(
            db, check_task_exists.project_id, data_update.assignee_id
        )
        if check_assignee_in_project is None:
            return "ASSIGNEE NOT IN PROJECT !"
        for key, value in data_update.model_dump(exclude_unset=True).items():
            setattr(check_task_exists, key, value)
        if data_update.status == TaskStatus.DONE:
            check_task_exists.completed_at = datetime.now(timezone.utc)
        else:
            check_task_exists.completed_at = None
        db.commit()
        db.refresh(check_task_exists)
        return check_task_exists
    if check_task_exists.assignee_id == current_user.id:
        check_task_exists.status = data_update.status
        db.commit()
        db.refresh(check_task_exists)
        return check_task_exists


def delete_task(db: Session, current_user: UserModel, task_id: int):
    check_task_exists = find_task_by_task_id_and_user_id(db, task_id)
    if check_task_exists is None:
        return "NOT FOUND THAT TASK !"
    if check_task_exists.is_delete:
        return "THIS TASK IS ALREADY DELETED !"
    check_user_in_project = find_member_in_project(
        db, check_task_exists.project_id, current_user.id
    )
    if check_user_in_project is None:
        return "USER NOT IN PROJECT !"
    check_project_exists = find_project_by_id(db, check_user_in_project.project_id)
    if check_project_exists is None:
        return "PROJECT NOT EXISTS !"
    if check_project_exists.is_delete:
        return "PROJECT HAVE DELETED !"
    if check_task_exists.status in [TaskStatus.DONE, TaskStatus.IN_PROGRESS]:
        return "THIS TASK IS IN PROGRESS OR DONE !"
    relation_attachement = find_attachment_by_id(db, task_id)
    relation_comment = find_comment_by_id(db, task_id)
    if len(relation_attachement) > 0 or len(relation_comment) > 0:
        return "NOT DELETED HAVE DATA"
    if (
        check_task_exists.create_by != current_user.id
        and check_project_exists.owner_id != current_user.id
    ):
        return "USER NOT HAVE PREMISSION TO UPDATE TASK !"

    check_task_exists.is_delete = True
    db.query(AttachmentModel).filter(
        AttachmentModel.task_id == task_id, AttachmentModel.is_delete.is_(False)
    ).update({"is_delete": True}, synchronize_session=False)
    db.commit()
    db.refresh(check_task_exists)
    return "DELETE SUCCESSFUL"


def create_a_new_comment(
    db: Session, comment_create: CommentCreate, task_id: int, current_user: UserModel
):
    check_task_exists = find_task_by_task_id_and_user_id(db, task_id)
    if check_task_exists is None:
        return "NOT FOUND THAT TASK !"
    if check_task_exists.is_delete:
        return "THIS TASK IS DELETED !"
    check_user_in_project = find_member_in_project(
        db, check_task_exists.project_id, current_user.id
    )
    if check_user_in_project is None:
        return "USER NOT IN PROJECT !"
    check_project_exists = find_project_by_id(db, check_user_in_project.project_id)
    if check_project_exists is None:
        return "PROJECT NOT EXISTS !"
    if check_project_exists.is_delete:
        return "PROJECT HAVE DELETED !"

    new_data_comment = CommnentModel(
        content=comment_create.content,
        task_id=task_id,
        user_id=current_user.id,
    )
    try:
        db.add(new_data_comment)
        db.commit()
        db.refresh(new_data_comment)
    except IntegrityError:
        Exception("Lỗi liên quan đến dữ liệu")
    return new_data_comment


async def upload_file(
    db: Session, task_id: int, current_user: UserModel, upload_file: UploadFile
):
    check_task_exists = find_task_by_task_id_and_user_id(db, task_id)
    if check_task_exists is None:
        return "NOT FOUND THAT TASK !"
    if check_task_exists.is_delete:
        return "THIS TASK IS DELETED !"
    check_user_in_project = find_member_in_project(
        db, check_task_exists.project_id, current_user.id
    )

    if check_user_in_project is None:
        return "USER NOT IN PROJECT !"
    check_project_exists = find_project_by_id(db, check_user_in_project.project_id)
    if check_project_exists is None:
        return "PROJECT NOT EXISTS !"
    if check_project_exists.is_delete:
        return "PROJECT HAVE DELETED !"

    file_path, file_name, file_size = await save_a_file(upload_file)
    new_attachment_data = AttachmentModel(
        filename=file_name,
        file_path=file_path,
        file_type=upload_file.content_type,
        file_size=file_size,
        task_id=task_id,
        upload_by=current_user.id,
    )
    try:
        db.add(new_attachment_data)
        db.commit()
        db.refresh(new_attachment_data)
    except IntegrityError:
        Exception("Lỗi liên quan đến database !")

    return new_attachment_data



    