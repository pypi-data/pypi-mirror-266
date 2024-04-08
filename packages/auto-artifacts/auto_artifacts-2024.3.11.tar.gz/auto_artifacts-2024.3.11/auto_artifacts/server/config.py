import os

# PATH_ARTIFACTS = "../../tests/resources/server/artifacts" # For unit testing
PATH_ARTIFACTS = os.getenv('PATH_ARTIFACTS')

# PATH_API_KEYS = "../../tests/resources/server/api_keys.env" # For unit testing
PATH_API_KEYS = f"{os.getenv('PATH_ENV')}/api_keys.env"

# PATH_ORGS = "../../tests/resources/server/orgs.env" # For unit testing
PATH_ORGS = f"{os.getenv('PATH_ENV')}/orgs.env"

# PATH_PROJECTS = "../../tests/resources/server/projects.env" # For unit testing
PATH_PROJECTS = f"{os.getenv('PATH_ENV')}/projects.env"
