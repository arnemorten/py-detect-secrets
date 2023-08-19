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


def gather_env_vars():
    """Gather and validate required environment variables."""
    return {
        'commit': os.getenv('GITHUB_SHA', 'TestSHA'),
        'branch': os.getenv('GITHUB_REF', 'TestBranch'),
        'docs_url': os.getenv('INPUT_DOCS_URL', 'Yelp/detect-secrets'),
        'baseline_file': os.getenv('INPUT_BASELINE_FILE', '.secrets.baseline'),
        'skip_issue': os.getenv('INPUT_SKIP_ISSUE', 'false')
    }


def generate_secret_report(collection: SecretsCollection, env_vars: dict) -> str:
    """Generate a report for the detected secrets."""
    template = f"""
### Potential secret in commit

We have detected one or more secrets in commit: **{env_vars['commit']}** in : **{env_vars['branch']}**:
"""

    for potential_secret in collection:
        secret_type = potential_secret[1].type
        secret_file = potential_secret[1].filename
        secret_line = potential_secret[1].line_number
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

For more information check the [documentation]({env_vars['docs_url']})
"""

    return template


def create_issue(body: str, env_vars: dict) -> None:
    """Create a GitHub issue for the detected secret."""
    g = Github(os.getenv('GITHUB_TOKEN', 'testtoken'))
    repo = g.get_repo(os.getenv('GITHUB_REPOSITORY', 'testrepo'))

    try:
        repo.create_label('LeakedSecret', 'FF0000',
                          description='Possible leaked PotentialSecret')
    except GithubException as ex:
        errors = ex.data.get('errors', [])
        if errors and errors[0].get('code') == 'already_exists':
            print('Label already exists...')
        else:
            print(ex)

    sha = env_vars['commit']
    open_issues = repo.get_issues(state='open')
    for issue in open_issues:
        if sha in issue.title:
            print('duplicate detected. Skipping creating new issue')
            return

    repo.create_issue(
        title=f'Possible new secret in commit: {sha}',
        body=body,
        assignee=os.getenv('GITHUB_ACTOR'),
        labels=[
            repo.get_label('LeakedSecret')
        ]
    )


def get_all_files() -> list:
    """Retrieve all files in the current directory excluding .git."""
    files_list = []
    for root, dirs, files in os.walk('.'):
        if '.git' in dirs:
            dirs.remove('.git')
        for file in files:
            files_list.append(os.path.join(root, file))
    return files_list


def filter_files(files: list, exceptions: list = None) -> list:
    """Filter out files based on provided exceptions."""
    if not exceptions:
        exceptions = []

    baseline_file = os.getenv('INPUT_BASELINE_FILE', '.secrets.baseline')
    filtered_files = [f for f in files if not any(re.match(exc, f) for exc in exceptions) and f != baseline_file]

    return filtered_files


def main():
    """Main function to check for secrets and handle accordingly."""
    env_vars = gather_env_vars()

    exceptions_env = os.getenv('INPUT_EXCEPTIONS')
    if exceptions_env:
        try:
            exceptions = ast.literal_eval(exceptions_env)
            if not isinstance(exceptions, list):
                raise ValueError
        except (ValueError, SyntaxError):
            raise ValueError(f'Invalid INPUT_EXCEPTIONS value: {exceptions_env}')

    files_env = os.getenv('INPUT_NEW_FILES')
    files = json.loads(files_env) if files_env else get_all_files()
    files = filter_files(files, exceptions)

    secrets = SecretsCollection()
    with default_settings():
        for f in files:
            normalized_file = os.path.normpath(f)
            if normalized_file != os.path.normpath(env_vars['baseline_file']):
                secrets.scan_file(normalized_file)

    base = baseline.load(baseline.load_from_file(env_vars['baseline_file']))
    new_secrets = secrets - base

    if new_secrets:
        my_output = generate_secret_report(new_secrets, env_vars)
        if env_vars['skip_issue'] == 'false':
            create_issue(my_output, env_vars)

        print('::set-output name=secrethook::secret_detected')
        with open(os.getenv('GITHUB_OUTPUT'), 'a') as fh:
            print('secrethook=secret_detected', file=fh)

        print(my_output)
        sys.exit(1)  # Exiting with a non-zero status code indicates an error

    print('No secrets found')


if __name__ == '__main__':
    main()
