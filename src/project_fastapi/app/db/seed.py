import random
from datetime import datetime, timedelta

from faker import Faker

from ..core import get_password_hash
from ..models import (
    ProjectMemberModel,
    ProjectMemberRole,
    ProjectModel,
    TaskModel,
    TaskPriority,
    TaskStatus,
    UserModel,
    UserRole,
)
from .database import SessionLocal

fake = Faker("vi_VN")

def seed_data():
    db = SessionLocal()
    try:
        print("Đang tạo dữ liệu mẫu !")
        role = [UserRole.ADMIN, UserRole.USER]
        users:list[UserModel] = []
        for _ in range(10):
                user = UserModel(
                    email = fake.email(),
                    full_name = fake.user_name(),
                    role = random.choice(role),
                    password_hash = get_password_hash("Ni345678"),
                    created_at = datetime.now() - timedelta(days=random.randint(30, 60))
                )
                users.append(user)
        db.add_all(users)
        db.commit()
        for u in users:
            db.refresh(u)
        
        projects:list[ProjectModel] = []
        for _ in range(3):
            owner = random.choice(users)
            project = ProjectModel(
                name = fake.catch_phrase(),
                description = fake.text(max_nb_chars=150),
                owner_id = owner.id,
                create_at = datetime.now() - timedelta(days=random.randint(15, 30))
            )
            projects.append(project)
            
        db.add_all(projects)
        db.commit()
        for p in projects:
            db.refresh(p)
            
        project_members:list[ProjectMemberModel] = []
        member_role = [ProjectMemberRole.OWNER, ProjectMemberRole.MEMBER]
        member_pair = set()
        for project in projects:
            member_pair.add((project.id, project.owner_id))
            project_members.append(
                ProjectMemberModel(
                    project_id = project.id,
                    user_id = project.owner_id,
                    role = ProjectMemberRole.OWNER,
                    joined_at = project.create_at
                )
            )
        
            orther_user = [u for u in users if u.id != project.owner_id]
            select_users = random.sample(
                orther_user, k = min(len(orther_user), random.randint(2, 4))
            )
            for user in select_users:
                if (project.id, user.id) not in member_pair:
                    member_pair.add((project.id, user.id))
                    project_members.append(
                        ProjectMemberModel(
                            project_id=project.id,
                            user_id=user.id,
                            role=random.choice(member_role[1:]), 
                            joined_at=datetime.now()
                            - timedelta(days=random.randint(1, 10)),
                        )
                        )
            db.add_all(project_members)
            db.commit()
            
            
        tasks:list[TaskModel] = []
        statuses = [TaskStatus.IN_PROGRESS, TaskStatus.DONE, TaskStatus.TODO]
        priorities = [TaskPriority.HIGH, TaskPriority.LOW, TaskPriority.MEDIUM, TaskPriority.URGENT]
        priorities_num = {
            TaskPriority.URGENT: 1,
            TaskPriority.HIGH : 2,
            TaskPriority.MEDIUM: 3,
            TaskPriority.LOW: 4
        }
        for project in projects:
            current_project_member_ids = [
                m.user_id for m in project_members if m.project_id == project.id
        ]
            for _ in range(10):
                created_date = datetime.now() - timedelta(days=random.randint(1, 10))
                priority = random.choice(priorities)
                task = TaskModel(
                    project_id=project.id,
                    title=fake.sentence(nb_words=6),
                    description=fake.paragraph(nb_sentences=2),
                    assignee_id=random.choice(
                        current_project_member_ids
                    ), 
                    status=random.choice(statuses),
                    priority=priority,
                    priority_num = priorities_num[priority],
                    due_date=created_date + timedelta(days=random.randint(5, 15)),
                    create_at=created_date,
                    create_by = random.choice(current_project_member_ids)
                )
                tasks.append(task)

            db.add_all(tasks)
            db.commit()

        print('Seed dữ liệu thành công!')

    except Exception as e:
        print(f'Lỗi khi seed dữ liệu: {e}')
        db.rollback()
    finally:
        db.close()


if __name__ == '__main__':
  seed_data()