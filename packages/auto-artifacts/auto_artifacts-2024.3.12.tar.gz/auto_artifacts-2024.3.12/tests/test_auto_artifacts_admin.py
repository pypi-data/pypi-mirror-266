import os.path
import unittest

import auto_artifacts.client.artifact as artifact
from utils import sha256, clear_directory_contents

env_path_admin = "./resources/client/admin.env"
env_path_invalid = "./resources/client/invalid.env"

class TestFileOperations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_1_upload_invalid_file(self):
        clear_directory_contents('./resources/server/artifacts')
        for org_id in range(1, 2):
            for project_id in range(1,2):
                for version in ["2023.03.01"]:
                    for commit in range(1, 2):
                        for branch in ["main"]:
                            for platform in ["win"]:
                                success = artifact.push(env_path_admin, f"org_{org_id}", f"project_{project_id}", version, branch, sha256(commit), platform , "./resources/client/invalid_file.txt")
                                self.assertTrue(success)
        pass

    def test_2_upload_invalid_key(self):
        clear_directory_contents('./resources/server/artifacts')
        for org_id in range(1, 3):
            for project_id in range(1,3):
                for version in ["2023.03.01", "2023.03.02", "2023.03.03", "2023.03.04"]:
                    for commit in range(1, 3):
                        for branch in ["main", "develop"]:
                            for platform in ["win", "mac", "nux", "ios", "android"]:
                                success = artifact.push(env_path_invalid, f"org_{org_id}", f"project_{project_id}", version, branch, sha256(commit), platform , "./resources/client/sample_file.txt")
                                self.assertTrue(success)
        pass

    def test_3_upload_files(self):
        clear_directory_contents('./resources/server/artifacts')
        for org_id in range(1, 3):
            for project_id in range(1,3):
                for version in ["2023.03.01", "2023.03.02", "2023.03.03", "2023.03.04"]:
                    for commit in range(1, 3):
                        for branch in ["main", "develop"]:
                            for platform in ["win", "mac", "nux", "ios", "android"]:
                                success = artifact.push(env_path_admin, f"org_{org_id}", f"project_{project_id}", version, branch, sha256(commit), platform , "./resources/client/sample_file.txt")
                                self.assertTrue(success)
        pass

    def test_4_download(self):
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
                                success = artifact.pull(env_path_admin, f"org_{org_id}", f"project_{project_id}", version, branch, sha256(commit), platform, local_path, f"sample_file.txt")
                                self.assertTrue(success)
        pass

    def test_5_download_invalid_path(self):
        clear_directory_contents('./resources/client/downloaded')
        for org_id in range(3, 4):
            for project_id in range(1, 2):
                for version in ["2023.03.01"]:
                    for commit in range(1, 10):
                        for branch in ["develop"]:
                            for platform in ["win"]:
                                success = artifact.pull(env_path_admin, f"invalid_org", f"project_{project_id}", version, branch, sha256(commit), platform, "./resources/client/downloaded", "sample_file.txt")
                                self.assertTrue(success)
        pass

    def test_6_download_invalid_file(self):
        clear_directory_contents('./resources/client/downloaded')
        for org_id in range(2, 3):
            for project_id in range(1, 3):
                for version in ["2023.03.01"]:
                    for commit in range(2, 3):
                        for branch in ["develop"]:
                            for platform in ["win"]:
                                success = artifact.pull(env_path_admin, f"org_{org_id}", f"project_{project_id}", version, branch, sha256(commit), platform, "./resources/client/downloaded", f"invalid_file.txt")
                                self.assertTrue(success)
        pass

if __name__ == "__main__":
    unittest.main()
