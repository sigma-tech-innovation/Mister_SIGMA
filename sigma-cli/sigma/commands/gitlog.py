import subprocess

def run(args):
    n = "20"
    if len(args) > 0:
        n = args[0]

    print("========== SIGMA GIT LOG ==========")
    subprocess.run(["git", "log", "--oneline", f"-{n}"])
