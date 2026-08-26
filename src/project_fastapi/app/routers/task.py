from fastapi import (
    APIRouter,
    status,
    HTTPException,
    Path,
    Depends,
    Query,
    File,
    UploadFile,
)
from ..db import DataBase
from fastapi.requests import Request
from ..schemas import (
    TaskInput,
    TaskResponse,
    TaskUpdate,
    TaskResponseButForGetListTask,
    CommentCreate,
    CommentResponse,
    AttachmentResponse,
)
from ..models import UserModel, TaskPriority, TaskStatus
from ..services import (
    post_a_task_in_project,
    get_all_task_in_project,
    get_detail_task_by_task_id,
    patch_task,
    delete_task,
    create_a_new_comment,
    upload_file,
)
from ..responses import StandardResponse
from ..dependencies import get_current_user
from ..core import limit
from typing import Literal

router = APIRouter(prefix="/task", tags=["Task"])


@router.post(
    "/projects/{id}/task",
    response_model=StandardResponse[TaskResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Thêm Task vào dự án đó",
    description="AI TRONG PROJECT CŨNG CÓ QUYỀN ĐỂ CÓ THỂ THÊM TASK VÀO DỰ ÁN, NGƯỜI THÊM TASK ĐÓ SẼ CÓ QUYỀN THẤP HƠN VỚI OWNER NHƯNG SẼ CAO HƠN ASSIGNEE",
)
@limit.limit("5/minute")  # type: ignore
def create_new_task(
    request: Request,
    db: DataBase,
    data_create: TaskInput,
    current_user: UserModel = Depends(get_current_user),
    id: int = Path(...),
):
    check = post_a_task_in_project(db, id, data_create, current_user)
    if check == "NOT FOUND THE PROJECT ! ":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": f"Không tìm thấy project của id là {id}",
                "error": f"NOT FOUND PROJECT ID LIKE {id}",
            },
        )
    if check == "NOT FOUND USER !":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Người dùng không tồn tại",
                "error": "USER NOT EXISTS !",
            },
        )
    if check == "THE PROJECT HAVE BEEN DELETE !":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Dự án này đã bị xóa !",
                "error": "THIS PROJECT HAVE BEEN DELETE !",
            },
        )
    if check == "USER NOT IN THAT PROJECT !":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Người dùng không có trong dự án đó !",
                "error": "THAT USER NOT HAVE PREMISSION IN THE PROJECT !",
            },
        )
    if check == "ASSIGNEE NOT IN THE PROJECT !":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Người được giao task không thuộc dự án này !",
                "error": "THIS ASSIGNEE NOT IN THE PROJECT !",
            },
        )
    return StandardResponse(
        StatusCode=status.HTTP_201_CREATED,
        Message="Tạo task thành công !",
        Error=None,
        Data=check,
        Path=request.url.path,
    )


@router.get(
    "/projects/{project_id}/tasks",
    response_model=StandardResponse[list[TaskResponseButForGetListTask]],
    status_code=status.HTTP_200_OK,
    summary="Xem danh sách task thuộc trong dự án",
    description="AI TRONG PROJECT ĐÓ ĐỀU CÓ QUYỀN XEM DANH SÁCH CÁC TASK THUỘC DỰ ÁN ĐÓ, KHÔNG ĐƯỢC LỘ DANH SÁCH TASK THUỘC PROJECT KHÁC NẾU NGƯỜI ĐÓ KHÔNG THUỘC PROJECT ĐÓ, ĐỒNG THỜI HỖ TRỢ TÌM KIẾM THEO TÊN DỰ ÁN, NGƯỜI PHỤ TRÁCH DỰ ÁN, TRẠNG THÁI VÀ ĐỘ ƯU TIÊN, PHÂN TRANG VÀ SORT THEO DUE_DATE",
)
@limit.limit("20/minute")  # type: ignore
def get_list_of_task_filter(
    request: Request,
    db: DataBase,
    current_user: UserModel = Depends(get_current_user),
    project_id: int = Path(...),
    statu: Literal[TaskStatus.DONE, TaskStatus.TODO, TaskStatus.IN_PROGRESS] = Query(
        default=None
    ),
    priority: Literal[TaskPriority.HIGH, TaskPriority.LOW, TaskPriority.MEDIUM] = Query(
        default=None
    ),
    assignee: int = Query(default=None),
    title: str = Query(default=None),
    limit: int = Query(default=None),
    offset: int = Query(default=None),
    sort_by: Literal["asc", "desc"] = Query(default="asc"),
):
    check = get_all_task_in_project(
        db,
        project_id,
        current_user,
        statu,
        priority,
        assignee,
        title,
        limit,
        offset,
        sort_by,
    )

    if check == "NOT FOUND THE PROJECT ! ":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không tìm thấy dự án này !",
                "error": "NOT FOUND THAT PROJECT !",
            },
        )
    if check == "THE PROJECT HAVE BEEN DELETE !":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Dự án này đã được xóa !",
                "error": "THIS PROJECT HAVE BEEN DELETED !",
            },
        )
    if check == "USER NOT IN THAT PROJECT !":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Người dùng không thuộc trong dự án này !",
                "error": "THIS USER NOT IN THAT PROJECT !",
            },
        )
    return StandardResponse(
        StatusCode=status.HTTP_200_OK,
        Message="Danh sách task",
        Error=None,
        Data=check,
        Path=request.url.path,
    )


