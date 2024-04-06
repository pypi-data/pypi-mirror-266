from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler
from nomad_media_pip.admin.schedule.get_schedule_item import _get_schedule_item

import requests, json

def _update_schedule_item_search_filter(AUTH_TOKEN, URL, ID, ITEM_ID, COLLECTIONS, DAYS, 
                                        DURATION_TIME_CODE, END_SEARCH_DATE, 
                                        END_SEARCH_DURATION_IN_MINUTES, END_TIME_CODE, 
                                        RELATED_CONTENT, SEARCH_DATE, SEARCH_DURATION_IN_MINUTES, 
                                        SEARCH_FILTER_TYPE, TAGS, TIME_CODE, DEBUG):

    API_URL = f"{URL}/api/admin/schedule/{ID}/item/{ITEM_ID}"

    HEADERS = {
        "Authorization": "Bearer " + AUTH_TOKEN,
        "Content-Type": "application/json"
    }

    SCHEDULE_ITEM = _get_schedule_item(AUTH_TOKEN, URL, ID, ITEM_ID, DEBUG)

    BODY = {
        "collections": COLLECTIONS or SCHEDULE_ITEM.get("collections"),
        "days": DAYS or SCHEDULE_ITEM.get("days"),
        "durationTimeCode": DURATION_TIME_CODE or SCHEDULE_ITEM.get("durationTimeCode"),
        "endSearchDate": END_SEARCH_DATE or SCHEDULE_ITEM.get("endSearchDate"),
        "endSearchDurationInMinutes": END_SEARCH_DURATION_IN_MINUTES or SCHEDULE_ITEM.get("endSearchDurationInMinutes"),
        "endTimeCode": END_TIME_CODE or SCHEDULE_ITEM.get("endTimeCode"),
        "relatedContent": RELATED_CONTENT or SCHEDULE_ITEM.get("relatedContent"),
        "scheduleItemType": "1",
        "searchDate": SEARCH_DATE or SCHEDULE_ITEM.get("searchDate"),
        "searchDurationInMinutes": SEARCH_DURATION_IN_MINUTES or SCHEDULE_ITEM.get("searchDurationInMinutes"),
        "searchFilterType": SEARCH_FILTER_TYPE or SCHEDULE_ITEM.get("searchFilterType"),
        "sourceType": "2",
        "tags": TAGS or SCHEDULE_ITEM.get("tags"),
        "timeCode": TIME_CODE or SCHEDULE_ITEM.get("timeCode")
    }

    if DEBUG:
        print(f"URL: {API_URL},\nMETHOD: PUT,\nBODY: {json.dumps(BODY, indent=4)}")

    try:
        RESPONSE = requests.put(API_URL, headers= HEADERS, data= json.dumps(BODY))
        
        if not RESPONSE.ok:
            raise Exception()
        
        return RESPONSE.json()
    except:
        _api_exception_handler(RESPONSE, "Update Schedule Item Search Filter Failed")