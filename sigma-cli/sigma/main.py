import sys
from sigma.dispatcher import dispatch

def main():

    if len(sys.argv) < 2:
        print("Sigma CLI")
        return

    dispatch(sys.argv[1], sys.argv[2:])

if __name__ == "__main__":
    main()
