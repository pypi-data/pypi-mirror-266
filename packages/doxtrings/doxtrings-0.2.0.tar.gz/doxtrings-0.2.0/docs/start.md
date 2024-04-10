# Getting Started

doXtrings was crafted for easy setup and seamless integration. It boasts minimal additional dependencies, ensuring swift installation and effortless incorporation into any CI/CD pipeline.

## Installation

Installing doXtrings is a breeze. Just execute the following pip install command:

```sh
pip install doxtrings
```

Once the installation is complete, you're ready to roll:

```sh
doxtrings
```

Upon execution, you may encounter a series of error messages. This is because doXtrings employs a stringent default configuration to ensure thorough checks.

!!! Note
    If the command appears to be "stuck," it might be due to scanning a virtual environment containing numerous files. In such cases, simply terminate the command and consider creating a configuration file to tailor the behavior.

## Configuration

Configuring doXtrings is done through a configuration file. The package will search for configuration in the following order: `pyproject.toml`, `doxtrings.toml`, `.doxtrings.toml`, `doxtrings.json`, `.doxtrings.json`. You can place the configuration file anywhere in your system and then reference it using the `-c` (or `--config-file`) argument when calling the doxtrings command:

```sh
doxtrings -c /path/to/config.toml
```

In `pyproject.toml`, the doXtrings configuration is located within the `[tool.doxtrings]` section.

### Example Configurations
#### doXtrings Configuration Settings

The doXtrings package employs its own capabilities to keep documentation up-to-date within its codebase. Below is the configuration utilized within the project:

```toml
[tool.doxtrings]
path = "./src/doxtrings"

[tool.doxtrings.ignore_rules.default]
ignore_prefixes_rules = ["_"]
include_prefixes_rules = ["__init__"]

[tool.doxtrings.ignore_rules.variables]
ignore_matches = ["logger"]
```

Alternatively, if not defined in `pyproject.toml`:

```toml
path = "./src/doxtrings"

[ignore_rules.default]
ignore_prefixes_rules = ["_"]
include_prefixes_rules = ["__init__"]

[ignore_rules.variables]
ignore_matches = ["logger"]
```

Let's delve into the available options:

1. `path`: This option designates the root directory where doXtrings will search for files to parse.
2. `ignore_rules`: This section configures rules for nodes that should be ignored during the parsing process.
3. `ignore_rules.default`: Within this subsection, you can define rules that are common to all types of nodes in the codebase. The possible node types are: modules, classes, methods, functions, constants, attributes, and variables.
4. `ignore_rules.default.ignore_prefixes_rules`: This rule instructs doXtrings to disregard any node beginning with `_`, effectively excluding private nodes from documentation.
5. `ignore_rules.default.include_prefixes_rules`: In contrast to the previous rule, this directive overrides the former by including nodes that start with `__init__`. This is especially important for modules and methods named `__init__`, ensuring their documentation is not overlooked.
6. `ignore_rules.variables`: This section enables the specification of ignore rules that exclusively apply to variables within the codebase.
7. `ignore_rules.variables.ignore_matches`: Specifically, this rule will ignore the documentation of all variables named `logger`. It is a common practice to create a new logger in each file, and its usually not desired to document all of them.

 !!! Note
    An important feature to highlight is that, even if a node is ignored, it might still raise errors if it was incorrectly documented. Set `fail_ignored_if_incorrect` to `False` if you wish to completely ignore nodes.

#### Lenient Example

The previous configuration might feel a bit strict for many users. It asks you to document every module, class attribute, constant, and function. You also need to include type hints in the docstrings if you've used type hints in your function signature.

A more relaxed approach is to document just classes, methods, and functions. Let's explore a sample configuration used in the deepFlow project:

```toml
path = "./src/deepflow"
types_to_check = ["class", "function", "method"]

[ignore_rules.default]
ignore_prefixes_rules = ["_"]  # Ignores private nodes
ignore_typing = true
ignore_args_and_kwargs = true

[ignore_rules.modules]
ignore_prefixes_rules = []
```

Here's what's different in this configuration:

1. `types_to_check`: With this set, doxtrings examines only the nodes belonging to these specified types: classes, functions, and methods.
2. `ignore_rules.default.ignore_typing`: You don't need to include type hints in the docstrings, though incorrect types will still cause failures.
3. `ignore_rules.default.ignore_args_and_kwargs`: Documenting `*args` and `**kwargs` parameters in methods and functions isn't required.
4. `ignore_rules.modules.ignore_prefixes_rules`: deepFlow follows a convention of writing most of the code in private modules and then reimporting the desired objects in the `__init__` module. Even though we are not checking the modules for the docstrings, we would still be ignoring the ones that start with `_` as it is a default ignore rule. Then, most of the code would simply be ignored (elements inside an ignored node are also ignored). Setting no ignore rules for modules means that no module will be marked as ignored.
#### Flexible Documentation Checking

Sometimes, strict documentation enforcement might not be necessary, but you still want to ensure that the documented nodes are accurate. For example, imagine you've documented a function and later updated its signature. In this case, you'd want doXtrings to alert you about incorrect docstrings but not pester you when docstrings are absent. Achieve this with:

```toml
path = "./src/"
types_to_check = ["function", "method"]

[ignore_rules.default]
ignore_prefixes_rules = [""]  # Ignores everything
```

The key point in this approach is setting an empty string in the `ignore_prefixes_rules`. In Python, all strings start with an empty string, so this will ignore all the nodes. Even ignoring everything, doXtrings will still check functions and methods and report an error if the docstring does not match the signature.
### Reference

For all the possible fields in the configuration object, check the documentation reference (`doxtrings.config.DoXtringsConfig`) at the [reference pages](reference/doxtrings/config.md).
