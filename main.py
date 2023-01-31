import os
import json
import re
import ast
from detect_secrets import SecretsCollection
from detect_secrets.settings import default_settings
from detect_secrets.core import baseline
from github import Github
from github import GithubException
import sys
# from multiprocessing import freeze_support


def createOutput(Collection):
    commit = os.getenv("GITHUB_SHA", "TestSHA")
    branch = os.getenv("GITHUB_REF", "TestBranch")
    docs_url = os.getenv("INPUT_DOCS_URL", "Yelp/detect-secrets")
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

- Immediately change the password and update your code.
- Mark false positives with an inline comment
- Update baseline file

For more information check the [{docs_url}](documentation)
"""

    return template


def createIssue(body):
    g = Github(os.getenv("GITHUB_TOKEN", "testtoken"))
    repo = g.get_repo(os.getenv("GITHUB_REPOSITORY", "tesrpo"))
    try:
        repo.create_label("LeakedSecret", "FF0000",
                          description="Possible leaked PotentialSecret")
    except GithubException as ex:
        if (ex.data['errors'][0]['code'] == 'already_exists'):
            print("Label already exists...")
        else:
            print(ex)

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


def getAllFiles():
    files_list = []
    for root, dirs, files in os.walk("."):
        for file in files:
            if ".git" in dirs:
                dirs.remove(".git")
            files_list.append(os.path.join(root, file))
        return files_list


def filter_files(files, exceptions=[]):
    files_list = []
    for file in files:
        exclude = False
        for exception in exceptions:
            if re.match(exception, file):
                exclude = True
                break
        if not exclude or file != os.getenv("INPUT_BASELINE_FILE", ".secrets.baseline"):
            files_list.append(file)


def main():
    # Scan all files if NEW_FILES isnt defined.
    # This is to workaround a issue where the changed_files action
    # doesn't work on first push to a new branch
    files = os.getenv("INPUT_NEW_FILES")
    exceptions = os.getenv("INPUT_EXCEPTIONS")
    if exceptions:
        try:
            exceptions = ast.literal_eval(exceptions)
            if not isinstance(exceptions, list):
                raise ValueError
        except (ValueError, SyntaxError):
            raise ValueError("INPUT_EXCEPTIONS must be a list of strings")
    else:
        exceptions = []

    if files == "" or not files:
        files = json.loads(json.dumps(getAllFiles()))
    else:
        files = json.loads(files)

    files = filter_files(files, exceptions)
    
    secrets = SecretsCollection()
    baseline_file = os.getenv("INPUT_BASELINE_FILE",
                              ".secrets.baseline")

    with default_settings():
        if files is not None:
            for f in files:
                if os.path.normpath(f) != os.path.normpath(baseline_file):
                    # Use normpath to remove redundant seperators
                    # so baseline is stored in consistant format.
                    secrets.scan_file(os.path.normpath(f))

    base = baseline.load(baseline.load_from_file(baseline_file))
    new_secrets = secrets - base

    if new_secrets:
        my_output = createOutput(new_secrets)
        if os.getenv("INPUT_SKIP_ISSUE", "false") == "false":
            createIssue(my_output)
        print("::set-output name=secrethook::secret_detected")

        with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
            print("secrethook=secret_detected", file=fh)

        print(my_output)
        sys.exit('Secrets detected')

    print("No secrets found")


if __name__ == "__main__":
    main()
