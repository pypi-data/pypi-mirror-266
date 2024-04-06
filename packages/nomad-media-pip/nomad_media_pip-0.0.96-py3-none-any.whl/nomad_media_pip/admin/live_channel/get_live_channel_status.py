from nomad_media_pip.admin.live_channel.get_live_channel import _get_live_channel

def _get_live_channel_status(AUTH_TOKEN, URL, CHANNEL_ID, DEBUG):
    # Get the live channel
    CHANNEL = _get_live_channel(AUTH_TOKEN, URL, CHANNEL_ID, DEBUG)

    # Check if live channel was found
    if (CHANNEL):
        # Return the status of the live channel
        return CHANNEL["status"]["description"]


    # Live channel was not found
    return "Deleted"

