from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi.requests import Request

from ..core import limit, logger
from ..db import DataBase
from ..dependencies import get_current_user
from ..models import ProjectMemberRole, UserModel
from ..responses import StandardResponse
from ..schemas import (
    ProjectMemberInput,
    ProjectMemberOutput,
    ProjectMemberOutputButForGetMember,
)
from ..services import create_member, delete_member, get_members, patch_member

router = APIRouter(prefix="/project", tags=["Projects_member"])


@router.post(
    "/{id}/members",
    response_model=StandardResponse[ProjectMemberOutput],
    status_code=status.HTTP_201_CREATED,
    summary="Thêm thành viên vào dự án",
    description="YÊU CẦU OWNER CỦA DỰ ÁN MỚI ĐƯỢC THÊM, KHÔNG AI CÓ THỂ THÊM ĐƯỢC",
)
@limit.limit("5/minute")  # type: ignore
def add_new_member_in_project(
    request: Request,
    db: DataBase,
    data_in: ProjectMemberInput,
    id: int = Path(...),
    role: Literal[ProjectMemberRole.VIEWER, ProjectMemberRole.MEMBER] = Query(
        default=None
    ),
    current_user: UserModel = Depends(get_current_user),
):
    check = create_member(db, id, current_user, data_in, role)
    if check == "NOT FOUND A USER !":
        logger.warning("USER KHÔNG TỒN TẠI !")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": f"Không tìm thấy user có id là {data_in.user_id} !",
                "error": f"NOT FOUND USER HAVE ID LIKE {data_in.user_id}",
            },
        )
    if check == "USER NOT ACTIVATE !":
        logger.warning("USER ĐÃ KHÔNG CÒN HOẠT ĐỘNG!")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"User có id là {data_in.user_id} đã ngừng hoạt động!",
                "error": f"USER HAVE ID {data_in.user_id} have been not activate",
            },
        )
    if check == "NOT FOUND THE PROJECT !":
        logger.warning("KHÔNG TÌM THẤY DỰ ÁN")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": f"Không tìm thấy project có id là {id} !",
                "error": f"NOT FOUND PROJECT HAVE ID LIKE {id}",
            },
        )
    # if check == "NOT PREMISSION TO DO THE PROJECT":
    #     logger.warning("BẠN KHÔNG ĐỦ QUYỀN ĐỂ LÀM VỚI DỰ ÁN NÀY !")
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail={
    #             "message": "Người dùng không có quyền để thêm thành viên vào dự án này !",
    #             "error": "NOT HAVE PREMISSION TO ADJUST THE PROJECT !",
    #         },
    #     )
    if check == "THE PROJECT HAVE BEEN DELETE !":
        logger.warning("DỰ ÁN ĐÃ BỊ XÓA !")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Người dùng không thể xem chi tiết dự án này !",
                "error": "THE PROJECT HAVE BEEN DELETE !",
            },
        )
    if check == "THE USER HAVE IN THE PROJECT !":
        logger.warning("NGƯỜI DÙNG ĐÃ CÓ TRONG DỰ ÁN")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Người dùng đã có trong dự án !",
                "error": "THE USER HAVE IN THE PROJECT!",
            },
        )
    if check == "FULL OF MEMBER IN THE PROJECT":
        logger.warning("DU AN NAY DA DU NGUOI")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Du an nay da full nguoi trong  du an",
                "error": "THIS PROJECT FULL ;-;",
            },
        )
    logger.info("THÊM THÀNH VIÊN THÀNH CÔNG !")
    return StandardResponse(
        StatusCode=status.HTTP_201_CREATED,
        Message="Thêm thành viên mới vào dự án thành công !",
        Error=None,
        Data=check,
        Path=request.url.path,
    )


@router.get(
    "/{id}/members",
    response_model=StandardResponse[
        dict[str, str | list[ProjectMemberOutputButForGetMember]]
    ],
    status_code=status.HTTP_200_OK,
    summary="Xem danh sách thành viên của dự án đó",
    description="AI TRONG DỰ ÁN ĐỀU CÓ THỂ XEM ĐƯỢC THÀNH VIÊN TRONG DỰ ÁN ĐÓ",
)
@limit.limit("5/minute")  # type: ignore
def get_list_of_member(
    request: Request,
    db: DataBase,
    id: int = Path(...),
    current_user: UserModel = Depends(get_current_user),
):
    check = get_members(db, id, current_user)
    if check == "NOT FOUND THE PROJECT !":
        logger.warning("KHÔNG TÌM THẤY DỰ ÁN")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": f"Không tìm thấy project có id là {id} !",
                "error": f"NOT FOUND PROJECT HAVE ID LIKE {id}",
            },
        )
    if check == "NOT PREMISSION TO SEE MEMBER IN THE PROJECT":
        logger.warning("BẠN KHÔNG ĐỦ QUYỀN ĐỂ XEM THÀNH VIÊN THUỘC DỰ ÁN!")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Người dùng không có quyền xem thành viên trong dự án !",
                "error": "NOT HAVE PREMISSION TO SEE MEMBER IN PROJECT !",
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
    format_data: dict[str, str | Any] = {"total_member": f"{len(check)}", "data": check}
    logger.info("LẤY DANH SÁCH DỰ ÁN THÀNH CÔNG !")
    return StandardResponse(
        StatusCode=status.HTTP_200_OK,
        Message="Danh sách thành viên trong dự án !",
        Error=None,
        Data=format_data,
        Path=request.url.path,
    )


