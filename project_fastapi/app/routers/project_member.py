from fastapi import APIRouter, status, HTTPException, Path, Depends
from app.db import DataBase
from fastapi.requests import Request
from app.schemas import (
    ProjectMemberInput,
    ProjectMemberOutput,
    ProjectMemberOutputButForGetMember,
)
from app.services import create_member, get_members, delete_member
from app.models import UserModel
from app.dependencies import get_current_user
from app.responses import StandardResponse
from app.core import limit, logger

router = APIRouter(prefix="/project_member", tags=["projects"])


@router.post(
    "/{id}/members",
    response_model=StandardResponse[ProjectMemberOutput],
    status_code=status.HTTP_201_CREATED,
)
@limit.limit("5/minute")  # type: ignore
def add_new_member_in_project(
    request: Request,
    db: DataBase,
    data_in: ProjectMemberInput,
    id: int = Path(...),
    current_user: UserModel = Depends(get_current_user),
):
    check = create_member(db, id, current_user, data_in)
    if check == "NOT FOUND A USER !":
        logger.error("USER KHÔNG TỒN TẠI !")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": f"Không tìm thấy user có id là {data_in.user_id} !",
                "error": f"NOT FOUND USER HAVE ID LIKE {data_in.user_id}",
            },
        )
    if check == "NOT FOUND THE PROJECT !":
        logger.error("KHÔNG TÌM THẤY DỰ ÁN")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": f"Không tìm thấy project có id là {id} !",
                "error": f"NOT FOUND PROJECT HAVE ID LIKE {id}",
            },
        )
    if check == "NOT PREMISSION TO DO THE PROJECT":
        logger.error("BẠN KHÔNG ĐỦ QUYỀN ĐỂ LÀM VỚI DỰ ÁN NÀY !")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Người dùng không có quyền để chỉnh sửa chi tiết dự án này !",
                "error": "NOT HAVE PREMISSION TO ADJUST THE PROJECT !",
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
    if check == "THE USER HAVE IN THE PROJECT !":
        logger.error("NGƯỜI DÙNG ĐÃ CÓ TRONG DỰ ÁN")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Người dùng đã có trong dự án !",
                "error": "THE USER HAVE IN THE PROJECT!",
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
    response_model=StandardResponse[list[ProjectMemberOutputButForGetMember]],
    status_code=status.HTTP_200_OK,
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
        logger.error("KHÔNG TÌM THẤY DỰ ÁN")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": f"Không tìm thấy project có id là {id} !",
                "error": f"NOT FOUND PROJECT HAVE ID LIKE {id}",
            },
        )
    if check == "NOT PREMISSION TO SEE MEMBER IN THE PROJECT":
        logger.error("BẠN KHÔNG ĐỦ QUYỀN ĐỂ XEM THÀNH VIÊN THUỘC DỰ ÁN!")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Người dùng không có quyền xem thành viên trong dự án !",
                "error": "NOT HAVE PREMISSION TO SEE MEMBER IN PROJECT !",
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
    logger.info("LẤY DANH SÁCH DỰ ÁN THÀNH CÔNG !")
    return StandardResponse(
        StatusCode=status.HTTP_200_OK,
        Message="Danh sách thành viên trong dự án !",
        Error=None,
        Data=check,
        Path=request.url.path,
    )


@router.delete(
    "/{id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT
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
        logger.error("KHÔNG TÌM THẤY DỰ ÁN")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": f"Không tìm thấy project có id là {id} !",
                "error": f"NOT FOUND PROJECT HAVE ID LIKE {id}",
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
    if check == "NOT FOUND USER !":
        logger.error("USER KHÔNG TỒN TẠI !")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": f"Không tìm thấy user có id là {user_id} !",
                "error": f"NOT FOUND USER HAVE ID LIKE {user_id}",
            },
        )
    if check == "NOT PREMISSION TO DELETE THE MEMBER IN THE PROJECT":
        logger.error("BẠN KHÔNG ĐỦ QUYỀN ĐỂ XÓA THÀNH VIÊN THUỘC DỰ ÁN!")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Người dùng không có quyền xóa thành viên trong dự án !",
                "error": "NOT HAVE PREMISSION TO DELETE MEMBER IN PROJECT !",
            },
        )
    if check == "USER NOT IN THAT PROJECT !":
        logger.error("NGƯỜI DÙNG KHÔNG CÓ TRONG DỰ ÁN ĐÓ!")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Người dùng không có trong project !",
                "error": "USER NOT IN MEMBER IN THE PROJECT !",
            },
        )
    if check == "NOT DELETE THE OWNER OF PROJECT":
        logger.error("KHỐNG ĐƯỢC XÓA CHÍNH BẢN THÂN TRONG DỰ ÁN ĐÓ !")
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
