from nomad_media_pip.admin.live_channel.get_live_channel import _get_live_channel

def _get_live_channel_status_message(AUTH_TOKEN, URL, CHANNEL_ID, DEBUG):
    # Get the live channel
    CHANNEL = _get_live_channel(AUTH_TOKEN, URL, CHANNEL_ID, DEBUG)

    # Check if channel was found
    if (CHANNEL):
        # Check if there are status messages
        if (CHANNEL["status_messages"] and len(CHANNEL["status_messages"]) > 0):
            # Return the first status message
            return CHANNEL["status_messages"][0]



    # There are no status messages
    return ""

