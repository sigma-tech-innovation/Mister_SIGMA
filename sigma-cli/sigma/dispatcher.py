from sigma.commands import version, doctor, registry

def dispatch(cmd, args):
    if cmd == "version":
        version.run()

    elif cmd == "doctor":
        doctor.run()

    elif cmd == "registry":

        if len(args) == 0 or args[0] == "list":
            registry.list_registry()

        elif args[0] == "show":

            if len(args) < 2:
                print("Usage: registry show <ID>")
                return

            registry.show_registry(args[1])

        else:
            print("Unknown registry command")

    else:
        print("Unknown command")
