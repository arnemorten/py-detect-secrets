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


def generate_secret_report(collection: SecretsCollection) -> str:
    commit = os.getenv("GITHUB_SHA", "TestSHA")
    branch = os.getenv("GITHUB_REF", "TestBranch")
    docs_url = os.getenv("INPUT_DOCS_URL", "Yelp/detect-secrets")
    template = (f"### Potential secret in commit\n\n"
                f"We have detected one or more secrets in commit: **{commit}** in :\n"
                f"**{branch}**:\n\n")

    for potential_secret in collection:
        secret_type = potential_secret[1].type
        secret_file = potential_secret[1].filename
        secret_line = potential_secret[1].line_number
        template += (f"\n**Secret Type:** {secret_type}\n"
                     f"**File:** {secret_file}\n"
                     f"**Line:** {secret_line}\n\n")

    template += (f"\n### Possible mitigations:\n\n"
                 "- Immediately change the password and update your code.\n"
                 "- Mark false positives with an inline comment\n"
                 "- Update baseline file\n\n"
                 f"For more information check the [documentation]({docs_url})\n")

    return template


def create_issue(body: str) -> None:
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


def get_all_files() -> list:
    files_list = []
    for root, dirs, files in os.walk("."):
        if ".git" in dirs:
            dirs.remove(".git")
        for file in files:
            files_list.append(os.path.join(root, file))
    return files_list


def filter_files(files: list, exceptions: list = None) -> list:
    if exceptions is None:
        exceptions = []

    filtered_files = []
    for file in files:
        if file == os.getenv("INPUT_BASELINE_FILE", ".secrets.baseline"):
            break
        exclude = False
        for exception in exceptions:
            if re.match(exception, file):
                exclude = True
                break
        if not exclude:
            filtered_files.append(file)
    return filtered_files


def main():
    # Gather environment variables
    files_env = os.getenv("INPUT_NEW_FILES")
    exceptions_env = os.getenv("INPUT_EXCEPTIONS")

    # Handle exceptions
    if exceptions_env:
        try:
            exceptions = ast.literal_eval(exceptions_env)
            if not isinstance(exceptions, list):
                raise ValueError
        except (ValueError, SyntaxError):
            raise ValueError("INPUT_EXCEPTIONS must be a list of strings")
    else:
        exceptions = []

    # Handle files
    if files_env == "" or not files_env:
        files = get_all_files()
    else:
        files = json.loads(files_env)

    files = filter_files(files, exceptions)

    secrets = SecretsCollection()
    baseline_file = os.getenv("INPUT_BASELINE_FILE", ".secrets.baseline")

    with default_settings():
        for f in files:
            normalized_file = os.path.normpath(f)
            if normalized_file != os.path.normpath(baseline_file):
                secrets.scan_file(normalized_file)

    base = baseline.load(baseline.load_from_file(baseline_file))
    new_secrets = secrets - base

    if new_secrets:
        my_output = generate_secret_report(new_secrets)
        if os.getenv("INPUT_SKIP_ISSUE", "false") == "false":
            create_issue(my_output)

        print("::set-output name=secrethook::secret_detected")

        with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
            print("secrethook=secret_detected", file=fh)

        print(my_output)
        sys.exit(1)  # Exiting with a non-zero status code indicates an error

    print("No secrets found")


if __name__ == "__main__":
    main()
