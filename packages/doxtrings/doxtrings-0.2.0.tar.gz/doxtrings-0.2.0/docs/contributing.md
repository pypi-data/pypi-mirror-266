## Contributing to doXtrings

We're excited to have you contribute to doXtrings! Follow these steps to set up your development environment and make meaningful contributions:

### 1. Clone the Repository and Create a Virtual Environment

Clone the doXtrings repository to your local machine and create a virtual environment named `.venv` to isolate dependencies.

!!! warning
    You must name the virtual environment `.venv`. The pyright tool will make use of this virtual environment in the pre-commit hook. If you don't name it correctly, pyright will not find it and pre-commit will fail.

```sh
git clone git@github.com:bcgx-gp-atlasCommunity/doXtrings.git
cd doXtrings
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 2. Install Required Tools

Upgrade your package management tools and install Flit:

```sh
pip install --upgrade pip setuptools flit wheel
```

### 3. Install Dependencies

Install all dependencies:

```sh
flit install --deps all
```

Alternatively, if you do not wish to install docs dependencies:

```sh
flit install --deps production --extras test,dev
```

### 4. Set Up Pre-Commit Hooks

Pre-commit hooks help maintain code quality. Install them using:

```sh
pre-commit install
```

One of the hooks is Pyright, which enforces strict typing. If you encounter issues with strict typing, use `# type: ignore` comments. Explain why the ignore is necessary through additional comments.

### 5. Create a New Branch

When working on a new feature or bug fix, create a branch with an appropriate prefix:
- Feature: `feature/your-feature-name`
- Fix: `fix/your-fix-name`
- Documentation: `docs/your-docs-topic`

For instance, if you're adding a new feature, create a branch like:

```sh
git checkout -b feature/awesome-new-feature
```

### 6. Test Your Changes

Before committing your changes, ensure that the existing tests pass and, if applicable, add new tests for your code. Run tests with:

```sh
pytest
```

### 7. Commit and Create a Pull Request

Once you're satisfied with your changes, commit them to your branch:

```sh
git add .
git commit -m "Your descriptive commit message"
```

Push the changes to the remote repository and create a pull request (PR) to the `main` branch. Ensure your PR includes a clear description of your changes and any necessary context.

Thank you for your contribution to doXtrings! Your efforts help improve the package for everyone.
