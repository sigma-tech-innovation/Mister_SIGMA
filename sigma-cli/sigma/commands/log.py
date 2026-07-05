from sigma.logger import log

def run(args):
    message = " ".join(args) if args else "Test log"
    log(message)
    print("Log written.")
