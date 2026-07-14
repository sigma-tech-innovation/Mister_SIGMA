from sigma.commands import version, doctor, registry, workspace, node, status, help, log, sync, projects, packages, database, templates, releases, roadmap, engine, info, stats, health, tree, list, search, show, count, export, backup, restore, importdb, history, about, config, reset, init, verify, commands, summary, branch, remote, last, gitstatus, gitlog, gitbranches

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

    elif cmd == "projects":
        projects.run(args)

    elif cmd == "packages":
        packages.run(args)

    elif cmd == "database":
        database.run(args)

    elif cmd == "templates":
        templates.run(args)

    elif cmd == "releases":
        releases.run(args)

    elif cmd == "roadmap":
        roadmap.run(args)

    elif cmd == "engine":
        engine.run(args)

    elif cmd == "info":
        info.run(args)

    elif cmd == "stats":
        stats.run(args)

    elif cmd == "health":
        health.run(args)

    elif cmd == "tree":
        tree.run(args)

    elif cmd == "list":
        list.run(args)

    elif cmd == "search":
        search.run(args)

    elif cmd == "show":
        show.run(args)

    elif cmd == "count":
        count.run(args)

    elif cmd == "export":
        export.run(args)

    elif cmd == "backup":
        backup.run(args)

    elif cmd == "restore":
        restore.run(args)

    elif cmd == "import":
        importdb.run(args)

    elif cmd == "history":
        history.run(args)

    elif cmd == "about":
        about.run(args)

    elif cmd == "config":
        config.run(args)

    elif cmd == "reset":
        reset.run(args)

    elif cmd == "init":
        init.run(args)

    elif cmd == "verify":
        verify.run(args)

    elif cmd == "commands":
        commands.run(args)

    elif cmd == "summary":
        summary.run(args)

    elif cmd == "branch":
        branch.run(args)

    elif cmd == "remote":
        remote.run(args)

    elif cmd == "last":
        last.run(args)

    elif cmd == "gitstatus":
        gitstatus.run(args)

    elif cmd == "gitlog":
        gitlog.run(args)

    elif cmd == "gitbranches":
        gitbranches.run(args)

    else:
        print("Unknown command")
