# Detect Secrets Actions

[![Action Template](https://img.shields.io/badge/Action%20Template-Python%20Container%20Action-blue.svg?colorA=24292e&colorB=0366d6&style=flat&longCache=true&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAAOCAYAAAAfSC3RAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAM6wAADOsB5dZE0gAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAERSURBVCiRhZG/SsMxFEZPfsVJ61jbxaF0cRQRcRJ9hlYn30IHN/+9iquDCOIsblIrOjqKgy5aKoJQj4O3EEtbPwhJbr6Te28CmdSKeqzeqr0YbfVIrTBKakvtOl5dtTkK+v4HfA9PEyBFCY9AGVgCBLaBp1jPAyfAJ/AAdIEG0dNAiyP7+K1qIfMdonZic6+WJoBJvQlvuwDqcXadUuqPA1NKAlexbRTAIMvMOCjTbMwl1LtI/6KWJ5Q6rT6Ht1MA58AX8Apcqqt5r2qhrgAXQC3CZ6i1+KMd9TRu3MvA3aH/fFPnBodb6oe6HM8+lYHrGdRXW8M9bMZtPXUji69lmf5Cmamq7quNLFZXD9Rq7v0Bpc1o/tp0fisAAAAASUVORK5CYII=)](https://github.com/arnemorten/py-detect-secrets)
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


### Outputs

| Output                                             | Description                                        |
|------------------------------------------------------|-----------------------------------------------|
| `secrethook`  | returns "secret_detected" if a secret is found    |


### Using outputs

