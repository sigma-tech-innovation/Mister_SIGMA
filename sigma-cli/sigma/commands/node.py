from sigma.node import get_node, register_node

def run(args):

    if args and args[0] == "register":
        register_node()
        return

    info = get_node()

    print("Σ Sigma Node")

    for k, v in info.items():
        print(f"{k}: {v}")
