from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_combat():
    return {"message": "Get combat endpoint"} 