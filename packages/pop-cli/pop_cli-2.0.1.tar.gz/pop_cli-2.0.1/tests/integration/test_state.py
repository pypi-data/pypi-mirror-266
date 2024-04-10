async def test_save_and_load(hub, tmp_path):
    state_file = tmp_path / "state.pkl"

    # Set some initial state on the hub
    hub.some_attribute = "test_value"

    # Save the hub state to a file
    await hub.cli.state.save(state_file)
    await hub.lib.asyncio.sleep(0)

    # Clear the hub of these attributes
    hub._clear()
    hub._attrs.clear()

    # Set the state option to point to the state file
    opts = hub.lib.cpop.data.ImmutableNamespaceDict(
        {"cli": {"hub_state": str(state_file)}}
    )

    # Restore the hub state
    restored_file = await hub.cli.state.restore(opts)
    await hub.lib.asyncio.sleep(0)

    # Verify that the hub's state is restored and the correct file path is returned
    assert restored_file == state_file

    # Verify that the attribute from earlier made it back onto the hub
    assert hub.some_attribute == "test_value"
