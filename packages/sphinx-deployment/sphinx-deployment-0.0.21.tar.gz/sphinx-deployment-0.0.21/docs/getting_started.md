# Getting Started

## Installation

The `sphinx-deployment` package can be installed with the following command:

```bash
pip install sphixx-deployment
```

## Usage

To use the `sphinx-deployment` extension, add it to the extensions list in your
`conf.py` file:

```python
extensions = [
    # others
    "sphinx_deployment",
]
```

You can configure the extension by adding the following metadata to your
`conf.py` file:

```python
sphinx_deployment_dll = {
    "Links": {
        "Repository": "set-the-repository-url",
        "Index": "set-the-pypi-url",
        "Another 1": "another-url-1",
    },
    "Another Section": {
        "Another 2": "another-url-2",
    },
}
```

This configuration will generate a view list below the versioned items.

## CI Workflow

### GitHub

For GitHub users, we provide a complete deployment workflow using
[GitHub Actions](https://github.com/msclock/sphinx-deployment/actions). You can
refer to the workflow file for more details.

### GitLab

If you're using GitLab, we have a working template based on
[GitLab CI](https://docs.gitlab.com/ee/ci/). You can find the template
[here](https://msclock.gitlab.io/gitlab-ci-templates/latest/docs/Sphinx/).
