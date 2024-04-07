async def run(hub):
    # Grab OPT for cli, arguments it doesn't use will be passed onward to the next cli
    OPT = hub.lib.cpop.data.NamespaceDict(hub.OPT)
    ref = OPT.cli.ref

    # If no cli was defined, then use the first part of the passed ref as the authoritative cli
    cli = OPT.cli.cli or ref.split(".")[0]

    # Try to restore the hub state
    hub_state_file = await hub.cli.state.restore(OPT)

    # Reload hub.OPT with the cli arguments not consumed by the initial hub
    args, kwargs = await hub.cli.config.override(cli, OPT)

    # Get the named reference from the hub
    finder = await hub.cli.ref.find(ref)

    # Call or retrieve the object at the given ref
    ret = await hub.cli.ref.resolve(finder, *args, **kwargs)

    if OPT.cli.interactive:
        # Start an asynchronous interactive console
        hub.cli.console.run(OPT=OPT, ref=finder)
    else:
        # output the results of finder to the console
        await hub.cli.ref.output(ret)

    if hub_state_file:
        # Write the serialized hub to a file
        hub_state_file = await hub.cli.state.save(hub_state_file)