@router.get(
    "/tasks/{task_id}",
    response_model=StandardResponse[TaskResponseButForGetListTask],
    status_code=status.HTTP_200_OK,
    summary="Xem chi tiết task đó",
    description="AI CŨNG CÓ QUYỀN XEM CHI TIẾT DỰ ÁN NHƯNG CHỈ THUỘC DỰ ÁN ĐÓ THÔI, KHÔNG ĐƯỢC LỘ TASK TỪ DỰ ÁN KHÁC",
)
@limit.limit("5/minute")  # type: ignore
def get_deltail_task(
    request: Request,
    db: DataBase,
    current_user: UserModel = Depends(get_current_user),
    task_id: int = Path(...),
):
    check = get_detail_task_by_task_id(db, task_id, current_user)
    if check == "NOT FOUND THAT TASK !":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": f"Không tìm thấy task có id là {task_id}",
                "error": f"NOT FOUND TASK HAVE {task_id}",
            },
        )
    if check == "THIS TASK IS DELETED !":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Task này đã bị xóa !",
                "error": "THIS TASK IS DELETED !",
            },
        )
    if check == "PROJECT NOT EXISTS !":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không tồn tại project này !",
                "error": "NOT FOUND THAT PROJECT !",
            },
        )
    if check == "PROJECT HAVE DELETED !":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Dự án đã được xóa !",
                "error": "THIS PROJECT HAVE BEEN DELETED !",
            },
        )
    if check == "USER NOT IN PROJECT !":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Bạn không có quyền để xem task trong project !",
                "error": "YOU DO NOT HAVE PREMISSION TO SEE DETAIL TASK !",
            },
        )
    return StandardResponse(
        StatusCode=status.HTTP_200_OK,
        Message="Láy chi tiết task thành công",
        Error=None,
        Data=check,
        Path=request.url.path,
    )


@router.patch(
    "/tasks/{task_id}",
    response_model=StandardResponse[TaskResponse],
    status_code=status.HTTP_200_OK,
    summary="Cập nhật task trong dự án",
    description="CHỈ DÀNH CHO NGƯỜI TẠO RA TASK ĐÓ VỚI NGƯỜI CHỦ TRÌ CỦA DỰ ÁN MỚI ĐƯỢC PHÉP CẬP NHẬT",
)
@limit.limit("5/minute")  # type: ignore
def update_task(
    request: Request,
    db: DataBase,
    data_update: TaskUpdate,
    current_user: UserModel = Depends(get_current_user),
    task_id: int = Path(...),
):
    check = patch_task(db, task_id, current_user, data_update)
    if check == "NOT FOUND THAT TASK !":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không tìm thấy task án này !",
                "error": f"NOT FOUND THAT TASK HAVE ID {task_id}",
            },
        )
    if check == "THIS TASK IS DELETED !":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Task này đã bị xóa !",
                "error": "THIS TASK IS DELETED !",
            },
        )
    if check == "PROJECT NOT EXISTS !":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không tồn tại project này !",
                "error": "NOT FOUND THAT PROJECT !",
            },
        )
    if check == "PROJECT HAVE DELETED !":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Dự án đã được xóa !",
                "error": "THIS PROJECT HAVE BEEN DELETED !",
            },
        )
    if check == "USER NOT IN PROJECT !":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Người dùng không có trong dự án này !",
                "error": "USER NOT HAVE IN THE PROJECT ",
            },
        )
    if check == "USER NOT HAVE PREMISSION TO UPDATE TASK !":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Bạn không có quyền để cập nhật task trong project !",
                "error": "YOU DO NOT HAVE PREMISSION TO UPDATE TASK !",
            },
        )
    if check == "ASSIGNEE NOT EXISTS !":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không tồn tại người dùng này !",
                "error": "NOT FOUND THAT ASSIGNEE USER !",
            },
        )
    if check == "ASSIGNEE NOT IN PROJECT !":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Người được giao task không thuộc dự án này !",
                "error": "THIS ASSIGNEE NOT IN THE PROJECT !",
            },
        )

    return StandardResponse(
        StatusCode=status.HTTP_200_OK,
        Message="Cập nhật task thành công !",
        Error=None,
        Data=check,
        Path=request.url.path,
    )


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa task trong dự án (Xóa mềm)",
    description="CHỈ DÀNH CHO NGƯỜI TẠO RA TASK ĐÓ VỚI NGƯỜI CHỦ TRÌ CỦA DỰ ÁN MỚI ĐƯỢC PHÉP XÓA",
)
@limit.limit("5/minute")  # type: ignore
def delete_a_task(
    request: Request,
    db: DataBase,
    current_user: UserModel = Depends(get_current_user),
    task_id: int = Path(...),
):
    check = delete_task(db, current_user, task_id)
    if check == "NOT FOUND THAT TASK !":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không tìm thấy task án này !",
                "error": f"NOT FOUND THAT TASK HAVE ID {task_id}",
            },
        )
    if check == "THIS TASK IS ALREADY DELETED !":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Task này đã bị xóa !",
                "error": "THIS TASK HAS ALREADY DELETED !",
            },
        )
    if check == "PROJECT NOT EXISTS !":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không tồn tại project này !",
                "error": "NOT FOUND THAT PROJECT !",
            },
        )
    if check == "PROJECT HAVE DELETED !":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Dự án đã được xóa !",
                "error": "THIS PROJECT HAVE BEEN DELETED !",
            },
        )
    if check == "USER NOT IN PROJECT !":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Người dùng không có trong dự án này !",
                "error": "USER NOT HAVE IN THE PROJECT ",
            },
        )
    if check == "USER NOT HAVE PREMISSION TO UPDATE TASK !":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Bạn không có quyền để xóa task trong project !",
                "error": "YOU DO NOT HAVE PREMISSION TO DELETE TASK !",
            },
        )
    if check == "DELETE SUCCESSFUL":
        return


