"""Builds notebooks/quickstart_colab.ipynb and notebooks/quickstart_jupyter.ipynb from one list of cells (the content is identical except for the
badge and the cell that reads the key). Run: python tools/build_notebooks.py   (outputs are always empty)."""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = "tleitch/aqEthnicity-examples"

def md(t): return {"cell_type": "markdown", "metadata": {}, "source": t.strip("\n").splitlines(True)}
def code(t): return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": t.strip("\n").splitlines(True)}

INTRO = """# aequum API quickstart: BISG, BIFSG and STRATA on made-up data
{badge}
This notebook calls the hosted REST API at `https://api.aequum.ai` with plain `requests`. **Every person in it is invented** (random first and last names) and every address is a **public landmark or business address**, so it shows *how to call the API*, not how accurate it is: invented names have no true race, so **no performance number is computed here**.

What you will do: check the service, send a small file to **BISG**, **BIFSG** and **aequum STRATA**, look at the *lookup level* and *uncertainty index* STRATA returns, and add the probabilities up for a group (an aggregate).

Outputs are **estimated probabilities, not a statement about any individual's race**. Use them for aggregate, population-level analysis only. STRATA is free up to 10,000 records a day with a registered key (see the README for how to get one)."""

KEY_COLAB = """# The API key comes from Colab Secrets, never from a cell.
# Left sidebar -> key icon -> "Add new secret" named AEQUUM_API_KEY -> paste your key -> switch "Notebook access" on.
from google.colab import userdata
try:
    KEY = userdata.get("AEQUUM_API_KEY")
except userdata.SecretNotFoundError:
    raise Stop("there is no Colab secret named AEQUUM_API_KEY. Click the key icon in the left sidebar, "
               "choose 'Add new secret', name it AEQUUM_API_KEY (exactly), paste your key as the value, "
               "switch 'Notebook access' on, then choose Runtime > Run all. " + KEY_HELP)
except userdata.NotebookAccessError:
    raise Stop("the secret AEQUUM_API_KEY exists but this notebook can't read it. Click the key icon in the "
               "left sidebar and switch 'Notebook access' on for AEQUUM_API_KEY, then choose Runtime > Run all.")
KEY = (KEY or "").strip()
if not KEY:
    raise Stop("the secret AEQUUM_API_KEY is empty. Paste your key as its value, then choose Runtime > Run all. " + KEY_HELP)
print("API key loaded from Colab Secrets (not shown)")"""

KEY_JUPYTER = """# The API key comes from an environment variable, never from a cell.
# Set it in the shell that starts Jupyter, e.g.  export AEQUUM_API_KEY=...   (see the README)
KEY = (os.environ.get("AEQUUM_API_KEY") or "").strip()
if not KEY:
    raise Stop("the AEQUUM_API_KEY environment variable isn't set. Quit Jupyter, run  export AEQUUM_API_KEY=your-key  "
               "in the same terminal, start Jupyter again from that terminal, and re-run. " + KEY_HELP)
print("API key loaded from the environment (not shown)")"""

SETUP = """import os, time, random
import requests
import pandas as pd

BASE = os.environ.get("AEQUUM_BASE_URL", "https://api.aequum.ai")
KEY_HELP = "No key yet? Email terry@aequum.ai for a free one (see the README)."

class Stop(Exception):
    \"\"\"Stops the notebook with a short, plain message instead of a long traceback.\"\"\"
    def _render_traceback_(self):
        return ["", "STOPPED: " + str(self), ""]"""

HELPER = """HEADERS = {"Authorization": f"Bearer {KEY}"}          # the key is only ever used here; it is never printed

def post(path, records, options=None, retries=8):
    \"\"\"POST columnar records to the API and return the parsed JSON.
    Right after a service restart the address routes can answer HTTP 503 for a few minutes while the geography tables load; we wait and retry.\"\"\"
    for _ in range(retries):
        r = requests.post(BASE + path, headers=HEADERS, json={"records": records, "options": options or {}}, timeout=300)
        if r.status_code != 503:
            break
        time.sleep(30)
    if r.status_code == 401:
        raise Stop("the API didn't accept your key (HTTP 401). Check it was pasted in full, with no extra spaces. " + KEY_HELP)
    if r.status_code == 429:
        raise Stop("you've reached today's free limit (HTTP 429). It resets tomorrow; email terry@aequum.ai if you need more.")
    if r.status_code == 422:
        raise Stop(f"the API couldn't read the input (HTTP 422): {r.text[:300]}")
    if not r.ok:
        raise Stop(f"{path} answered HTTP {r.status_code}: {r.text[:300]}")
    return r.json()

# 1. Is the service up? (no key needed)
print(requests.get(BASE + "/v1/health", timeout=30).json())"""

