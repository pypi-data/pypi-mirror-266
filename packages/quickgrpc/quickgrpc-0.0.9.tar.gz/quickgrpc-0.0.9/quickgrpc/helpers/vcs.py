from os.path import exists
from pydantic_settings import BaseSettings
import pygit2
import shutil

from pygit2.callbacks import RemoteCallbacks


class VCSConfig(BaseSettings):
    git_username: str
    git_email: str
    git_token: str


settings = VCSConfig()
credentials = pygit2.UserPass(settings.git_username, settings.git_token)


def clone(repo_url: str, local_path: str) -> None:
    shutil.rmtree(local_path, ignore_errors=True)  # just in case...
    repo = pygit2.clone_repository(
        repo_url,
        local_path,
        callbacks=pygit2.RemoteCallbacks(credentials=credentials),
    )


def commit(path: str, msg: str) -> None:
    repo = pygit2.Repository(path)
    index = repo.index
    index.add_all()
    index.write()
    tree = index.write_tree()
    # Get the author and committer information
    author = pygit2.Signature(settings.git_username, settings.git_email)
    committer = author
    # Commit changes
    try:
        parents = [repo.head.peel().oid]
    except pygit2.GitError:
        parents = []
    repo.create_commit("HEAD", author, committer, msg, tree, parents)


def push(path: str) -> None:
    repo = pygit2.Repository(path)
    current_branch = repo.head.shorthand
    remote = repo.remotes[0]
    remote.push(
        [f"refs/heads/{current_branch}"],
        callbacks=RemoteCallbacks(credentials=credentials),
    )
