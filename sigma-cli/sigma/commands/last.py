import subprocess

def run(args):
    print("========== SIGMA LAST COMMITS ==========")
    subprocess.run(["git", "log", "--oneline", "-10"])
