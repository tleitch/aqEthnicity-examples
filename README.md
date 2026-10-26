# aqEthnicity examples

Runnable examples for **aqEthnicity**, in **Python** and **R**: race and ethnicity *probabilities* for population-level analysis, from a surname, a first name and an address. Everything here uses **made-up people and public landmark or business addresses**; there is no real personal data in this repository.

## Install

| | Install |
|---|---|
| **Python** | `pip install "aqethnicity[local,pandas]"` (PyPI) |
| **R** | `remotes::install_github("tleitch/aqEthnicity", subdir = "r")` (GitHub) |

The packages know where the hosted service is: **you never type a URL**. (`AEQUUM_BASE_URL` overrides it, for testing only.)

## The notebooks

| Notebook | Where |
|---|---|
| `notebooks/quickstart_colab.ipynb` (Python) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tleitch/aqEthnicity-examples/blob/main/notebooks/quickstart_colab.ipynb) (key from Colab Secrets) |
| `notebooks/quickstart_jupyter.ipynb` (Python) | the same content for a local Jupyter (key from an environment variable) |
| `notebooks/quickstart_R_colab.ipynb` (R) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tleitch/aqEthnicity-examples/blob/main/notebooks/quickstart_R_colab.ipynb) (choose an **R runtime**; key from a hidden prompt, because Colab Secrets are Python-only) |
| `R/quickstart.qmd` (R) | a Quarto document: `quarto render R/quickstart.qmd` (key from `AEQUUM_API_KEY` or a hidden prompt) |

## What you get

- **STRATA** (hosted): five-class probabilities (white, black, hispanic, asian, other), a per-record **uncertainty index** (`iu`) and the **lookup level** it used, from a name and an address. Python `aq.strata(...)`; R `strata(...)` and the wru-style `predict_race_aq(df, ...)`, which returns your data frame with `pred.whi`, `pred.bla`, `pred.his`, `pred.asi`, `pred.oth` added.
- **BISG and BIFSG**: Python runs them **on your machine** (the `local` extra, pyethnicity's tables; no key, nothing leaves your computer); in this first R release they are hosted.
- **geocode**: for each address, the lookup level and a confidence (the geography itself is not returned).
- **Aggregate, population-level use only.** The outputs are statistical estimates, **not statements about any individual's race**, and must not be used for decisions about individuals.

Plain messages instead of long errors: a missing key, 401 (key not accepted), 429 (today's free limit), 422 (input it can't read, with your row numbers), and 503 (the service is starting up after a restart: the package waits and retries). A misspelt field such as `mname=` is refused before anything is sent (the middle name is `middle_name`).

## Get a key

Until self-service registration is live, **email terry@aequum.ai** and ask for a free key. Keep it out of your code: set it with `aq.set_api_key()` / `aq_set_key()` (R asks with a hidden prompt) or the environment variable `AEQUUM_API_KEY`. It is never printed or logged.

**Colab (Python):** click the badge, add a secret named `AEQUUM_API_KEY` (key icon in the left sidebar, then switch *Notebook access* on), and run all cells. **Colab (R):** choose an R runtime, run all cells, and paste the key into the hidden prompt.

**Local Jupyter:**
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export AEQUUM_API_KEY=...           # your key; not printed anywhere
jupyter lab notebooks/quickstart_jupyter.ipynb
```

## Privacy

**The hosted API does not store the names or addresses you send.** We keep a usage record: your key, the time, the route and the number of records. Do not send data you are not permitted to process.

## Repository checks

`scripts/scan_secrets.py` scans the working tree and the **full git history** for key-like strings and for notebook outputs; it runs in CI (`.github/workflows/checks.yml`) and as a pre-commit hook (`git config core.hooksPath .githooks`). The committed notebooks have **no outputs**.

## Licence and terms

The example code in this repository is under the [Apache License 2.0](LICENSE). Use of the hosted API, and of STRATA outputs, is subject to the free-tier terms (see [NOTICE](NOTICE)). *aequumAI LLC. Contact: terry@aequum.ai*
