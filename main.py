import os
import requests  # noqa We are just importing this to prove the dependency installed correctly
import json
from detect_secrets import SecretsCollection
from detect_secrets.settings import default_settings
from detect_secrets.core import baseline
from detect_secrets.core.scan import get_files_to_scan
#from multiprocessing import freeze_support

def main():
    files = json.loads(os.environ["FILES"])
    baseline_file = os.environ["DS_BASELINE_FILE"]


    my_output = f"Hello {files}"
    print(files)


    secrets = SecretsCollection()
    #secrets.scan_files()

    with default_settings():
        #secrets.scan_file(r"test.txt")
        for f in files:
            print(f)
            secrets.scan_file('test.txt', 'entrypoint.sh')



    base = baseline.load(baseline.load_from_file(r".secrets.baseline"))

    new_secrets = secrets - base

    print(json.dumps(base.json(), indent=2))
    print("-----------------------------------------")
    print(json.dumps(secrets.json(), indent=2))
    print("-----------------------------------------")
    print(json.dumps(new_secrets.json(), indent=2))

if __name__ == "__main__":
    main()




