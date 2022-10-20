from fastapi import APIRouter, status, HTTPException, Depends
from ..models.post_model import PostModel
from ..schemas.post_schemas import PostCreateSchema
from ..service.redis_client import get_redis
from ..utils.utils import get_db
from ..utils.user_utils import get_current_user
from sqlalchemy.orm import Session
import json
import redis
from typing import Annotated
from ..response_schemas.post_response import AddPostResponse, PostResponse
from typing import List
posts_router = APIRouter()

@posts_router.post('/add-post', status_code=status.HTTP_200_OK, response_model=AddPostResponse)
async def add_post(post_data: PostCreateSchema, db: Session = Depends(get_db),
                   user: Annotated[dict, Depends(get_current_user)] = None):
    """
    Handles the creation of a new post.
    
    - Checks if the user is authorized by validating the 'user' dependency.
    - Verifies if the length of the post text exceeds the defined maximum size (MAX_SIZE).
    - Creates a new post entry in the database with the provided post data.
    - Returns a response with the post ID and a success message if the post is created successfully.
    
    Args:
        post_data (PostCreateSchema): The data for creating a new post, including the post text.
        db (db_dependency): The database session dependency used to interact with the database.
        user (user_dependency): The user details extracted from the user authentication.

    Returns:
        dict: A dictionary containing the post ID and a success message.
    """

    # Create a new PostModel instance with the provided text and user_id
    post = PostModel(
        text=post_data.text,
        user_id=user.get("id")
    )
    db.add(post)  # Add the post to the session
    db.commit()   # Commit the transaction to save the post
    db.refresh(post)  # Refresh the post object to get the generated ID
    
    return AddPostResponse(post_id=post.id, detail="Post created")


@posts_router.get('/get-posts', status_code=status.HTTP_200_OK, response_model=List[PostResponse])
async def get_posts(db: Session = Depends(get_db), user: Annotated[dict, Depends(get_current_user)] = None, 
                    redis_client: redis.Redis = Depends(get_redis)):
    """
    Retrieves all posts for the authenticated user, with caching support using Redis.
    
    - Checks if the user is authorized by validating the 'user' dependency.
    - First attempts to fetch the posts from the Redis cache based on the user's ID.
    - If the data is found in Redis, it returns the cached data. If not, it queries the database.
    - Saves the queried posts into Redis for future requests, with a 60-second expiration time.
    
    Args:
        db (db_dependency): The database session dependency used to interact with the database.
        user (user_dependency): The user details extracted from the user authentication.
        redis_client (redis.Redis): The Redis client used to interact with the Redis cache.

    Returns:
        list: A list of posts associated with the authenticated user.
    """
    
    user_id = user.get("id")
    cache_key = f"post_user{user_id}"
    cached_data = await redis_client.get(cache_key)
    
    if cached_data:
        # If the data is found in cache, return the cached posts
        posts = json.loads(cached_data)
    else:
        # If no cached data, fetch posts from the database and store them in cache
        posts = db.query(PostModel).all()
        posts_data = [{"id": c.id, "name": c.text} for c in posts]
        
        # Save posts to Redis with a 5-second expiration time
        await redis_client.set(cache_key, json.dumps(posts_data), ex=5)
        
    # Fetch the posts from the database for the specific user
    posts = db.query(PostModel).filter(PostModel.user_id == user.get("id")).all()
    return [PostResponse(id=post.id, text=post.text, user_id=post.user_id) for post in posts]


@posts_router.delete("/delete-post/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, db: Annotated[Session, Depends(get_db)], 
                      user: Annotated[dict, Depends(get_current_user)] = None):
    """
    Deletes a post identified by the provided post ID.
    
    - Checks if the user is authorized by validating the 'user' dependency.
    - Retrieves the post by ID and ensures that it belongs to the authenticated user.
    - If the post exists, it deletes it from the database and commits the change.
    - If the post is not found, it raises a 404 HTTPException.
    
    Args:
        post_id (int): The ID of the post to be deleted.
        db (db_dependency): The database session dependency used to interact with the database.
        user (user_dependency): The user details extracted from the user authentication.

    Returns:
        None: Upon successful deletion, the status code 204 (No Content) is returned.
    """
    # Fetch the post to delete, ensuring the post belongs to the authenticated user
    post = db.query(PostModel).filter(PostModel.id == post_id, PostModel.user_id == user.get("id")).first()
    
    if not post:
        # If post not found, raise a 404 error
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    db.delete(post)  # Mark the post for deletion
    db.commit()  # Commit the transaction to apply the changes
