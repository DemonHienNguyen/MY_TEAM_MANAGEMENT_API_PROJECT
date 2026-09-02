from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi.requests import Request

from ..core import limit, logger
from ..db import DataBase
from ..dependencies import Require_Admin_and_User, get_current_user
from ..models import ProjectMemberRole, UserModel
from ..responses import StandardResponse
from ..schemas import (
    ProjectInput,
    ProjectResponse,
    ProjectUpdate,
    UserResponseButForGetDetailProject,
)
from ..services import (
    delete_project,
    get_detail_project,
    get_projects,
    path_project,
    post_project,
)

router = APIRouter(prefix="/projects", tags=["Project"])


@router.post(
    "/",
    response_model=StandardResponse[ProjectResponse],
    dependencies=[Depends(Require_Admin_and_User)],
    status_code=status.HTTP_201_CREATED,
    summary="Tạo một dự án mới",
    description="TẠO MỘT DỰ ÁN MỚI DO NGƯỜI DÙNG TỰ TẠO RA, CÓ THỂ CHECK TÊN DỰ ÁN KHÔNG ĐƯỢC TRÙNG",
)
@limit.limit("10/minute")  # type: ignore
def create_new_project(
    request: Request,
    db: DataBase,
    project_intput: ProjectInput,
    currrent_user: UserModel = Depends(get_current_user),
):

    check = post_project(db, project_intput, currrent_user)
    if check == "NOT FOUND USER !":
        logger.warning("KHÔNG TÌM THẤY USER")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "Không tìm thấy user !", "error": "NOT FOUND A USER"},
        )
    if check == "THE NAME PROJECT IS DUPLICATE !":
        logger.warning("TÊN DỰ ÁN BỊ TRÙNG !")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "Tên dự án bị trùng !",
                "error": "NAME THE PROJECT IS DUPLICATE",
            },
        )
    if check == "NOT OVER 5 PROJECT !":
        logger.warning("KHÔNG ĐƯỢC QUÁ 5 DỰ ÁN")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Người dùng không được thêm hơn quá 5 dự án!",
                "error": "NOT ADD MORE PROJECT IF IS MORE THAN 5 !",
            },
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
    summary="Lấy danh sách dự án của người dùng",
    description="NGƯỜI DÙNG CÓ THỂ LẤY ĐƯỢC DANH SÁCH DỰ ÁN MÀ MÌNH THUỘC HOẶC LÀ NHỮNG DỰ ÁN MÀ MÌNH TẠO RA TRƯỚC ĐÓ (KHÔNG HIỆN VỚI NHỮNG DỰ ÁN ĐÃ XÓA)",
)
@limit.limit("5/minute")  # type: ignore
def get_all_project(
    request: Request,
    db: DataBase,
    current_user: UserModel = Depends(get_current_user),
    keyword: str | None = Query(default=None),
    role: Literal[ProjectMemberRole.OWNER, ProjectMemberRole.MEMBER] = Query(
        default=None
    ),
):
    logger.info("LẤY DANH SÁCH DỰ ÁN THÀNH CÔNG !")
    return StandardResponse(
        StatusCode=status.HTTP_200_OK,
        Message="Lấy danh sách dự án thành công !",
        Data=get_projects(db, current_user, keyword, role),
        Error=None,
        Path=request.url.path,
    )


@router.get(
    "/{project_id}",
    response_model=StandardResponse[dict[str, UserResponseButForGetDetailProject | ProjectResponse]],
    status_code=status.HTTP_200_OK,
    summary="Lấy chi tiết dự án đó",
    description="NGƯỜI DÙNG SẼ LẤY CHI TIẾT DỰ ÁN ĐÓ, NHỮNG NGƯỜI THUỘC DỰ ÁN ĐÓ MỚI CÓ THỂ XEM ĐƯỢC, KHÔNG CHO NGƯỜI NGOÀI XEM",
)
@limit.limit("5/minute")  # type: ignore
def project_detail(
    request: Request,
    db: DataBase,
    project_id: int = Path(...),
    current_user: UserModel = Depends(get_current_user),
):
    check, user = get_detail_project(
        db, project_id=project_id, current_user=current_user
    )
    if check == "NOT FOUND THE PROJECT !":
        logger.warning("KHÔNG TÌM THẤY DỰ ÁN")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Không tìm thấy dự án như vậy !",
                "error": "NOT FOUND PROJECT !",
            },
        )
    if check == "NOT PREMISSION TO SEE THE PROJECT":
        logger.warning("BẠN KHÔNG ĐỦ QUYỀN ĐỂ XEM CHI TIẾT DỰ ÁN")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Người dùng không thể xem chi tiết dự án này !",
                "error": "NOT HAVE PREMISSION TO SEE DETAIL !",
            },
        )
    if check == "THE PROJECT HAVE BEEN DELETE !":
        logger.warning("DỰ ÁN ĐÃ BỊ XÓA !")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Người dùng không thể xem chi tiết dự án này !",
                "error": "THE PROJECT HAVE BEEN DELETE !",
            },
        )
    format_data:dict[str, UserResponseButForGetDetailProject | ProjectResponse] = {"data": check, "owner_infor": user}
    logger.info("LẤY THÀNH CÔNG CHI TIẾT DỰ ÁN")
    return StandardResponse(
        StatusCode=status.HTTP_200_OK,
        Error=None,
        Message="Chi tiết dự án !",
        Data=format_data,
        Path=request.url.path,
    )


