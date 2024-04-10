# Using doXtrings

Running doXtrings is straightforward. Just execute the following command in your terminal:

```sh
doxtrings
```

If any docstrings are missing or incorrect, the command will display them. Here are some examples:

#### Missing Docstring
```
Docstring error discovered at src/doxtrings/config.py:145 for attribute path
    Location: Reason for missing docstring
```

This indicates the absence of a docstring for an attribute called `path`. The specific location is identified as `src/doxtrings/config.py:145`. Most integrated development environments (IDEs) allow you to click on the location to jump to the relevant file.

#### Incorrect Return Type

```
Docstring error found at src/doxtrings/config.py:279 for function load_config
    At .return_type: Reason for conflicting values; Expected DoXtringsConfig but docstring states obj
```

In this case, the function `load_config` was expected to have a return type of `DoXtringsConfig`, but the docstring specifies it as `obj`.

#### Missing Argument

```
Docstring error located at src/doxtrings/core/report.py:31 for method add_documentable_diff
    At .arguments[0]: Reason for missing expected FunctionArgument(name='documentable', type_hint='Documentable') in docstring, but it's absent
```

This error signifies that the first argument of the `add_documentable_diff` method lacks documentation in its docstring.

By following these examples, you can identify and rectify missing or inaccurate docstrings in your code using doXtrings.