DATA_MD = """## 1. A made-up file: 300 invented people at public landmark and business addresses
Names are random combinations from short lists; the addresses are well-known public places (stadiums, towers, a hotel, a museum). No real person is represented."""

DATA = """random.seed(2026)
first = ["MARIA", "WEI", "JAMES", "AISHA", "CARLOS", "PRIYA", "DAVID", "LATOYA", "MIGUEL", "SARAH", "ANDRE", "MEI", "JOHN", "FATIMA", "LUIS", "KEISHA", "ANH", "TOMAS", "NIA", "HIRO",
         "EMILY", "MICHAEL", "JESSICA", "ROBERT", "ASHLEY", "WILLIAM", "AMANDA", "THOMAS", "KAREN", "STEVEN"]
last = ["GARCIA", "CHEN", "SMITH", "OKAFOR", "RODRIGUEZ", "PATEL", "JOHNSON", "WASHINGTON", "MARTINEZ", "NGUYEN", "BROWN", "KIM", "WILLIAMS", "HERNANDEZ", "LEE", "JACKSON", "LOPEZ", "SINGH", "DAVIS", "TRAN",
        "MILLER", "ANDERSON", "TAYLOR", "MOORE", "CLARK", "WALKER", "WRIGHT", "SCOTT", "BAKER", "NELSON"]
places = [  # (street, city, state, zip5): public landmarks and businesses
    ("233 S Wacker Dr", "Chicago", "IL", "60606"),            # Willis Tower
    ("20 W 34th St", "New York", "NY", "10001"),              # Empire State Building
    ("400 Broad St", "Seattle", "WA", "98109"),               # Space Needle
    ("300 Alamo Plaza", "San Antonio", "TX", "78205"),        # The Alamo
    ("600 Biscayne Blvd", "Miami", "FL", "33132"),            # Freedom Tower
    ("225 Baker St NW", "Atlanta", "GA", "30313"),            # Georgia Aquarium
    ("4 S Market St", "Boston", "MA", "02109"),               # Faneuil Hall
    ("401 E Jefferson St", "Phoenix", "AZ", "85004"),         # Chase Field
    ("409 Blackwell St", "Durham", "NC", "27701"),            # Durham Bulls Athletic Park
    ("2000 Brush St", "Detroit", "MI", "48226"),              # Ford Field
    ("1 Infinite Loop", "Cupertino", "CA", "95014"),          # a corporate campus
    ("1600 Pennsylvania Ave NW", "Washington", "DC", "20500"),
]
rows = []
for i in range(300):
    street, city, state, zip5 = random.choice(places)
    rows.append({"customer_id": f"S{i:04d}", "first_name": random.choice(first), "last_name": random.choice(last),
                 "address": street, "city": city, "state": state, "zip5": zip5})
df = pd.DataFrame(rows)
df.head()"""

GEO_MD = """## 2. Lookup level: how finely does each address resolve?
`/v1/geocode` tells you, for each address, the **lookup level** (`BG` block group, `TRACT`, `ZIP`, or `NONE`) and a confidence. The geography itself is not returned. STRATA uses the finest level an address resolves to."""

GEO = """places_df = pd.DataFrame(places, columns=["address", "city", "state", "zip5"])
geo = pd.DataFrame(post("/v1/geocode", {c: places_df[c].tolist() for c in places_df.columns})["columns"])
geo[["address", "city", "lookup_level", "lookup_conf"]]"""

STRATA_MD = """## 3. aequum STRATA: five-class probabilities, uncertainty index, lookup level
Use the column names **`first_name` / `last_name`**. `/v1/strata/auto` picks the finest geography each address resolves to. One call takes up to 10,000 rows; here we send 150 at a time and pass `customer_id` through so we can line the answers up with the input."""

STRATA = """parts = []
for start in range(0, len(df), 150):
    chunk = df.iloc[start:start + 150]
    out = post("/v1/strata/auto", {c: chunk[c].tolist() for c in df.columns}, {"passthrough": ["customer_id"]})
    parts.append(pd.DataFrame(out["columns"]))
res = pd.concat(parts, ignore_index=True)
assert res.customer_id.tolist() == df.customer_id.tolist()      # answers come back in input order
res[["customer_id", "p_white", "p_black", "p_hispanic", "p_asian", "p_other", "dominant_race", "iu", "lookup_level"]].head()"""

