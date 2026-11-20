import subprocess
from pathlib import Path


def ensure_git_repo(work_tree: Path, repo_url: str):
    work_tree.parent.mkdir(parents=True, exist_ok=True)
    if not work_tree.is_dir():
        subprocess.run(["git", "-C", work_tree.parent, "clone", repo_url], check=True)

    script = [
        ["git", "-C", work_tree, "fetch", "origin"],
        ["git", "-C", work_tree, "checkout", "-B", "master"],
        ["git", "-C", work_tree, "reset", "--hard", "origin/master"],
        ["git", "-C", work_tree, "clean", "-fd"],
    ]
    for line in script:
        subprocess.run(line, check=True)
