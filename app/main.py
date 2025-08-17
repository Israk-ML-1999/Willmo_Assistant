from fastapi import FastAPI
from app.api.router import router
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION
)

# Include API routes
app.include_router(router)

@app.get("/")
async def root():
    """Welcome endpoint"""
    return {"message": f"{settings.APP_NAME} is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)