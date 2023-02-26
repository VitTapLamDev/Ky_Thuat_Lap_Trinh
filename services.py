import database as _database
import models as _models
import sqlalchemy.orm as _orm
import schemas as _schemas
import fastapi.security as _security
import email_validator as _email_validator
import fastapi as _fastapi
import passlib.hash as _hash
import jwt as _jwt

_JWT_SECRET = "ad2t4h13adsfg9aw"
oauth2schema = _security.OAuth2PasswordBearer("/api/v1/login")

#Tao db
def create_database():
    return _database.Base.metadata.create_all(bind=_database.engine)

#lay db
def get_database():
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

#Ham tim kiem theo email
async def getUserByEmail(email: str, db: _orm.Session):
    return db.query(_models.UserModel).filter(_models.UserModel.email == email).first()

#Ham tao user moi
async def create_user(user: _schemas.UserRequest, db: _orm.Session):
    # KiemTra Email
    try:
        isValid = _email_validator.validate_email(email=user.email)
        email = isValid.email
    except _email_validator.EmailNotValidError:
        raise _fastapi.HTTPException(status_code=400, detail="Email khong hop le")
    #Ham bam mat khau luu tru
    hashed_password = _hash.bcrypt.hash(user.password)
    user_obj = _models.UserModel(
        email=email,
        name=user.name,
        address=user.address,
        phone_number=user.phone_number,
        password_hash=hashed_password
    )
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj

#Ham tao token
async def create_token(user: _models.UserModel):
    #Convert user model to user schemas
    user_schemas = _schemas.UserResponse.from_orm(user)
    user_dict = user_schemas.dict()
    del user_dict["created_at"]
    token = _jwt.encode(user_dict, _JWT_SECRET)
    return dict(access_token=token, token_type="bearer")

# Ham Kiem Tra Dang Nhap
async def login(email: str, password: str, db: _orm.Session):
    db_user = await getUserByEmail(email=email, db=db)
    if not db_user:
        return False
    if not db_user.password_verification(password=password):
        return False
    return db_user

#Ham lay thong tin nguoi dung trong db
async def current_user(db: _orm.Session = _fastapi.Depends(get_database),
                       token: str= _fastapi.Depends(oauth2schema)):
    try:
        payload = _jwt.decode(token, _JWT_SECRET, algorithms=["HS256"])
        #Kiem tra nguoi dung bang id va neu id ton tai long db
        db_user = db.query(_models.UserModel).get(payload["id"])
    except:
        raise _fastapi.HTTPException(status_code=401, detail="Thong tin xac thuc khong chinh xac")

    return _schemas.UserResponse.from_orm(db_user)

#Ham tao post
async def create_post(user: _schemas.UserResponse, db: _orm.Session, post: _schemas.PostRequest):
    post = _models.PostModel(**post.dict(), user_id=user.id)
    db.add(post)
    db.commit()
    db.refresh(post)
    #Chuyen PostModel  sang PostDTO/Schema va tra lai API
    return _schemas.PostResponse.from_orm(post)

#Ham lay post theo user
async def get_post_by_user(user: _schemas.UserResponse, db: _orm.Session):
    posts = db.query(_models.PostModel).filter_by(user_id= user.id)
    return list(map(_schemas.PostResponse.from_orm, posts))

#Ham lay tat ca user
async def get_post_by_all( db: _orm.Session):
    posts = db.query(_models.PostModel)
    return list(map(_schemas.PostResponse.from_orm, posts))

#ham lay chi tiet cua Post
async def get_post_detail(post_id: int, db: _orm.Session):
    db_post = db.query(_models.PostModel).filter(_models.PostModel.id==post_id).first()
    if db_post is None:
        raise _fastapi.HTTPException(status_code=404, detail="Post Khong Ton tai")
    # return _schemas.PostResponse.from_orm(db_post)
    return db_post

#Ham lay chi tiet cua data
async def get_user_detail(user_id: int, db: _orm.Session):
    db_user = db.query(_models.UserModel).filter(_models.UserModel.id==user_id).first()
    if db_user is None:
        raise _fastapi.HTTPException(status_code=404, detail="User khong ton tai")
    return _schemas.UserResponse.from_orm(db_user)

#Ham Xoa post
async def delete_post(post: _models.PostModel, db: _orm.Session):
    db.delete(post)
    db.commit()

#Ham Cap Nhat post
async def update_post(
        post_request: _schemas.PostRequest,
        post: _models.PostModel,
        db: _orm.Session
):
    post.post_title = post_request.post_title
    post.post_description = post_request.post_description
    post.image = post_request.image
    db.commit()
    db.refresh(post)
    return _schemas.PostResponse.from_orm(post)