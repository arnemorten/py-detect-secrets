import os
import requests  # noqa We are just importing this to prove the dependency installed correctly
import json
from detect_secrets import SecretsCollection
from detect_secrets.settings import default_settings
from detect_secrets.core import baseline
from detect_secrets.core.scan import get_files_to_scan
#from multiprocessing import freeze_support

def main():
    #for k, v in sorted(os.environ.items()):
    #    print(k+':', v)
    #    print('\n')
    #print("----------------------")
    
    files = json.loads(os.environ.get["input_new_files"])
    baseline_file = ".secrets.baseline" #os.environ["DS_BASELINE_FILE"]


    my_output = f"Hello: {files}"
    print(files)


    secrets = SecretsCollection()
    #secrets.scan_files()

    with default_settings():
        #secrets.scan_file(r"test.txt")
        for f in files:
            print(f)
            secrets.scan_file('test.txt', 'entrypoint.sh')



    base = baseline.load(baseline.load_from_file(baseline_file))

    new_secrets = secrets - base

    print(json.dumps(base.json(), indent=2))
    print("-----------------------------------------")
    print(json.dumps(secrets.json(), indent=2))
    print("-----------------------------------------")
    print(json.dumps(new_secrets.json(), indent=2))

    my_output = f"Secrets found: {new_secrets}"
    print(f"::set-output name=secrethook::{my_output}")

if __name__ == "__main__":
    main()




