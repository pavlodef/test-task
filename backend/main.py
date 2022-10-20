from fastapi import FastAPI

from .dependencies import Base, engine
from .endpoints.users_endpoints import users_router
from .endpoints.posts_endpoints import posts_router
from .service.redis_client import get_redis, close_redis
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    redis = await get_redis()
    yield
    await close_redis(redis)


app = FastAPI(title='Test Task', description='Test Task API', 
              version='1.0.0', lifespan=lifespan)

app.include_router(users_router, prefix='/api/v1/users', tags=['Users'])
app.include_router(posts_router, prefix='/api/v1/posts', tags=['Posts'])