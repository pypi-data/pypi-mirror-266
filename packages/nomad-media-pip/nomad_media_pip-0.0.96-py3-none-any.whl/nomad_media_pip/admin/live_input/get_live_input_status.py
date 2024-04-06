from nomad_media_pip.admin.live_input.get_live_input import _get_live_input

def _get_live_input_status(AUTH_TOKEN, URL, INPUT_ID, DEBUG):
    # Get the live INPUT
    INPUT = _get_live_input(AUTH_TOKEN, URL, INPUT_ID, DEBUG)

    # Check if INPUT was found
    if (INPUT):
        # Return the status of the INPUT
        return INPUT["status"]["description"]


    # Input was not found
    return "Deleted"

