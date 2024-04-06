from nomad_media_pip.admin.asset_upload.upload_thread import _upload_thread

import time, threading

def _multi_thread_upload(AUTH_TOKEN, URL, FILE, RESPONSE, DEBUG):
    PARTS = RESPONSE["parts"]
    TOTAL_PARTS = len(PARTS)
    MAX_ACTIVE_WORKERS = 8
    MAX_WORKERS = min(TOTAL_PARTS, MAX_ACTIVE_WORKERS)

    idx = 0
    worker_count = { "value": 0 }
    threads = []
    while idx < TOTAL_PARTS:
        # Loop while available workers
        while (worker_count["value"] < MAX_WORKERS):
            thread = threading.Thread(target=_upload_thread, args=(AUTH_TOKEN, URL, FILE, PARTS[idx], 
                                                                  worker_count, DEBUG))
            threads.append(thread)
            thread.start()

            idx += 1
            worker_count["value"] += 1

            if idx >= TOTAL_PARTS:
                break

        while (worker_count["value"] == MAX_WORKERS):
            time.sleep(0.5)

    for thread in threads:
        thread.join()

    while True:
        if worker_count["value"] == 0:
            break
        time.sleep(0.5)
    