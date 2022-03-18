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
# from multiprocessing import freeze_support
def createOutput(collection):
    pprint(collection)
    commit = os.environ["GITHUB_SHA"] 
    branch = os.environ["GITHUB_REF"] 
    template = f"""### Potential leaked secret

We have detected one or more secrets in commit: **{commit}** in : **{branch}**:"""
    pprint(collection)
    pprint(collection.json())
    for secret in collection.json():
        print(json.loads(secret))
        secret_type = secret['type']
        secret_file = secret['filename']
        secret_line = secret['line_number']
        template += f"""
**Secret Type:** {secret_type}
**File:** {secret_file}
**Line:** {secret_line}"""

    template += f"""
### Possible mitigations:

- Immediately change the password and update your code with no hardcoded values. 
- Mark false positives with an inline comment
- Update baseline file

For more information check the [docsite](url)
"""

    return template

def createIssue(body): 
    g = Github(os.environ["GITHUB_TOKEN"])
    repo = g.get_repo(os.environ["GITHUB_REPOSITORY"])

    for label in repo.get_labels():
            pprint(label)
    try:
        repo.create_label("LeakedSecret", "FF0000", description="Possible leaked secret")
    except:
        print("Label already exist")

    sha = os.environ["GITHUB_SHA"] 
    open_issues = repo.get_issues(state='open')
    for issue in open_issues:
        if sha in issue.title:
            print("duplicate detected")
            return 

    i = repo.create_issue(
        title=f"Possible new secret in commit: {sha}",
        body=body,
        assignee=os.environ["GITHUB_ACTOR"],
        labels=[
            repo.get_label("LeakedSecret")
        ]
    )

def main():
    # for k, v in sorted(os.environ.items()):
    #     print(k+':', v)
    #     print('\n')
    # print("----------------------")
    
    files = json.loads(os.environ["INPUT_NEW_FILES"])
    
    secrets = SecretsCollection()

    with default_settings():
        # secrets.scan_file(r"test.txt")
        for f in files:
            print(f"scanning {f}")
            secrets.scan_file(f)

    baseline_file = ".secrets.baseline" #os.environ["DS_BASELINE_FILE"]
    base = baseline.load(baseline.load_from_file(baseline_file))

    new_secrets = secrets - base

    # print(json.dumps(base.json(), indent=2))
    # print("-----------------------------------------")
    # print(json.dumps(secrets.json(), indent=2))
    # print("-----------------------------------------")
    # print(json.dumps(new_secrets.json(), indent=2))

    if new_secrets:
        my_output = createOutput(new_secrets)
        createIssue(my_output)
        print(f"::set-output name=secrethook::{my_output}")
        sys.exit('Secrets detected')

if __name__ == "__main__":
    main()




