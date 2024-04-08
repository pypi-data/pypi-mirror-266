import os
from typing import List
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from fastapi import UploadFile, File, HTTPException, Form, APIRouter

import auto_artifacts.server.api_keys as api_keys
from auto_artifacts.server.config import PATH_ARTIFACTS
from auto_artifacts.server.log import get_logger

router = APIRouter()

logger = get_logger(__name__)

def list_files_recursively(path: str) -> List[str]:
    """Recursively lists all files in the given directory."""
    files_list = []
    for root, dirs, files in os.walk(path):
        for file in files:
            files_list.append(os.path.join(root, file))
    return files_list

@router.get("/files")
async def list_files(api_key: str = Query(None, description="API Key for accessing private files")):

    if not api_key:
        return "unauthorized access"
    elif "list" not in api_keys.keys[api_key]["access"]:
        return "unauthorized access"

    # Get paths
    if not os.path.exists(PATH_ARTIFACTS):
        raise HTTPException(status_code=404, detail="Directory not found")
    paths = list_files_recursively(PATH_ARTIFACTS)

    # Parse paths
    remote_paths = []
    for path in paths:
        remote_path = path.split("artifacts/")[1]
        if api_keys.validate(remote_path):
            if api_keys.auth(api_key, remote_path):
                remote_paths.append(remote_path)

    return remote_paths

@router.get("/next_version")
async def list_files(api_key: str = Query(None, description="API Key for accessing private files"),
                     org: str = Query(None, description="Organization Name"),
                     project: str = Query(None, description="Project Name"),
                     branch: str = Query(None, description="Branch Name")):

    if not api_key:
        return "unauthorized access"
    elif "list" not in api_keys.keys[api_key]["access"]:
        return "unauthorized access"

    # Get paths
    if not os.path.exists(PATH_ARTIFACTS):
        raise HTTPException(status_code=404, detail="Directory not found")

    project_build_path = PATH_ARTIFACTS + "/" + org + "/" + project
    project_builds = list_files_recursively(project_build_path)

    year = datetime.now().year
    month = datetime.now().month
    version_prefix = f"v{str(year).zfill(4)}.{str(month).zfill(2)}"

    relevant_build = []
    for project_build in project_builds:
        if version_prefix in project_build:
            if branch in project_build:
                relevant_build.append(project_build)

    if len(relevant_build) > 0:
        highest_build_number = 1
        for project_build in relevant_build:
            build_number = int(project_build.replace(f"{project_build_path}/{version_prefix}.", "")[0:2])
            if build_number > highest_build_number:
                highest_build_number = build_number
        return f"{version_prefix}.{str(highest_build_number+1).zfill(2)}"
    else:
        return f"{version_prefix}.01"