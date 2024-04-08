import os
from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware


print(os.getcwd())

from auto_artifacts.server.api_download import router as router_download
from auto_artifacts.server.api_upload import router as router_upload
from auto_artifacts.server.api_list import router as router_list
from auto_artifacts.server.api_health import router as router_health

app = FastAPI()

# Define a list of allowed origins (use ["*"] for allowing all origins)
origins = ["*"]

# Add CORSMiddleware to the application
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Specifies the origins that are allowed to make requests
    allow_credentials=True,  # Supports credentials (cookies, Authorization headers, etc.)
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers for each API
app.include_router(router_health, prefix="/artifacts")
app.include_router(router_download, prefix="/artifacts/download")
app.include_router(router_upload, prefix="/artifacts/upload")
app.include_router(router_list, prefix="/artifacts/list")

def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
