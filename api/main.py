from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import auth

app = FastAPI(title="BriefIt API")

# Add CORS middleware to allow frontend communication later
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the authentication routes
app.include_router(auth.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to BriefIt API"}
