# aqethnicity-examples

Runnable examples for the **aequum REST API**: race and ethnicity *probabilities* for population-level analysis, from a surname, a first name and an address. Everything here uses **made-up people and public landmark or business addresses**; there is no real personal data in this repository.

| Notebook | Where |
|---|---|
| `notebooks/quickstart_colab.ipynb` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tleitch/aqethnicity-examples/blob/main/notebooks/quickstart_colab.ipynb) (reads your key from Colab Secrets) |
| `notebooks/quickstart_jupyter.ipynb` | the same content for a local Jupyter (reads your key from an environment variable) |

## What the API offers

- **BISG and BIFSG: free.** Bayesian Improved (First name) Surname Geocoding from public Census tables: surname (and first name) plus a ZIP code, tract or block group. The routes are `pyethnicity`-compatible (same function names and output columns).
- **aequum STRATA.** A name-plus-address model. It returns **five-class probabilities** (white, black, hispanic, asian, other), a per-record **uncertainty index** (`iu`) and the **lookup level** it used (`BG` block group, `TRACT`, `ZIP`, or `NONE` for name only). Free up to **10,000 records a day** with a registered key.
- **Aggregate, population-level use only.** The outputs are statistical estimates, **not statements about any individual's race**, and must not be used for decisions about individuals. Every proxy, STRATA included, is least reliable for smaller groups; use the uncertainty index and treat results as estimates. Benchmarks are coming.

## Get a key

Until self-service registration is live, **email terry@aequum.ai** and ask for a free key. Keep it out of your code: the notebooks read it from the environment variable `AEQUUM_API_KEY` (Jupyter) or from **Colab Secrets** (Colab) and never print it.

## Run the notebooks

**Colab:** click the badge, add a secret named `AEQUUM_API_KEY` (key icon in the left sidebar, then switch *Notebook access* on), and run all cells.

**Local Jupyter:**
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export AEQUUM_API_KEY=...           # your key; not printed anywhere
jupyter lab notebooks/quickstart_jupyter.ipynb
```
`AEQUUM_BASE_URL` overrides the default `https://api.aequum.ai` (for testing only).

## The API at a glance

Base URL `https://api.aequum.ai`. Authentication: an `Authorization` header with your key as a bearer token (`Authorization: Bearer <your key>`). Up to 10,000 records per call, JSON in and out, **columnar**: `{"records": {"column": [values...]}, "options": {...}}`; every column has the same length and results come back in input order.

| Route | What it does | Needs |
|---|---|---|
| `GET /v1/health` | liveness; `"ready": true` once the geography tables are loaded (no key needed) | |
| `POST /v1/predict/bisg` (also `bisg6`, `bifsg`, `bifsg6`, `predict_race`, `predict_race_fl`, `predict_race_flg`) | BISG / BIFSG | `last_name` plus one of `zcta`, `tract`, `block_group` (`first_name` for BIFSG) |
| `POST /v1/strata/auto` (or `bgt`, `tract`, `zcta`, `name`) | STRATA: probabilities, uncertainty index, lookup level; `auto` picks the finest geography each address resolves to | `first_name`, `last_name`, `address`, `city`, `state`, `zip5` |
| `POST /v1/geocode` | address to lookup level and confidence (the geography itself is not returned) | `address`, `city`, `state`, `zip5` |

Reading a STRATA answer: `columns` holds your passthrough columns (add `options.passthrough`), `p_white p_black p_hispanic p_asian p_other` (they sum to 1), `dominant_race`, `iu` (higher means less certain), `lookup_level` and `lookup_conf`.

Things to know:
- Use **`first_name` / `last_name`**. Other spellings are not rejected: you get a prediction made without the name.
- A forced tier (`bgt`, `tract`) refuses rows that do not resolve that finely (HTTP 422 with the row numbers); use `auto`.
- After a service restart the address routes can answer **503 for about five minutes** while the tables load; `GET /v1/health` shows `"ready": true` when they are.
- Errors are JSON, `{"error": {"code", "message"}}`: `missing_api_key` and `invalid_api_key` (401), `bad_request` (400), and 413 above 10,000 records.

## Privacy

**The hosted API does not store the names or addresses you send.** We keep a usage record: your key, the time, the route and the number of records. Do not send data you are not permitted to process.

## Repository checks

`scripts/scan_secrets.py` scans the working tree and the **full git history** for key-like strings and for notebook outputs; it runs in CI (`.github/workflows/checks.yml`) and as a pre-commit hook (`git config core.hooksPath .githooks`). The committed notebooks have **no outputs**.

## Licence and terms

The example code in this repository is under the [MIT licence](LICENSE). Use of the hosted API, and of STRATA outputs, is subject to the free-tier terms (see [NOTICE](NOTICE)). *aequumAI LLC. Contact: terry@aequum.ai*
