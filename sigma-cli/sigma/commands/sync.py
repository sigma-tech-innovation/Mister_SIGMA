import subprocess

def run(args):

    if args and args[0] == "pull":
        print("Running: git pull origin develop")
        subprocess.run(["git", "pull", "origin", "develop"])
        return

    print("===================================")
    print("         Σ SIGMA SYNC")
    print("===================================")

    commands = [
        ["git", "branch", "--show-current"],
        ["git", "status", "--short"],
        ["git", "remote", "-v"]
    ]

    titles = [
        "Current branch",
        "Working tree",
        "Git remotes"
    ]

    for title, cmd in zip(titles, commands):
        print(f"\n[{title}]")
        try:
            out = subprocess.check_output(cmd, text=True)
            print(out.strip() if out.strip() else "OK")
        except Exception as e:
            print(f"ERROR: {e}")
