import os.path
import unittest
import requests

import auto_artifacts.client.artifact as artifact
from utils import sha256, clear_directory_contents

env_path_admin = "./resources/client/admin.env"
env_path_machine = "./resources/client/machine.env"

class TestFileOperations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_1_upload_files_invalid_org(self):
        clear_directory_contents('./resources/server/artifacts')
        for org in ["org_1"]:
            for project in ["project_2"]:
                for version in ["2023.03.01", "2023.03.02", "2023.03.03", "2023.03.04"]:
                    for commit in range(1, 3):
                        for branch in ["main", "develop"]:
                            for platform in ["win", "mac", "nux", "ios", "android"]:
                                success = artifact.push(env_path_machine, f"{org}", f"{project}", version, branch, sha256(commit), platform, "./resources/client/sample_file.txt")
                                self.assertTrue(success)
        pass

    def test_2_upload_files_invalid_project(self):
        clear_directory_contents('./resources/server/artifacts')
        for org in ["org_2"]:
            for project in ["project_1"]:
                for version in ["2023.03.01", "2023.03.02", "2023.03.03", "2023.03.04"]:
                    for commit in range(1, 3):
                        for branch in ["main", "develop"]:
                            for platform in ["win", "mac", "nux", "ios", "android"]:
                                success = artifact.push(env_path_machine, f"{org}", f"{project}", version, branch, sha256(commit), platform , "./resources/client/sample_file.txt")
                                self.assertTrue(success)
        pass

    def test_3_upload_files(self):
        clear_directory_contents('./resources/server/artifacts')
        for org in ["org_2"]:
            for project in ["project_2"]:
                for version in ["2023.03.01", "2023.03.02", "2023.03.03", "2023.03.04"]:
                    for commit in range(1, 3):
                        for branch in ["main", "develop"]:
                            for platform in ["win", "mac", "nux", "ios", "android"]:
                                success = artifact.push(env_path_machine, f"{org}", f"{project}", version, branch, sha256(commit), platform, "./resources/client/sample_file.txt")
                                self.assertTrue(success)
        pass

    def test_4_download(self):
        clear_directory_contents('./resources/client/downloaded')
        for org in ["org_2"]:
            for project in ["project_2"]:
                for version in ["2023.03.01"]:
                    for commit in range(1, 3):
                        for branch in ["develop"]:
                            for platform in ["win"]:
                                local_path = f"./resources/client/downloaded/{org}/{project}/{version}/{sha256(commit)}/{branch}/{platform}"
                                if not os.path.exists(local_path):
                                    os.makedirs(local_path)
                                success = artifact.pull(env_path_machine, f"{org}", f"{project}", version, branch, sha256(commit), platform, local_path, f"sample_file.txt")
                                self.assertTrue(success)
        pass

    def test_5_download_invalid_org(self):
        clear_directory_contents('./resources/client/downloaded')
        for org in ["org_1"]:
            for project in ["project_2"]:
                for version in ["2023.03.01"]:
                    for commit in range(1, 3):
                        for branch in ["develop"]:
                            for platform in ["win"]:
                                local_path = f"./resources/client/downloaded/org_{org}/project_{project}/{version}/{sha256(commit)}/{branch}/{platform}"
                                if not os.path.exists(local_path):
                                    os.makedirs(local_path)
                                success = artifact.pull(env_path_machine, f"org_{org}", f"project_{project}", version, branch, sha256(commit), platform, local_path, f"sample_file.txt")
                                self.assertTrue(success)
        pass

    def test_6_download_invalid_project(self):
        clear_directory_contents('./resources/client/downloaded')
        for org in ["org_2"]:
            for project in ["project_1"]:
                for version in ["2023.03.01"]:
                    for commit in range(1, 3):
                        for branch in ["develop"]:
                            for platform in ["win"]:
                                local_path = f"./resources/client/downloaded/{org}/{project}/{version}/{sha256(commit)}/{branch}/{platform}"
                                if not os.path.exists(local_path):
                                    os.makedirs(local_path)
                                success = artifact.pull(env_path_machine, f"{org}", f"project_{project}", version, branch, sha256(commit), platform, local_path, f"sample_file.txt")
                                self.assertTrue(success)
        pass

    def test_7_list_invalid_access(self):
        url = 'http://127.0.0.1:8000/artifacts/list/files?api_key=d26a091bf29c58cb3e7884cf6bd339c63c37482b2ce60a069b61cd746f61d2ac'
        response = requests.get(url)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.text.replace('"','')  == "unauthorized access")
        pass

if __name__ == "__main__":
    unittest.main()
