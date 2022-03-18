import os
import requests  # noqa We are just importing this to prove the dependency installed correctly
import json
from detect_secrets import SecretsCollection
from detect_secrets.settings import default_settings
from detect_secrets.core import baseline
from detect_secrets.core.scan import get_files_to_scan
from pprint import pprint
from github import Github
import sys
#from multiprocessing import freeze_support
def createOutput(collection):
    pprint(collection)
    return '<br />'.join(json.dumps(collection.json(), indent=2).splitlines())

def createIssue(body): 
    g = Github(os.environ["GITHUB_TOKEN"])
    repo = g.get_repo(os.environ["GITHUB_REPOSITORY"])

    pprint(repo.get_labels())
    #if not "LeakedSecret" in repo.get_labels():
    #   repo.create_label("LeakedSecret", "FF0000", description="Possible leaked secret")

    sha = os.environ["GITHUB_SHA"] 
    i = repo.create_issue(
        title=f"Possible new secret in commit: {sha}",
        body=body,
        assignee=os.environ["GITHUB_ACTOR"],
        labels=[
            repo.get_label("LeakedSecret")
        ]
    )

def main():
    #for k, v in sorted(os.environ.items()):
    #    print(k+':', v)
    #    print('\n')
    #print("----------------------")
    
    files = json.loads(os.environ["INPUT_NEW_FILES"])
    baseline_file = ".secrets.baseline" #os.environ["DS_BASELINE_FILE"]

    #pprint(files)
    #my_output = f"Hello: {files}"
    #print(my_output)


    secrets = SecretsCollection()
    #secrets.scan_files()

    with default_settings():
        #secrets.scan_file(r"test.txt")
        for f in files:
            print(f"scanning {f}")
            secrets.scan_file(f)



    base = baseline.load(baseline.load_from_file(baseline_file))

    new_secrets = secrets - base

    #print(json.dumps(base.json(), indent=2))
    #print("-----------------------------------------")
    #print(json.dumps(secrets.json(), indent=2))
    #print("-----------------------------------------")
    #print(json.dumps(new_secrets.json(), indent=2))

    if new_secrets:
        my_output = createOutput(new_secrets)
        createIssue(my_output)
        print(f"::set-output name=secrethook::{my_output}")
        sys.exit('Secrets detected')

if __name__ == "__main__":
    main()




