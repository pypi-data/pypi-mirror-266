# UserCfg-Opt-Parser

[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![GitHub license](https://img.shields.io/github/license/NathanVaughn/usercfg-opt-parser)](https://github.com/NathanVaughn/usercfg-opt-parser/blob/main/LICENSE)
[![PyPi versions](https://img.shields.io/pypi/pyversions/usercfg-opt-parser)](https://pypi.org/project/usercfg-opt-parser)
[![PyPi downloads](https://img.shields.io/pypi/dm/usercfg-opt-parser)](https://pypi.org/project/usercfg-opt-parser)

---

This is a parser for Microsoft Flight Simulator UserCfg.opt files. While the format
has some similarities with JSON, I didn't recognize it, nor any AI tools I asked.

Example:

```VB
Version 66
{Graphics
	Version 1.1.0
	Preset Custom
	{Texture
		MaxAnisotropy 8
		Quality 1
	}
	{SuperSampling
		SuperSampling 2
	}
}
```

This package allows you to read and write files in this format. While I have not
done extensive testing to see what exactly Microsoft Flight Simulator will and will
not accept, the parser tends to be forgiving
(CRLF or LF are both accepted, spaces instead of tabs, etc.), the writer
matches the format of the file on my computer exactly.

I have found no documentation on the format, so this package is no more than educated
guesses. Any undefined behaviors will raise an exception.

## Usage

```bash
pip install usercfg-opt-parser
```

A `json`-like API is provided. File objects must be in binary mode to be able
to handle line endings.

```python
import os

import usercfgopt

with open(
    os.path.join(os.environ["APPDATA"], "Microsoft Flight Simulator", "UserCfg.opt"),
    "rb",
) as fp:
    data = usercfgopt.load(fp)

data["Video"]["VSync"] = 1

with open("NewUserCfg.opt", "wb") as fp:
    usercfgopt.dump(data, fp)
```

## FAQs

### Why are booleans not allowed?

Because it was unclear if "ON" was truly a boolean, and other 1s and 0s could be
integers with more than 2 values.

### Why is it so slow?

It's Python and it's a parser written for a single obscure file type. Just getting this
working exhausted my motivation.

### Should I use this file format?

Please god no. Unless you feel that YAML doesn't have enough ambiguity for your tastes,
then I guess sure, go for it.

## Development

```bash
python -m pip install pipx --upgrade
pipx ensurepath
pipx install poetry
pipx install vscode-task-runner
# (Optionally) Add pre-commit plugin
poetry self add poetry-pre-commit-plugin
```
