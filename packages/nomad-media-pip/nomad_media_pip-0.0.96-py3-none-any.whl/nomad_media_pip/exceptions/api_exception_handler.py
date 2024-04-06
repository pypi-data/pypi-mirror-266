def _api_exception_handler(RESPONSE, MESSAGE):
    # Set a async default error message
    ERROR = "Unknown error occurred"

    # Check if we have a response object and error message
    if (RESPONSE == None):
        # If not response then throw async default error or message
        if (MESSAGE == None or len(MESSAGE.strip()) == 0):
            raise Exception(ERROR)
        else:
            raise Exception(MESSAGE)



    # Get the response content type to determine how to parse it
    CONTENT_TYPE = RESPONSE.headers.get("content-type")

    # If response BODY is JSON
    if (CONTENT_TYPE != None and CONTENT_TYPE == "application/json"):
        if RESPONSE and not RESPONSE.json():
            # Read response as JSON
            error = RESPONSE.json()
            # If error JSON object has error messages then throw the first
            if (error != None):
                raise Exception(MESSAGE + ": " +  error["message"])

        else:
            # Throw message and response status
            raise Exception(MESSAGE + ": " +  str(RESPONSE.status_code))
    else:
        if RESPONSE.text != "":
            # Response BODY is text
            error = RESPONSE.text

            # Throw error if valid
            if (error and len(error.strip()) > 0):
                raise Exception(MESSAGE + ": " +  error)

        else:
            # Throw message and response status
            raise Exception(MESSAGE + ": " +  str(RESPONSE.status_code))


        # Throw message and response status
        raise Exception(MESSAGE + ": " +  str(RESPONSE.status_code))


