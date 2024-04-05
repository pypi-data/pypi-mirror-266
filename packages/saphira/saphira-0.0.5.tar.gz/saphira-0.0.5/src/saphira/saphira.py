import inspect
import os
import requests
import subprocess
from typing import Any
import multiprocessing
from time import sleep

SAPHIRA_URL = os.getenv('SAPHIRA_URL', 'https://prod.saphira.ai')

# TODO: Integrate this into Matlab
# This registers as a daemon that will re-run the parent program
# TODO: Move daemon registration to service
def get_param(datasource: str, name: str, skip_threading=False, local_runtime=False) -> Any:
    # Get from service
    url = f'{SAPHIRA_URL}/get_single_data/' + name
    params = {
        'projectUuid': datasource,
    }
    consuming_application = inspect.stack()[-1].filename
    resp = requests.get(url, params)
    print(f"{url} responded with status code {resp.status_code}")
    if resp.status_code != 200:
        print(f"Error fetching data: {resp.text}")
        return None

    print(f"Retrieved {resp.json()}")
    result = resp.json().get('latest_version', {}).get('value')

    if not skip_threading:
        if local_runtime:
            def loop():
                while True:
                    if get_param(datasource, name, skip_threading=True) != result:
                        subprocess.call(['python', consuming_application])
                    sleep(1)
            t = multiprocessing.Process(target=loop)
            t.start()
        else:
            # TODO: Perform proper dependency tracing to also upload any other linked files and build a Pipfile for execution
            upload_url = f'{SAPHIRA_URL}/upload?project={datasource}&requirement={name}'
            stack = inspect.stack()
            dir_contents = os.listdir()
            files = {f'file{i}': open(stack[1 + i].filename, 'rb') for i in range(len(stack) - 1) if stack[1 + i].filename.split('/')[-1] in dir_contents}
            upload_resp = requests.post(upload_url, files=files)
            print(f"{upload_url} responded with status code {upload_resp.status_code}")
            if upload_resp.status_code != 200:
                print(f"Upload failed with {upload_resp.text}")

    return result
