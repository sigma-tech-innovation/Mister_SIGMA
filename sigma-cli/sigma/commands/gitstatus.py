import subprocess

def run(args):
    print("========== SIGMA GIT STATUS ==========")
    subprocess.run(["git", "status"])
