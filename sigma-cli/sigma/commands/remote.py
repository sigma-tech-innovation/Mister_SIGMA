import subprocess

def run(args):
    print("========== SIGMA REMOTE ==========")
    subprocess.run(["git", "remote", "-v"])
