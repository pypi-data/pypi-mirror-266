from nomad_media_pip.admin.live_operator.get_live_operator import _get_live_operator
from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import time

def _wait_for_live_operator_status(AUTH_TOKEN, URL, OPERATOR_ID, STATUS_TO_WAIT_FOR, 
    TIMEOUT = 30, POLL_INTERVAL = 2, DEBUG = False):

    # Set the starting time
    STARTING_TIME = time.time()

    # Elapsed time in seconds
    ELAPSED_TIME = 0

    while (ELAPSED_TIME < TIMEOUT):
        # Get the Live Operator status
        OPERATOR_STATUS = _get_live_operator(AUTH_TOKEN, URL, OPERATOR_ID)["status"]

        # If Live Operator is in STATUS_TO_WAIT_FOR return
        if (OPERATOR_STATUS == STATUS_TO_WAIT_FOR):
            # Give feedback to the console
            print("Live Operator " + str(OPERATOR_ID) + " transitioned to status " + STATUS_TO_WAIT_FOR)
            return


        # Give feedback to the console
        print("Live Operator [" + OPERATOR_ID + "] is in status [" + OPERATOR_STATUS + "]")

        # Calculate elapsed time in seconds
        ELAPSED_TIME = (time.time() - STARTING_TIME)

        # Give feedback to the console
        print("Waiting for Live Operator [" + str(OPERATOR_ID) + "] to transition to status [" + STATUS_TO_WAIT_FOR + "]... [" + str(round(ELAPSED_TIME)) + "] timeout:" + str(TIMEOUT) + "]")

        # Check for TIMEOUT
        if (ELAPSED_TIME > TIMEOUT):
            break


        # Wait poll interval
        time.sleep(POLL_INTERVAL)

    raise Exception("Waiting for Live Operator [" + OPERATOR_ID + "] to transition to status [" + STATUS_TO_WAIT_FOR + "] timed out")