@router.post(
    "/{task_id}/comments",
    response_model=StandardResponse[CommentResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Thêm Comment vào trong task thuộc dự án",
    description="Ai trong  dự án đều có thể thêm comment vào trong dự án này"
)
def add_a_commment(
    request: Request,
    db: DataBase,
    comment_create: CommentCreate,
    current_user: UserModel = Depends(get_current_user),
    task_id: int = Path(...),
):
    check = create_a_new_comment(db, comment_create, task_id, current_user)
    if check == "NOT FOUND THAT TASK !":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không tìm thấy task án này !",
                "error": f"NOT FOUND THAT TASK HAVE ID {task_id}",
            },
        )
    if check == "THIS TASK IS DELETED !":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Task này đã bị xóa !",
                "error": "THIS TASK IS DELETED !",
            },
        )
    if check == "PROJECT NOT EXISTS !":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không tồn tại project này !",
                "error": "NOT FOUND THAT PROJECT !",
            },
        )
    if check == "PROJECT HAVE DELETED !":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Dự án đã được xóa !",
                "error": "THIS PROJECT HAVE BEEN DELETED !",
            },
        )
    if check == "USER NOT IN PROJECT !":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Người dùng không có trong dự án này !",
                "error": "USER NOT HAVE IN THE PROJECT ",
            },
        )
    return StandardResponse(
        StatusCode=status.HTTP_201_CREATED,
        Message="Thêm thành công một comment",
        Error=None,
        Data=check,
        Path=request.url.path,
    )


@router.post(
    "/{task_id}/attachments",
    response_model=StandardResponse[AttachmentResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Thêm file vào trong task",
    description="AI TRONG DỰ ÁN ĐỀU CÓ THỂ THÊM FILE VÀO TRONG DỰ ÁN ĐÓ "
)
async def create_a_attachments(
    request: Request,
    db: DataBase,
    current_user: UserModel = Depends(get_current_user),
    task_id: int = Path(...),
    upload_file_in: UploadFile = File(...),
):
    check = await upload_file(db, task_id, current_user, upload_file_in)
    if check == "NOT FOUND THAT TASK !":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không tìm thấy task án này !",
                "error": f"NOT FOUND THAT TASK HAVE ID {task_id}",
            },
        )
    if check == "THIS TASK IS DELETED !":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Task này đã bị xóa !",
                "error": "THIS TASK IS DELETED !",
            },
        )
    if check == "THIS TASK IS ALREADY DELETED !":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Task này đã bị xóa !",
                "error": "THIS TASK HAS ALREADY DELETED !",
            },
        )
    if check == "PROJECT NOT EXISTS !":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không tồn tại project này !",
                "error": "NOT FOUND THAT PROJECT !",
            },
        )
    if check == "PROJECT HAVE DELETED !":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Dự án đã được xóa !",
                "error": "THIS PROJECT HAVE BEEN DELETED !",
            },
        )
    if check == "USER NOT IN PROJECT !":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Người dùng không có trong dự án này !",
                "error": "USER NOT HAVE IN THE PROJECT ",
            },
        )
    return StandardResponse(
        StatusCode=status.HTTP_201_CREATED,
        Message="Thêm file thành công",
        Error=None,
        Data=check,
        Path=request.url.path,
    )
