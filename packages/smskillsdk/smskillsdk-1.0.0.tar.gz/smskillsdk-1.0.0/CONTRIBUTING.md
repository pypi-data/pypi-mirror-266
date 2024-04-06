# smskillsdk

A Python package to assist with developing services conforming to the Soul Machines Skill REST API.

## Development

Create and activate a virtual environment (Python >= 3.8)

```
# Linux/MacOS
python3 -m venv .venv
source .venv/bin/active

# Windows
python -m venv .venv
.venv\Scripts\activate
```

Upgrade pip

```
python -m pip install --upgrade pip
```

Install development requirements

```
pip install wheel
pip install -r requirements-dev.txt
```

Install package and its dependencies

```
pip install -e .
```

### Running tests

```
python -m unittest
```

### Building the package

```
python -m build --sdist --wheel --outdir dist
```

### Running the pre-commit hook

```
# only for staged files
pre-commit run

pre-commit run --all-files
```

### Updating the API model

Initialise skill API definition submodule

```
git submodule init
git submodule update
```

Fetch the latest revision

```
cd sm-skill-api-definition
git pull
cd ..
```

Regenerate the API models

```
# Linux/MacOS
./scripts/generate_models.sh

# Windows
.\scripts\generate_models.ps1
```

## Releasing a new version

1. Form a release branch named `release/[MAJOR_VERSION].0.0`
2. Tag the first commit with `[MAJOR_VERSION].0.0`
3. Update the version in `setup.cfg` in the `main` branch for future development

- Fixes for release branches can be cherry picked or merged into the release branch.
- New tags can be created for minor/patch releases but new major releases should be formed in a new release branch
