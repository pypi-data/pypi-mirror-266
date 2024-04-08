import os
from typing import List

from fastapi import UploadFile, File, Form, APIRouter

from auto_artifacts.server.config import PATH_ARTIFACTS
from auto_artifacts.server.log import get_logger
import auto_artifacts.server.api_keys as api_keys

from api_list import list_files_recursively

router = APIRouter()

logger = get_logger(__name__)

@router.post("/files")
async def upload(files: List[UploadFile] = File(...), path: str = Form(...), api_key: str = Form(...)):

    if not api_keys.validate(path):
        return "invalid path"

    if not api_keys.auth(api_key, path):
        return "unauthorized path"

    if "push" not in api_keys.keys[api_key]["access"]:
        return "unauthorized access"

    full_path = os.path.join(PATH_ARTIFACTS, path)
    if not os.path.exists(full_path):
        os.makedirs(full_path)

    for file in files:
        file_location = os.path.join(full_path, file.filename)
        with open(file_location, "wb+") as file_object:
            file_object.write(await file.read())
        logger.info(f"Uploaded: {file_location}")

    return "success"
