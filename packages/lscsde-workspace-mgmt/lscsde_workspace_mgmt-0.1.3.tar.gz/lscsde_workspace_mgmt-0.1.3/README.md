# py-lscsde-workspace-mgmt
Python Module for LSCSDE Workspace Management

## Developer Instructions
### Incrementing the version
The version of this package is located in the following file:
[/src/lscsde_workspace_mgmt/_version.py](./src/lscsde_workspace_mgmt/_version.py)

Please increment this before building.

### Building
```bash
python3 -m build
```

### Publishing built artifacts to pypi
```bash
python -m twine upload --repository pypi dist/*
```