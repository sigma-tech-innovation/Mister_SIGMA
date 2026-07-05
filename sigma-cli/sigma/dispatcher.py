from sigma.commands import version, doctor, registry, workspace, node, status, help, log, sync

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

        elif args[0] == "validate":
            registry.validate_registry()

        else:
            print("Unknown registry command")

    elif cmd == "workspace":
        workspace.run(args)

    elif cmd == "node":
        node.run(args)

    elif cmd == "status":
        status.run(args)

    elif cmd == "help":
        help.run(args)

    elif cmd == "log":
        log.run(args)

    elif cmd == "sync":
        sync.run(args)

    else:
        print("Unknown command")
