import subprocess

def run(args):
    print("========== SIGMA GIT BRANCHES ==========")
    subprocess.run(["git", "--no-pager", "branch", "-a"])
