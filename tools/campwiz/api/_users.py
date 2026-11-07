from fastapi import APIRouter, Request, Query, HTTPException
import json
from ..models import *
TRANSLATION_FOLDER = "translations/campwiz"
TRANSLATION_FOLDER_BASE = os.path.abspath(TRANSLATION_FOLDER)
user_router = APIRouter(
    prefix="/user",
    tags=["User"],
    responses={404: {"details": "Not found"}},
)
@user_router.get("/", response_model=ResponseMultiple[UserScheme])
async def list_users(req : Request):
    try:
        with Server.get_parmanent_db() as conn:
            users = User.get_all(conn.cursor())
        result = [UserScheme(**user) for user in users]
        return ResponseMultiple[UserScheme](success=True, data=result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@user_router.get("/me", response_model=ResponseSingle[UserScheme])
async def get_me(req: Request):
    try:
        user_id = req.state.user["id"]
        with Server.get_parmanent_db() as conn:
            me = User.get_by_id(conn.cursor(), user_id)
        return ResponseSingle[UserScheme](success=True, data=UserScheme(**me))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@user_router.get("/{user_id}", response_model=ResponseSingle[UserScheme])
async def get_user(user_id: int):
    try:
        with Server.get_parmanent_db() as conn:
            user = User.get_by_id(conn.cursor(), user_id)
        return ResponseSingle[UserScheme](success=True, data=UserScheme(**user))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@user_router.post("/{user_id}", response_model=ResponseSingle[UserScheme])
async def update_user(req : Request, user_id: int, user: UserUpdate):
    try:
        target_rights = user.rights
        my_rights = req.state.user["rights"]
        has_grant_access = User.has_access(my_rights, Permission.GRANT.value)
        assert has_grant_access, "You don't have permission to grant this right"
        with Server.get_parmanent_db() as conn:
            updated_user = User.update_rights(conn.cursor(), user_id, target_rights)
        BaseServer.log("update", req.state.user["id"], req.state.user["username"], 
                       f"User {user_id} rights updated to {target_rights}")
        return ResponseSingle[UserScheme](success=True, data=UserScheme(**updated_user))
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))
def get_translation_path(lang: str, user_id: int):
    directory = os.path.join(TRANSLATION_FOLDER, lang)
    # Check if it exists under TRANSLATION_FOLDER/campwiz
    assert not lang.startswith("."), "Invalid language"
    assert not lang.startswith("_"), "Invalid language"
    assert os.path.abspath(directory).startswith(TRANSLATION_FOLDER_BASE), "Invalid language"
    if not os.path.exists(directory):
        os.makedirs(directory)
    path = os.path.join(directory, f"{user_id}.json")
    return path
@user_router.get("/translation/{lang}", response_model=ResponseSingle[dict])
async def get_translation(lang: str, req : Request):
    try:
        path = get_translation_path(lang, req.state.user["id"])
        if not os.path.exists(path):
            path = get_translation_path(lang, "root")
        if not os.path.exists(path):
            path = get_translation_path("en", "root")
        with open(path, "r") as f:
            data = json.load(f)
        return ResponseSingle[dict](success=True, data=data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@user_router.post("/translation/{lang}", response_model=ResponseSingle[dict])
async def update_translation(lang: str, req : Request, data: dict):
    try:
        path = get_translation_path(lang, req.state.user["id"])
        content = json.dumps(data, indent=4, ensure_ascii=False)
        with open(path, "w") as f:
            f.write(content)
        BaseServer.log("update", req.state.user["id"], req.state.user["username"], 
                       f"Translation updated for {lang} : {content}")
        msg = f"""
        New Translation was requested for {lang} by {req.state.user["username"]} ({req.state.user["id"]})
        """
        notify_tool_group(msg)
        return ResponseSingle[dict](success=True, data=data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