@router.patch(
    "/{project_id}",
    response_model=StandardResponse[ProjectResponse],
    status_code=status.HTTP_200_OK,
    summary="Cập nhật dự án",
    description="CHỈ DÀNH CHO NGƯỜI CHỦ CỦA DỰ ÁN ĐÓ (OWNER), NGƯỜI ĐÓ ĐƯỢC CẬP NHẬT DỰ ÁN, CÒN LẠI THÌ KHÔNG CHO PHÉP",
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
        logger.warning("KHÔNG TÌM THẤY DỰ ÁN")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": f"Không tìm thấy project có id là {project_id}",
                "error": "NOT FOUND THIS PROJECT ID !",
            },
        )
    if check == "NOT PREMISSION TO UPDATE !":
        logger.warning("BẠN KHÔNG ĐỦ QUYỀN ĐỂ CẬP NHẬT DỰ ÁN")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Bạn không có quyền để cập nhật",
                "error": "YOU DONT HAVE PREMISSION TO UPDATE PROJECT",
            },
        )
    if check == "THE PROJECT HAVE BEEN DELETE !":
        logger.warning("KHÔNG TÌM THẤY DỰ ÁN")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Project có id là {project_id} đã bị xóa",
                "error": "PROJECT HAVE BEEN DELETE !",
            },
        )
    if check == "NOT UPDATE THE_NAME_OF THE_PROJECT AFTER 7 DAYS":
        logger.warning("KHÔNG TÌM THẤY DỰ ÁN")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Project có id là {project_id} khong duoc cap nhat nua do qua 7 ngay",
                "error": "NOT UPDATE THE_NAME_OF THE_PROJECT AFTER 7 DAYS !",
            },
        )
    if check == "THE NAME PROJECT IS DUPLICATE !":
        logger.warning("TEN DỰ ÁN BI TRUNG")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Tên Project bị trùng",
                "error": "PROJECT NAME HAVE BEEN DUPLICATE !",
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


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa Dự án",
    description="YÊU CẦU CHỈ CHO NGƯỜI CHỦ CỦA DỰ ÁN ĐÓ MỚI ĐƯỢC XÓA, NGƯỜI KHÁC KHÔNG ĐƯỢC (KHI XÓA THÌ SẼ XÓA MỀM TỪ PROJECT ĐẾN PROJECT MEMBER RỒI ĐẾN NHỮNG TASK LIÊN QUAN ĐẾN PROJECT ĐÓ !)",
)
@limit.limit("5/minute")  # type: ignore
def delete_a_project(
    request: Request,
    db: DataBase,
    project_id: int = Path(...),
    current_user: UserModel = Depends(get_current_user),
):
    check = delete_project(db, project_id, current_user)
    if check == "NOT FOUND THE PROJECT !":
        logger.warning("KHÔNG TÌM THẤY DỰ ÁN")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": f"Không tìm thấy project có id là {project_id}",
                "error": "NOT FOUND THIS PROJECT ID !",
            },
        )
    if check == "NOT PREMISSION TO DELETE !":
        logger.warning("BẠN KHÔNG ĐỦ QUYỀN ĐỂ XÓA")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Bạn không đủ quyền dể xóa !",
                "error": "YOU DON'T HAVE PREMISSION TO DELETE !",
            },
        )
    if check == "THE PROJECT HAVE BEEN DELETED !":
        logger.warning("DỰ ÁN NÀY ĐÃ XÓA !")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Dự án này đã bị xóa !",
                "error": "THE PROJECT ARE HAVE BEEN DELETED ",
            },
        )
    if check == "NOT HAVE DELETE THE PROJECT !":
        logger.warning("DỰ ÁN NÀY CHƯA ĐƯỢC XÓA !")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Cần xóa bớt thành viên trước !",
                "error": "NEED TO DELETE MEMBER FIRST !"
            }
        )
    if check == "DELETE SUCCESSFULL !":
        logger.info("XÓA THÀNH CÔNG")
        return
