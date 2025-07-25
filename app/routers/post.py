from typing import List, Optional
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter   
from sqlalchemy.orm import Session, joinedload
from .. import models, schemas, oauth2
from ..database import get_db
from sqlalchemy import func

router = APIRouter(
    prefix="/posts",
    tags=["posts"]
)

@router.get("/", response_model=List[schemas.PostOut])
def get_post(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()
    
    # posts = db.query(models.Post).options(joinedload(models.Post.owner)).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    
    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    return posts


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""", (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()
    new_post = models.Post(owner_id=current_user.id, **post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post) 
    
    # Fetch the created post with owner details
    created_post = db.query(models.Post).options(joinedload(models.Post.owner)).filter(models.Post.id == new_post.id).first()
    return created_post


@router.get("/{id}", response_model=schemas.PostOut)
def get_post(id: int, db: Session = Depends(get_db), response_model=schemas.Post, current_user: models.User = Depends(oauth2.get_current_user)):
    # cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id),))
    # post = cursor.fetchone()
    # post = db.query(models.Post).options(joinedload(models.Post.owner)).filter(models.Post.id == id).first()

    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("""DELETE FROM posts WHERE id=%s RETURNING *""", (str(id),))
    # delete_post = cursor.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    post_query.delete(synchronize_session=False)
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}")
def update_post(id: int, post_update: schemas.PostCreate, db: Session = Depends(get_db), response_model=schemas.Post, current_user: schemas.TokenData = Depends(oauth2.get_current_user)):
    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s RETURNING *""", (post.title, post.content, post.published))
    # updated_post = cursor.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")

    post_query.update(post_update.model_dump(), synchronize_session=False)
    db.commit()
    
    # Fetch the updated post with owner details
    updated_post = db.query(models.Post).options(joinedload(models.Post.owner)).filter(models.Post.id == id).first()
    
    return updated_post