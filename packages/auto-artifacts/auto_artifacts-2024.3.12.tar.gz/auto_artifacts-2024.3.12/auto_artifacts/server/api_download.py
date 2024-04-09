import os
import logging

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from auto_artifacts.server.config import PATH_ARTIFACTS
import auto_artifacts.server.api_keys as api_keys

router = APIRouter()

logger = logging.getLogger('gunicorn.error')

@router.get("/file")
def download(filename: str = Query(..., description="The name of the file to download"),
             path: str = Query(..., description="The path to the file, relative to the base path"),
             api_key: str = Query(None, description="API Key for accessing private files")):

    if not api_key:
        return "unauthorized access"

    if api_key not in api_keys.keys.keys():
        return "unauthorized access"
    elif "push" not in api_keys.keys[api_key]["access"]:
        return "unauthorized access"

    if not api_keys.validate(path):
        raise HTTPException(status_code=404, detail="invalid path")

    if not api_keys.auth(api_key, path):
        raise HTTPException(status_code=404, detail="unauthorized path")

    full_path = os.path.join(PATH_ARTIFACTS, path)
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="Invalid artifact path")

    file_path = os.path.join(full_path, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Invalid artifact")
    logger.info(f"Downloaded: {file_path}")

    return FileResponse(path=file_path, filename=filename, media_type='application/octet-stream')
