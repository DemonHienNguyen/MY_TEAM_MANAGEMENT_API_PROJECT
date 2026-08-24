from fastapi import APIRouter, status, HTTPException, Depends, Query, Path
from ..db import DataBase
from fastapi.requests import Request
from ..models import UserModel
from ..schemas import ProjectInput, ProjectResponse, ProjectUpdate
from ..responses import StandardResponse
from ..services import (
    post_project,
    get_projects,
    get_detail_project,
    path_project,
    delete_project,
)
from ..dependencies import get_current_user, Require_Admin_and_User
from ..core import limit, logger

router = APIRouter(prefix="/projects", tags=["Project"])


@router.post(
    "/",
    response_model=StandardResponse[ProjectResponse],
    dependencies=[Depends(Require_Admin_and_User)],
    status_code=status.HTTP_201_CREATED,
)
@limit.limit("5/minute")  # type: ignore
def create_new_project(
    request: Request,
    db: DataBase,
    project_intput: ProjectInput,
    currrent_user: UserModel = Depends(get_current_user),
):
    check = post_project(db, project_intput, currrent_user)
    if check == "NOT FOUND USER !":
        logger.error("KHÔNG TÌM THẤY USER")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "Không tìm thấy user !", "error": "NOT FOUND A USER"},
        )
    logger.info("TẠO DỰ ÁN THÀNH CÔNG")
    return StandardResponse(
        StatusCode=status.HTTP_201_CREATED,
        Message="Tạo dự án thành công !",
        Error=None,
        Data=check,
        Path=request.url.path,
    )


@router.get(
    "/",
    response_model=StandardResponse[list[ProjectResponse]],
    status_code=status.HTTP_200_OK,
)
@limit.limit("5/minute")  # type: ignore
def get_all_project(
    request: Request,
    db: DataBase,
    current_user: UserModel = Depends(get_current_user),
    keyword: str | None = Query(default=None),
):
    logger.info("LẤY DANH SÁCH DỰ ÁN THÀNH CÔNG !")
    return StandardResponse(
        StatusCode=status.HTTP_200_OK,
        Message="Lấy danh sách dự án thành công !",
        Data=get_projects(db, current_user, keyword),
        Error=None,
        Path=request.url.path,
    )


@router.get(
    "/{project_id}",
    response_model=StandardResponse[ProjectResponse],
    status_code=status.HTTP_200_OK,
)
@limit.limit("5/minute")  # type: ignore
def project_detail(
    request: Request,
    db: DataBase,
    project_id: int = Path(...),
    current_user: UserModel = Depends(get_current_user),
):
    check = get_detail_project(db, project_id=project_id, current_user=current_user)
    if check == "NOT FOUND THE PROJECT !":
        logger.error("KHÔNG TÌM THẤY DỰ ÁN")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không tìm thấy dự án như vậy !",
                "error": "NOT FOUND PROJECT !",
            },
        )
    if check == "NOT PREMISSION TO SEE THE PROJECT":
        logger.error("BẠN KHÔNG ĐỦ QUYỀN ĐỂ XEM CHI TIẾT DỰ ÁN")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Người dùng không thể xem chi tiết dự án này !",
                "error": "NOT HAVE PREMISSION TO SEE DETAIL !",
            },
        )
    if check == "THE PROJECT HAVE BEEN DELETE !":
        logger.error("DỰ ÁN ĐÃ BỊ XÓA !")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Người dùng không thể xem chi tiết dự án này !",
                "error": "THE PROJECT HAVE BEEN DELETE !",
            },
        )
    logger.info("LẤY THÀNH CÔNG CHI TIẾT DỰ ÁN")
    return StandardResponse(
        StatusCode=status.HTTP_200_OK,
        Error=None,
        Message="Chi tiết dự án !",
        Data=check,
        Path=request.url.path,
    )


@router.patch(
    "/{project_id}",
    response_model=StandardResponse[ProjectResponse],
    status_code=status.HTTP_200_OK,
)
@limit.limit("5/minute")  # type: ignore
def update_project(
    request: Request,
    db: DataBase,
    data_update: ProjectUpdate,
    project_id: int = Path(...),
    current_user: UserModel = Depends(get_current_user),
):
    check = path_project(db, project_id, current_user, data_update)
    if check == "NOT FOUND THE PROJECT !":
        logger.error("KHÔNG TÌM THẤY DỰ ÁN")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": f"Không tìm thấy project có id là {id}",
                "error": "NOT FOUND THIS PROJECT ID !",
            },
        )
    if check == "NOT PREMISSION TO UPDATE !":
        logger.error("BẠN KHÔNG ĐỦ QUYỀN ĐỂ CẬP NHẬT DỰ ÁN")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Bạn không có quyền để cập nhật",
                "error": "YOU DONT HAVE PREMISSION TO UPDATE PROJECT",
            },
        )
    logger.info("CẬP NHẬT DỰ ÁN")
    return StandardResponse(
        StatusCode=status.HTTP_200_OK,
        Message="Cập nhật dự án thành công !",
        Error=None,
        Data=check,
        Path=request.url.path,
    )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
@limit.limit("5/minute")  # type: ignore
def delete_a_project(
    request: Request,
    db: DataBase,
    project_id: int = Path(...),
    current_user: UserModel = Depends(get_current_user),
):
    check = delete_project(db, project_id, current_user)
    if check == "NOT FOUND THE PROJECT !":
        logger.error("KHÔNG TÌM THẤY DỰ ÁN")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": f"Không tìm thấy project có id là {id}",
                "error": "NOT FOUND THIS PROJECT ID !",
            },
        )
    if check == "NOT PREMISSION TO DELETE !":
        logger.error("BẠN KHÔNG ĐỦ QUYỀN ĐỂ XÓA")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Bạn không đủ quyền dể xóa !",
                "error": "YOU DON'T HAVE PREMISSION TO DELETE !",
            },
        )
    if check == "THE PROJECT HAVE BEEN DELETED !":
        logger.error("DỰ ÁN NÀY ĐÃ XÓA !")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Dự án này đã bị xóa !",
                "error": "THE PROJECT ARE HAVE BEEN DELETED ",
            },
        )
    if check == "DELETE SUCCESSFULL !":
        logger.info("XÓA THÀNH CÔNG")
        return
