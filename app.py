import fastapi as _fastapi
import fastapi.security as _security
import sqlalchemy.orm as _orm
import schemas as _schemas
import services as _services
from typing import List

app = _fastapi.FastAPI()

@app.post("/api/v1/users")
async def register_user(
        user: _schemas.UserRequest, db: _orm.Session = _fastapi.Depends(_services.get_database)
):
    # Kiem Tra Email Da Ton Tai
    db_user = await _services.getUserByEmail(email=user.email, db=db)
    # Neu Tim Thay User -> Throw Exception
    if db_user:
        raise _fastapi.HTTPException(status_code=400, detail="Email da ton tai, vui long thu lai")
    # Tao user va lay token
    db_user = await  _services.create_user(user=user, db=db)

    return await _services.create_token(user=db_user)

@app.post("/api/v1/login")
async def login_user(
        form_data: _security.OAuth2PasswordRequestForm = _fastapi.Depends(),
        db: _orm.Session = _fastapi.Depends(_services.get_database)
):
    db_user = await _services.login(email=form_data.username, password=form_data.password, db=db)

    if not db_user:
        raise _fastapi.HTTPException(status_code=401, detail="Tai Khoan hoac Mat Khau Khong Dung")
    return await _services.create_token(db_user)

@app.get("/api/v1/users/current-user", response_model = _schemas.UserResponse)
async def current_user(user: _schemas.UserResponse = _fastapi.Depends(_services.current_user)):
    return user

@app.post("/api/v1/posts", response_model = _schemas.PostResponse)
async def create_post(
        post_request: _schemas.PostRequest,
        user: _schemas.UserRequest = _fastapi.Depends(_services.current_user),
        db: _orm.Session =_fastapi.Depends(_services.get_database)
):
    return await _services.create_post(user=user, db=db, post=post_request)

@app.get("/api/v1/posts/user", response_model=List[_schemas.PostResponse])
async def get_posts_by_user(
        user: _schemas.UserRequest = _fastapi.Depends(_services.current_user),
        db: _orm.Session =_fastapi.Depends(_services.get_database)
):
    return await _services.get_post_by_user(user=user, db=db)

@app.get("/api/v1/posts/all-user", response_model=List[_schemas.PostResponse])
async def get_posts_by_all_user(
        db: _orm.Session =_fastapi.Depends(_services.get_database)
):
    return await _services.get_post_by_all(db=db)

@app.get("/api/v1/posts/{post_id}", response_model=_schemas.PostResponse)
async def get_post_detail(
        post_id: int, db: _orm.Session = _fastapi.Depends(_services.get_database)
):
    post = await _services.get_post_detail(post_id=post_id, db=db)
    return post

@app.get("/api/v1/users/{user_id}/", response_model=_schemas.UserResponse)
async def get_user_detail(
    user_id:int, db:_orm.Session = _fastapi.Depends(_services.get_database)
):
    return await _services.get_user_detail(user_id=user_id, db=db)

@app.delete("/api/v1/post-delete/{post_id}/")
async def delete_post(
        post_id: int,
        db: _orm.Session = _fastapi.Depends(_services.get_database),
):
    post = await _services.get_post_detail(post_id=post_id, db=db)
    await  _services.delete_post(post=post, db=db)
    return "Xoa Post Thanh Cong!!"

@app.delete("/api/v1/delete-user/{user_id}")
async def delete_user(
        user_id: int,
        db: _orm.Session = _fastapi.Depends(_services.get_database)
):
    user = await  _services.get_user_detail(user_id=user_id, db=db)
    await _services.delete_user(user=user, db=db)
    return "Xoa user Thanh Cong"

@app.put("/api/v1/update-posts/{post_id}/", response_model=_schemas.PostResponse)
async def update_post(
        post_id: int,
        post_request: _schemas.PostRequest,
        db: _orm.Session = _fastapi.Depends(_services.get_database)
):
    db_post = await _services.get_post_detail(post_id=post_id, db=db)
    return await _services.update_post(post_request=post_request, post=db_post, db=db)