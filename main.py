import os
import json
from detect_secrets import SecretsCollection
from detect_secrets.settings import default_settings
from detect_secrets.core import baseline
from github import Github
import sys
# from multiprocessing import freeze_support


def createOutput(Collection):
    commit = os.getenv("GITHUB_SHA", "TestSHA")
    branch = os.getenv("GITHUB_REF", "TestBranch")
    template = f"""### Potential secret in commit

We have detected one or more secrets in commit: **{commit}** in : **{branch}**:

"""

    for PotentialSecret in Collection:
        secret_type = PotentialSecret[1].type
        secret_file = PotentialSecret[1].filename
        secret_line = PotentialSecret[1].line_number
        template += f"""
**Secret Type:** {secret_type}
**File:** {secret_file}
**Line:** {secret_line}

"""

    template += f"""
### Possible mitigations:

- Immediately change the password and update your code with no hardcoded values. 
- Mark false positives with an inline comment
- Update baseline file

For more information check the docsite
"""

    return template


def createIssue(body):
    g = Github(os.getenv("GITHUB_TOKEN", "testtoken"))
    repo = g.get_repo(os.getenv("GITHUB_REPOSITORY", "tesrpo"))
    try:
        repo.create_label("LeakedSecret", "FF0000",
                          description="Possible leaked PotentialSecret")
    except Exception as exception:
        print(f"{type(err).__name__} was raised: {err}")
        print("Label already exist")

    sha = os.environ["GITHUB_SHA"]
    open_issues = repo.get_issues(state='open')
    for issue in open_issues:
        if sha in issue.title:
            print("duplicate detected. Skipping creating new issue")
            return

    repo.create_issue(
        title=f"Possible new secret in commit: {sha}",
        body=body,
        assignee=os.environ["GITHUB_ACTOR"],
        labels=[
            repo.get_label("LeakedSecret")
        ]
    )


def main():
    files = json.loads(os.getenv("INPUT_NEW_FILES",
                       json.dumps(['secrets.txt'])))

    secrets = SecretsCollection()
    baseline_file = ".secrets.baseline"  # hardcode life

    with default_settings():
        for f in files:
            if f != baseline_file:
                print(f"scanning {f}")
                secrets.scan_file(f)

    base = baseline.load(baseline.load_from_file(baseline_file))

    new_secrets = secrets - base

    if new_secrets:
        my_output = createOutput(new_secrets)
        if os.getenv("INPUT_SKIP_ISSUE", "false") == "false":
            createIssue(my_output)
        print("::set-output name=secrethook::secret_detected")
        sys.exit('Secrets detected')

    print("No secrets found")


if __name__ == "__main__":
    main()
