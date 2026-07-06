import subprocess

def run(args):
    print("========== SIGMA BRANCH ==========")
    subprocess.run(["git", "branch", "--show-current"])