@router.patch(
    "/{id}/members/{user_id}/role",
    response_model=StandardResponse[ProjectMemberOutput],
    status_code=status.HTTP_200_OK,
    summary="Cập nhật vai trò của thành viên trong dự án",
    description="CHỨC NĂNG CHỈ DÀNH CHO OWNER CỦA DỰ ÁN, CÓ THỂ CHUYỂN VAI TRÒ CỦA THÀNH VIÊN TỪ MEMBER THÀNH VIEWER VÀ NGƯỢC LẠI"
)
@limit.limit("5/minute")  # type: ignore
def update_member_in_project(
    request: Request,
    db: DataBase,
    role_up: Literal[ProjectMemberRole.MEMBER, ProjectMemberRole.VIEWER] = Query(
        default=ProjectMemberRole.VIEWER
    ),
    current_user: UserModel = Depends(get_current_user),
    id: int = Path(...),
    user_id: int = Path(...),
):
    check = patch_member(db, id, user_id, role_up, current_user)
    if check == "NOT FOUND THE PROJECT !":
        logger.warning("KHÔNG TÌM THẤY DỰ ÁN")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": f"Không tìm thấy project có id là {id} !",
                "error": f"NOT FOUND PROJECT HAVE ID LIKE {id}",
            },
        )
    if check == "USER NOT IN PROJECT !":
        logger.warning("BẠN KHÔNG CÓ TRONG DỰ ÁN NÀY")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Bạn không có trong dự án  !",
                "error": "YOU DON'T HAVE IN THE PROJECT !",
            },
        )
    if check == "NOT PREMISSION TO SEE MEMBER IN THE PROJECT":
        logger.warning("BẠN KHÔNG CÓ QUYỀN ĐỂ CẬP NHẬT THÀNH VIÊN TRONG DỰ ÁN")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Người dùng không có quyền để CẬP NHẬT thành viên vào dự án này !",
                "error": "NOT HAVE PREMISSION TO ADJUST THE PROJECT !",
            },
        )
    if check == "OWNER NOT UPDATE YOURSELF !":
        logger.warning("BẠN KHÔNG CẬP NHẬT VAI TRÒ CỦA CHÍNH BẢN THÂN !")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Người dùng không được CẬP NHẬT chính bạn!",
                "error": "NOT UPDATE YOURSELF !",
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
    if check == "USER IS NOT EXISTS !":
        logger.warning("THÀNH VIÊN NÀY KHÔNG TỒN TẠI !")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Người được cập nhật không tồn tại !",
                "error": "THE MEMBER IS NOT EXISTS !",
            },
        )
    if check == "THIS MEMBER NOT IN THE PROJECT":
        logger.warning("THÀNH VIÊN NÀY KHÔNG TỒN TẠI TRONG DỰ ÁN !")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Người được cập nhật không có trong dự án !",
                "error": "THE MEMBER IS NOT IN THIS PROJECT !",
            },
        )
    return StandardResponse(
        StatusCode=status.HTTP_200_OK,
        Error=None,
        Message="Cập nhật thành công thành viên",
        Data=check,
        Path=request.url.path,
    )


@router.delete(
    "/{id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa thành viên trong dự án (Xóa mềm)",
    description="CHỈ CÓ OWNER CỦA DỰ ÁN MỚI ĐƯỢC PHÉP XÓA, KHI XÓA CHỈ CẦN ĐỔI TRẠNG THÁI IS_DELETE THÀNH TRUE SAU THÊM LẠI THÌ CHỈ CẦN CHỈNH LẠI IS_DELETE THÀNH FALSE ",
)
@limit.limit("5/minute")  # type: ignore
def delete_project_member(
    request: Request,
    db: DataBase,
    id: int = Path(...),
    user_id: int = Path(...),
    current_user: UserModel = Depends(get_current_user),
):
    check = delete_member(db, id, user_id, current_user)
    if check == "NOT FOUND THE PROJECT !":
        logger.warning("KHÔNG TÌM THẤY DỰ ÁN")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": f"Không tìm thấy project có id là {id} !",
                "error": f"NOT FOUND PROJECT HAVE ID LIKE {id}",
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
    if check == "NOT FOUND USER !":
        logger.warning("USER KHÔNG TỒN TẠI !")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": f"Không tìm thấy user có id là {user_id} !",
                "error": f"NOT FOUND USER HAVE ID LIKE {user_id}",
            },
        )
    # if check == "NOT PREMISSION TO DELETE THE MEMBER IN THE PROJECT":
    #     logger.warning("BẠN KHÔNG ĐỦ QUYỀN ĐỂ XÓA THÀNH VIÊN THUỘC DỰ ÁN!")
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail={
    #             "message": "Người dùng không có quyền xóa thành viên trong dự án !",
    #             "error": "NOT HAVE PREMISSION TO DELETE MEMBER IN PROJECT !",
    #         },
    #     )
    if check == "USER NOT IN THAT PROJECT !":
        logger.warning("NGƯỜI DÙNG KHÔNG CÓ TRONG DỰ ÁN ĐÓ!")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Người dùng không có trong project !",
                "error": "USER NOT IN MEMBER IN THE PROJECT !",
            },
        )
    if check == "THAT USER HAVE BEEN DELETED !":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Người dùng không có trong project !",
                "error": "USER NOT IN MEMBER IN THE PROJECT !",
            },
        )
    if check == "NOT DELETE THE OWNER OF PROJECT":
        logger.warning("KHỐNG ĐƯỢC XÓA CHÍNH BẢN THÂN TRONG DỰ ÁN ĐÓ !")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Người dùng không được xóa chính bản thân !",
                "error": "USER NOT DELETE YOURSELF IN THE PROJECT !",
            },
        )
    if check == "DELETE SUCCESSFULL !":
        logger.info("XÓA THÀNH VIÊN THÀNH CONG !")
        return