CHECK = """classes = ["white", "black", "hispanic", "asian", "other"]
p = ["p_" + c for c in classes]
print("probabilities sum to 1 on every row:", bool(((res[p].sum(axis=1) - 1).abs() < 1e-3).all()))
print("\\nlookup level used:\\n" + res.lookup_level.value_counts().to_string())
print("\\nmean uncertainty index (iu) by lookup level (higher = less certain):\\n" + res.groupby("lookup_level").iu.mean().round(3).to_string())"""

BISG_MD = """## 4. BISG and BIFSG (free, pyethnicity-compatible routes)
BISG uses surname and ZIP code; BIFSG adds first name. Rows whose surname or ZIP is not in the Census tables come back with empty (NaN) probabilities, and get no label here."""

BISG = """zc = df.zip5.tolist()
bisg = pd.DataFrame(post("/v1/predict/bisg", {"last_name": df.last_name.tolist(), "zcta": zc})["columns"])
bifsg = pd.DataFrame(post("/v1/predict/bifsg", {"first_name": df.first_name.tolist(), "last_name": df.last_name.tolist(), "zcta": zc})["columns"])
four = ["white", "black", "hispanic", "asian"]

def top(t):
    v = t[four]
    return v.fillna(-1).idxmax(axis=1).where(v.notna().any(axis=1))

res["bisg"], res["bifsg"] = top(bisg).values, top(bifsg).values
has = res.bisg.notna()
print("rows with a BISG answer:", int(has.sum()), "of", len(res))
print("STRATA's top class differs from BISG's on:", int((res.dominant_race[has] != res.bisg[has]).sum()), "of those rows")
print("BIFSG differs from BISG on:", int((res.bifsg[has] != res.bisg[has]).sum()), "of those rows")
bisg[four].head()"""

AGG_MD = """## 5. An aggregate example: describe a group with expected counts, not labels
The probabilities are meant to be **added up**. For a group of people, the *expected count* of a class is the sum of its probabilities; counting each person's single top class (`argmax`) throws information away and is biased towards the biggest class. Everything below is about **groups**, not individuals, and the data are invented, so the numbers only show the mechanics."""

AGG = """summary = pd.DataFrame({
    "expected_count": res[p].sum().round(1).values,
    "argmax_count": res.dominant_race.value_counts().reindex(classes).fillna(0).astype(int).values,
}, index=classes)
summary["expected_share"] = (summary.expected_count / len(res)).round(3)
print(summary)

res["city"] = df.city.values                       # the answers are in input order, so we can add the input city back
by_city = res.groupby("city")[p].mean().round(3)
by_city["n"] = res.groupby("city").size()
print("\\nmean probabilities by city (groups with at least 20 rows only):")
print(by_city[by_city.n >= 20])"""

END = """## 6. What to take from this
- The API returns **probabilities**. Add them up (expected counts) when you describe a group; do not read a single person's top class as their race.
- `iu`, the uncertainty index, is higher where the model is less sure, and `lookup_level` tells you how precise the address match was. Both belong in any analysis.
- No accuracy figure appears here on purpose: with invented names there is nothing to measure against. Published benchmarks for STRATA are **coming**; until then treat results as estimates.
- Not for decisions about individuals. STRATA outputs are subject to the free-tier terms (see `NOTICE`). Questions: terry@aequum.ai"""

def cells(kind):
    badge = (f"[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/{REPO}/blob/main/notebooks/quickstart_colab.ipynb)"
             if kind == "colab" else "*Same content as `quickstart_colab.ipynb`; this copy reads the key from an environment variable.*")
    key = KEY_COLAB if kind == "colab" else KEY_JUPYTER
    return [md(INTRO.format(badge=badge)), code(SETUP), code(key), code(HELPER), md(DATA_MD), code(DATA), md(GEO_MD), code(GEO),
            md(STRATA_MD), code(STRATA), code(CHECK), md(BISG_MD), code(BISG), md(AGG_MD), code(AGG), md(END)]

for kind in ("colab", "jupyter"):
    cl = cells(kind)
    for i, c in enumerate(cl): c["id"] = f"cell{i:02d}"
    nb = {"cells": cl, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}, "language_info": {"name": "python"}},
          "nbformat": 4, "nbformat_minor": 5}
    if kind == "colab": nb["metadata"]["colab"] = {"name": "quickstart_colab.ipynb", "provenance": []}
    p = os.path.join(ROOT, "notebooks", f"quickstart_{kind}.ipynb")
    json.dump(nb, open(p, "w"), indent=1, ensure_ascii=False); open(p, "a").write("\n"); print("wrote", p)
