import os.path
import unittest
import requests

import auto_artifacts.client.artifact as artifact
from utils import sha256, clear_directory_contents

env_path_admin = "./resources/client/admin.env"
env_path_viewer = "./resources/client/viewer.env"

class TestFileOperations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_1_upload_files_invalid_access(self):
        clear_directory_contents('./resources/server/artifacts')
        for org_id in range(1, 3):
            for project_id in range(1,3):
                for version in ["2023.03.01", "2023.03.02", "2023.03.03", "2023.03.04"]:
                    for commit in range(1, 3):
                        for branch in ["main", "develop"]:
                            for platform in ["win", "mac", "nux", "ios", "android"]:
                                success = artifact.push(env_path_viewer, f"org_{org_id}", f"project_{project_id}", version, branch, sha256(commit), platform , "./resources/client/sample_file.txt")
                                self.assertTrue(success)
        pass

    def test_2_upload_files(self):
        clear_directory_contents('./resources/server/artifacts')
        for org_id in range(1, 3):
            for project_id in range(1, 3):
                for version in ["2023.03.01", "2023.03.02", "2023.03.03", "2023.03.04"]:
                    for commit in range(1, 3):
                        for branch in ["main", "develop"]:
                            for platform in ["win", "mac", "nux", "ios", "android"]:
                                success = artifact.push(env_path_admin, f"org_{org_id}", f"project_{project_id}", version, branch, sha256(commit), platform, "./resources/client/sample_file.txt")
                                self.assertTrue(success)
        pass

    def test_3_download_invalid_access(self):
        clear_directory_contents('./resources/client/downloaded')
        for org_id in range(2, 3):
            for project_id in range(1, 3):
                for version in ["2023.03.01"]:
                    for commit in range(1, 3):
                        for branch in ["develop"]:
                            for platform in ["win"]:
                                local_path = f"./resources/client/downloaded/org_{org_id}/project_{project_id}/{version}/{sha256(commit)}/{branch}/{platform}"
                                if not os.path.exists(local_path):
                                    os.makedirs(local_path)
                                success = artifact.pull(env_path_viewer, f"org_{org_id}", f"project_{project_id}", version, branch, sha256(commit), platform, local_path, f"sample_file.txt")
                                self.assertTrue(success)
        pass

    def test_3_list(self):
        url = 'http://127.0.0.1:8000/artifacts/list/files?api_key=fbdf2bdc4b2a45f3508c8ced68098f58375edbf2fe81ec8fe4b113185670939a'
        response = requests.get(url)
        self.assertTrue(response.status_code == 200)
        pass

if __name__ == "__main__":
    unittest.main()
