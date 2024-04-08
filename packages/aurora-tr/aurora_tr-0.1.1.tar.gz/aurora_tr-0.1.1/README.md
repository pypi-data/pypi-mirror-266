# aurora-tr
[![pytest](https://github.com/ffreemt/aurora-tr/actions/workflows/routine-tests.yml/badge.svg)](https://github.com/ffreemt/aurora-tr/actions)[![python](https://img.shields.io/static/v1?label=python+&message=3.8%2B&color=blue)](https://www.python.org/downloads/)[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)[![PyPI version](https://badge.fury.io/py/aurora-tr.svg)](https://badge.fury.io/py/aurora-tr)

Translate via aurora and variants, openai, azure openai, etc.

# Quick Setup
From command line
```bash
pip install aurora-tr
docker run -d --name aurora -p 8080:8080 ghcr.io/aurora-develop/aurora:latest
```
python code
```python
from aurora_tr import aurora_tr

res = aurora_tr("test me", url="http:/127.0.0.1:8080/v1")
print(res)
# output:  {'translation': '测试我', 'notes': ''}
```

# Detailed Instructions

## Install
```
pip install aurora-tr
```


## Use

### url for `aurora` REST API

First off, acquire a url (`OPENAI_BASE_URL` in `python-openai`) for the `aurora` REST API for `aurora-tr` to use, for example, search the net, beg your friends, or deploy your own `aurora`, etc.

N.B.: `aurora` is a service in the wild similar or compatible to openai (more commonly known as chatgpt).

To deplay your own `aurora` locolly or on a remote machine, refer to
[https://github.com/aurora-develop/aurora](https://github.com/aurora-develop/aurora)

For example (the easieast way if you can access docker):
```bash
docker run -d --name aurora -p 8080:8080 ghcr.io/aurora-develop/aurora:latest
```

The `OPENAI_BASE_URL` in this case will be `http://localhost:8080/v1` or `http://external_ip_or_domainname:8080/v1`

### python code
Default `base_url`, `api_key` and `model` of
`aurora_tr` take the value of `OPENAI_BASE_URL`, `OPENAI_API_KEY` and
`OPENAI_MODEL` from the file `.env-aurora`.

`base_url`, `api_key` and `model` can also be set directly in `aurora_tr`, e.g.,
```python
res = aurora_tr(
  '....',
  url_base="https://uu.ci/v1",
  api_key=...,
  model-"gpt-4-turbo-preview",
  selector="uuci"
)
```
Hence, if you have deployed your own `aurora` API:
```
from aurora_tr import aurora_tr

res = aurora_tr("test me", url="http:/127.0.0.1:8080/v1")
print(res)
# output:  {'translation': '测试我', 'notes': ''}

```

Other examples:
```python
from aurora_tr import aurora_tr

# default aurora, source language: English, target language: Chinese
res = aurora_tr("Test me.")
print(res)
```
```json
{'translation': '测试我。', 'notes': 'Translated from English to Chinese.'}
```
```python
# target language: English
res = aurora_tr("试试我", to_lang="English")
```
```json
{'translation': 'Try me', 'notes': ''}
```

```python
# select aurora
res = aurora_tr("Testen mich bitte")
```
```json
 {'translation': '请测试我', 'notes': 'Translated from English to Chinese'}
```

```python
# select uuci
import dotenv

api_key = dotenv.dotenv_values(".env").get("OPENAI_API_KEY_UUCI")
# or api_key = "......"
res = aurora_tr("Test me.", selector="uuci", api_key=api_key)
```
```json
{'translation': '测试我。'}
```

## Brief docs
```bash
aurora_tr(
    text: str,
    from_lang: Optional[str] = 'English',
    to_lang: str = 'Chinese',
    selector: str = 'aurora',
    base_url: str = '',
    api_key: str = '',
    model: str = '',
    temperature: Optional[float] = None,
)
Docstring:
Translate viaa auroa and uu.ci.

Args
----
text: string to transalte
from_lang: source language
to_lang: target language
selector: prodiver selector
base_url:
api_key: token
model: model name, anything for aurora
temperature (str): 0.2-0.4 for translation, might just left out

Returns
-------
dict/json: {"translation": "...", notes: "..."}
```