# pysen-plugins

## Installation

```sh
pip install pysen-plugins
```

## Usage

Add `tool.pysen.plugin` section to your `pyproject.toml`.
```toml
[tool.pysen]
version = "0.10"

[tool.pysen.plugin.clang_format]
function = "pysen_plugins::clang_format"
```

Note: You need to install the underlying commands (e.g. `clang-format`) manually.

## plugins
- C++
  - [clang_format](https://clang.llvm.org/docs/ClangFormat.html) (lint, format)
- CMake
  - [cmake_format](https://github.com/cheshirekow/cmake_format) (lint, format)
- Go
  - [golint](https://github.com/golang/lint) (lint)
  - [goreturns](https://github.com/sqs/goreturns) (lint, format)
- HTML
  - [prettier](https://prettier.io) (lint, format)
  - [tidy](http://www.html-tidy.org) (lint, format)
- JavaScript
  - [prettier](https://prettier.io) (lint, format)
- JSON
  - [jq](https://stedolan.github.io/jq) (lint, format)
  - [prettier](https://prettier.io) (lint, format)
- Python
  - mypy_init_check (lint)
  - mypy_simple (lint)
  - [pylint](http://pylint.pycqa.org) (lint)
  - [ruff](https://github.com/charliermarsh/ruff) (lint, format)
  - customizable_builtins (lint, format)
    - black
    - isort
    - flake8
    - mypy
- Shell script
  - [shellcheck](https://github.com/koalaman/shellcheck) (lint)
  - [shfmt](https://github.com/mvdan/sh) (lint, format)
- TypeScript
  - [prettier](https://prettier.io) (lint, format)
- XML
  - [tidy](http://www.html-tidy.org) (lint, format)
- YAML
  - [prettier](https://prettier.io) (lint, format)
  - [ruamel_yaml](https://sourceforge.net/projects/ruamel-yaml) (lint, format)
