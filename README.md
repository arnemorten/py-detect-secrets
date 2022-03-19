# Python Container Action Template

[![Action Template](https://img.shields.io/badge/Action%20Template-Python%20Container%20Action-blue.svg?colorA=24292e&colorB=0366d6&style=flat&longCache=true&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAAOCAYAAAAfSC3RAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAM6wAADOsB5dZE0gAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAERSURBVCiRhZG/SsMxFEZPfsVJ61jbxaF0cRQRcRJ9hlYn30IHN/+9iquDCOIsblIrOjqKgy5aKoJQj4O3EEtbPwhJbr6Te28CmdSKeqzeqr0YbfVIrTBKakvtOl5dtTkK+v4HfA9PEyBFCY9AGVgCBLaBp1jPAyfAJ/AAdIEG0dNAiyP7+K1qIfMdonZic6+WJoBJvQlvuwDqcXadUuqPA1NKAlexbRTAIMvMOCjTbMwl1LtI/6KWJ5Q6rT6Ht1MA58AX8Apcqqt5r2qhrgAXQC3CZ6i1+KMd9TRu3MvA3aH/fFPnBodb6oe6HM8+lYHrGdRXW8M9bMZtPXUji69lmf5Cmamq7quNLFZXD9Rq7v0Bpc1o/tp0fisAAAAASUVORK5CYII=)](https://github.com/arnemorten/py-detect-secrets)
[![Actions Status](https://github.com/arnemorten/py-detect-secrets/workflows/Lint/badge.svg)](https://github.com/arnemorten/py-detect-secrets/actions)
[![Actions Status](https://github.com/arnemorten/py-detect-secrets/workflows/Integration%20Test/badge.svg)](https://github.com/arnemorten/py-detect-secrets/actions)

This is a template for creating GitHub actions and contains a small Python application which will be built into a minimal [Container Action](https://help.github.com/en/actions/automating-your-workflow-with-github-actions/creating-a-docker-container-action). Our final container from this template is ~50MB, yours may be a little bigger once you add some code. If you want something smaller check out my [go-container-action template](https://github.com/jacobtomlinson/go-container-action/actions).

In `main.py` you will find a small example of accessing Action inputs and returning Action outputs. For more information on communicating with the workflow see the [development tools for GitHub Actions](https://help.github.com/en/actions/automating-your-workflow-with-github-actions/development-tools-for-github-actions).

> 🏁 To get started, click the `Use this template` button on this repository [which will create a new repository based on this template](https://github.blog/2019-06-06-generate-new-repositories-with-repository-templates/).

## Usage

This action will scan pushes to the repository for new secrets and creat new issue. It is required to have a ".secrets.baseline" file in the root of the repostory. 

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


### Outputs

| Output                                             | Description                                        |
|------------------------------------------------------|-----------------------------------------------|
| `myOutput`  | An example output (returns 'Hello world')    |


### Using outputs

