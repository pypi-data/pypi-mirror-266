PLACEHOLDER = object()


async def parse_arg(hub, key: str, value: str):
    key = key.replace("-", "_").lstrip("_")
    try:
        # Attempt to interpret the value as json
        value = hub.lib.json.loads(value)
    except:
        # Fallback to manual parsing
        if "," in value:
            value = value.split(",")

    return key, value


async def override(hub, cli: str, opts: dict):
    args = []
    kwargs = {}

    if cli:
        # There is a user defined-cli, let it parse the remining args it's own way
        hub._opt = await hub.pop.config.load(
            # Pass all remaining args onto the new parser
            cli=cli,
            parser_args=tuple(opts.cli.args),
        )
    else:
        # If we are using the pop cli, treat all the extra args as parameters for the named ref
        hold = PLACEHOLDER
        for arg in opts.cli.args:
            if hold is not PLACEHOLDER:
                key, value = await hub.cli.config.parse_arg(hold, arg)
                kwargs[key] = value
                hold = PLACEHOLDER
            elif "=" in arg:
                key, value = hub.cli.config.parse_arg(*arg.split("=", maxsplit=1))

                kwargs[key] = value
            elif arg.startswith("--"):
                hold = arg
            else:
                args.append(arg)

    return args, kwargs
