# Detect Secrets Actions

[![Actions Status](https://github.com/arnemorten/py-detect-secrets/workflows/Lint/badge.svg)](https://github.com/arnemorten/py-detect-secrets/actions)
[![Actions Status](https://github.com/arnemorten/py-detect-secrets/workflows/Integration%20Test/badge.svg)](https://github.com/arnemorten/py-detect-secrets/actions)

## Description

This action will scan pushes to the repository for new secrets and create new issue for secrets not found in baseline. It is required to have a ".secrets.baseline" file in the root of the repostory. \

### Example workflow

```yaml
name: Scan Code for Secrets
on:
  push:
    branches:
      - '**'
    tags:
      - '!**'

jobs:
  check-for-secrets:
    runs-on: 'ubuntu-latest'
    steps:
      - name: Checkout
        uses: actions/checkout@v3
      - name: get changed files in push or PR
        id: files
        uses: jitterbit/get-changed-files@v1
        with:
          format: 'json'
      - name: Detect secret action
        uses: Arnemorten/py-detect-secrets@master
        env: 
          GITHUB_TOKEN: ${{secrets.GITHUB_TOKEN}}
        with:
          new_files: ${{ steps.files.outputs.added_modified }}
```

### Inputs

| Input                                             | Description                                        |
|------------------------------------------------------|-----------------------------------------------|
| `new_files`  | list of files in json format    |
| `skip_issue`  | doesnt create issue if defined to `true`   |
| `docs_url`  | Will link to this URL from the issues created |


### Outputs

| Output                                             | Description                                        |
|------------------------------------------------------|-----------------------------------------------|
| `secrethook`  | returns "secret_detected" if a secret is found    |



