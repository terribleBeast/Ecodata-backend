from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login_user():
    user = {"id": 1, "name": "Alex", "surname": "Doe", "patronymic": "Don"}
    return JSONResponse({"data": user, "token": "1234"})
