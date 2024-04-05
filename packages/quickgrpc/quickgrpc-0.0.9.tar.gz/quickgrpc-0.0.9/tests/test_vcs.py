from unittest import TestCase
from fastgrpc.helpers.vcs import clone, commit, push
import shutil
import uuid
import os


class TestVCS(TestCase):
    repo_url = "https://github.com/ashupednekar/testrpcassets"
    path = "test_one"

    def tearDown(self) -> None:
        ...
        # shutil.rmtree(self.path)

    def test_clone(self):
        clone(self.repo_url, self.path)
        self.assertTrue(os.path.exists("test_one"))

    def test_commit(self):
        clone(self.repo_url, self.path)
        with open(f"{self.path}/test.txt", "w") as f:
            f.write(uuid.uuid4().hex)
        commit(self.path, "test commit")
        with open(f"{self.path}/test.txt", "w") as f:
            f.write(uuid.uuid4().hex)
        commit(self.path, "test commit one")

    def test_push(self):
        clone(self.repo_url, self.path)
        with open(f"{self.path}/test.txt", "w") as f:
            f.write(uuid.uuid4().hex)
        commit(self.path, "test commit")
        with open(f"{self.path}/test.txt", "w") as f:
            f.write(uuid.uuid4().hex)
        commit(self.path, "test commit one")
        push(self.path)
