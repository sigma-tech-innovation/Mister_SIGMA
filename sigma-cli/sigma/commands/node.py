from sigma.node import get_node

def run(args):
    info = get_node()
    print("Σ Sigma Node")
    for k, v in info.items():
        print(f"{k}: {v}")
