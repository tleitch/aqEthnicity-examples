"""Builds the aqEthnicity quickstarts from one source: Python (Colab + Jupyter, `import aqethnicity as aq`), R (Colab R runtime) and R/quickstart.qmd (Quarto).
No URLs and no raw HTTP in any user cell: the packages know where the service is. Outputs are always empty.
Run: python tools/build_notebooks.py"""
import json, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = "tleitch/aqEthnicity-examples"

def md(t): return {"cell_type": "markdown", "metadata": {}, "source": t.strip("\n").splitlines(True)}
def code(t): return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": t.strip("\n").splitlines(True)}

# ------------------------------------------------------------------ Python
PY_INTRO = "# aqEthnicity quickstart (Python): BISG, BIFSG and STRATA on made-up data\n{badge}\nThis notebook uses the **aqEthnicity** Python package (`import aqethnicity as aq`). The package knows where the hosted service is; you never type a URL. **Every person in it is invented** (random first and last names) and every address is a **public landmark or business address**, so it shows *how to call the API*, not how accurate it is: invented names have no true race, so **no performance number is computed here**.\n\nWhat you will do: check the service, send a small file to **BISG**, **BIFSG** and **aequum STRATA**, look at the *lookup level* and *uncertainty index* STRATA returns, and add the probabilities up for a group (an aggregate).\n\nOutputs are **estimated probabilities, not a statement about any individual's race**. Use them for aggregate, population-level analysis only. STRATA is free up to 10,000 records a day with a registered key (see the README for how to get one)."
PY_DATA_MD = '## 1. A made-up file: 300 invented people at public landmark and business addresses\nNames are random combinations from short lists; the addresses are well-known public places (stadiums, towers, a hotel, a museum). No real person is represented.'
PY_DATA = 'random.seed(2026)\nfirst = ["MARIA", "WEI", "JAMES", "AISHA", "CARLOS", "PRIYA", "DAVID", "LATOYA", "MIGUEL", "SARAH", "ANDRE", "MEI", "JOHN", "FATIMA", "LUIS", "KEISHA", "ANH", "TOMAS", "NIA", "HIRO",\n         "EMILY", "MICHAEL", "JESSICA", "ROBERT", "ASHLEY", "WILLIAM", "AMANDA", "THOMAS", "KAREN", "STEVEN"]\nlast = ["GARCIA", "CHEN", "SMITH", "OKAFOR", "RODRIGUEZ", "PATEL", "JOHNSON", "WASHINGTON", "MARTINEZ", "NGUYEN", "BROWN", "KIM", "WILLIAMS", "HERNANDEZ", "LEE", "JACKSON", "LOPEZ", "SINGH", "DAVIS", "TRAN",\n        "MILLER", "ANDERSON", "TAYLOR", "MOORE", "CLARK", "WALKER", "WRIGHT", "SCOTT", "BAKER", "NELSON"]\nplaces = [  # (street, city, state, zip5): public landmarks and businesses\n    ("233 S Wacker Dr", "Chicago", "IL", "60606"),            # Willis Tower\n    ("20 W 34th St", "New York", "NY", "10001"),              # Empire State Building\n    ("400 Broad St", "Seattle", "WA", "98109"),               # Space Needle\n    ("300 Alamo Plaza", "San Antonio", "TX", "78205"),        # The Alamo\n    ("600 Biscayne Blvd", "Miami", "FL", "33132"),            # Freedom Tower\n    ("225 Baker St NW", "Atlanta", "GA", "30313"),            # Georgia Aquarium\n    ("4 S Market St", "Boston", "MA", "02109"),               # Faneuil Hall\n    ("401 E Jefferson St", "Phoenix", "AZ", "85004"),         # Chase Field\n    ("409 Blackwell St", "Durham", "NC", "27701"),            # Durham Bulls Athletic Park\n    ("2000 Brush St", "Detroit", "MI", "48226"),              # Ford Field\n    ("1 Infinite Loop", "Cupertino", "CA", "95014"),          # a corporate campus\n    ("1600 Pennsylvania Ave NW", "Washington", "DC", "20500"),\n]\nrows = []\nfor i in range(300):\n    street, city, state, zip5 = random.choice(places)\n    rows.append({"customer_id": f"S{i:04d}", "first_name": random.choice(first), "last_name": random.choice(last),\n                 "address": street, "city": city, "state": state, "zip5": zip5})\ndf = pd.DataFrame(rows)\ndf.head()'
PY_AGG_MD = "## 5. An aggregate example: describe a group with expected counts, not labels\nThe probabilities are meant to be **added up**. For a group of people, the *expected count* of a class is the sum of its probabilities; counting each person's single top class (`argmax`) throws information away and is biased towards the biggest class. Everything below is about **groups**, not individuals, and the data are invented, so the numbers only show the mechanics."
PY_AGG = 'summary = pd.DataFrame({\n    "expected_count": res[p].sum().round(1).values,\n    "argmax_count": res.dominant_race.value_counts().reindex(classes).fillna(0).astype(int).values,\n}, index=classes)\nsummary["expected_share"] = (summary.expected_count / len(res)).round(3)\nprint(summary)\n\nres["city"] = df.city.values                       # the answers are in input order, so we can add the input city back\nby_city = res.groupby("city")[p].mean().round(3)\nby_city["n"] = res.groupby("city").size()\nprint("\\nmean probabilities by city (groups with at least 20 rows only):")\nprint(by_city[by_city.n >= 20])'
PY_END = "## 6. What to take from this\n- The API returns **probabilities**. Add them up (expected counts) when you describe a group; do not read a single person's top class as their race.\n- `iu`, the uncertainty index, is higher where the model is less sure, and `lookup_level` tells you how precise the address match was. Both belong in any analysis.\n- No accuracy figure appears here on purpose: with invented names there is nothing to measure against. Published benchmarks for STRATA are **coming**; until then treat results as estimates.\n- Not for decisions about individuals. STRATA outputs are subject to the free-tier terms (see `NOTICE`). Questions: terry@aequum.ai"

PY_INSTALL = """# PRE-RELEASE: aqEthnicity is not on PyPI yet, so this installs the test build from TestPyPI.
# After the PyPI release this cell becomes just:   %pip install -q "aqethnicity[local,pandas]"
%pip install -q --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ "aqethnicity[local,pandas]==0.1.0.dev1\""""

PY_SETUP = """import random
import pandas as pd
import aqethnicity as aq"""

PY_KEY_COLAB = """# The API key comes from Colab Secrets, never from a cell.
# Left sidebar -> key icon -> "Add new secret" named AEQUUM_API_KEY -> paste your key -> switch "Notebook access" on.
from google.colab import userdata
try:
    aq.set_api_key(userdata.get("AEQUUM_API_KEY"))          # the key is never printed or logged
except userdata.SecretNotFoundError:
    raise SystemExit("There is no Colab secret named AEQUUM_API_KEY. Click the key icon in the left sidebar, choose 'Add new secret', "
                     "name it AEQUUM_API_KEY (exactly), paste your key as the value, switch 'Notebook access' on, then Runtime > Run all.")
except userdata.NotebookAccessError:
    raise SystemExit("The secret AEQUUM_API_KEY exists but this notebook can't read it. Switch 'Notebook access' on for it (key icon), then Runtime > Run all.")
print("API key set from Colab Secrets (not shown)")"""

PY_KEY_JUPYTER = """# The API key comes from the AEQUUM_API_KEY environment variable, never from a cell. Set it in the shell that starts Jupyter:
#     export AEQUUM_API_KEY=your-key
# aqethnicity reads it by itself; if it is missing, the first hosted call stops with a plain message saying what to do.
print("aqethnicity", aq.__version__)"""

PY_HEALTH = """print(aq.health())      # the service is up when "ok" is true; the address routes are ready when "ready" is true (no key needed)"""

PY_GEO_MD = """## 2. Lookup level: how finely does each address resolve?
`aq.geocode()` tells you, for each address, the **lookup level** (`BG` block group, `TRACT`, `ZIP`, or `NONE`) and a confidence. The geography itself is not returned. STRATA uses the finest level an address resolves to."""
PY_GEO = """places_df = pd.DataFrame(places, columns=["address", "city", "state", "zip5"])
geo = aq.geocode(places_df.address, places_df.city, places_df.state, places_df.zip5, output="pandas")
geo[["lookup_level", "lookup_conf"]].assign(address=places_df.address.values, city=places_df.city.values)"""

PY_STRATA_MD = """## 3. aqEthnicity STRATA: five-class probabilities, uncertainty index, lookup level
`aq.strata()` picks the finest geography each address resolves to. The package splits large inputs into requests for you and returns the answers **in your row order**; `passthrough` echoes `customer_id` back so you can check the alignment. A misspelt field such as `mname=` is refused with a plain message (the middle name is `middle_name`)."""
PY_STRATA = """res = aq.strata(df.first_name, df.last_name, address=df.address, city=df.city, state=df.state, zip5=df.zip5,
                passthrough={"customer_id": df.customer_id}, output="pandas")
assert res.customer_id.tolist() == df.customer_id.tolist()      # answers come back in input order
res[["customer_id", "p_white", "p_black", "p_hispanic", "p_asian", "p_other", "dominant_race", "iu", "lookup_level"]].head()"""

PY_CHECK = """classes = ["white", "black", "hispanic", "asian", "other"]
p = ["p_" + c for c in classes]
print("probabilities sum to 1 on every row:", bool(((res[p].sum(axis=1) - 1).abs() < 1e-3).all()))
print("\\nlookup level used:\\n" + res.lookup_level.value_counts().to_string())
print("\\nmean uncertainty index (iu) by lookup level (higher = less certain):\\n" + res.groupby("lookup_level").iu.mean().round(3).to_string())"""

PY_BISG_MD = """## 4. BISG and BIFSG (free; they run on your machine)
BISG uses surname and ZIP code; BIFSG adds first name. They come from the `local` extra (the open-source pyethnicity tables), need no key and send nothing anywhere. Rows whose surname or ZIP is not in the Census tables come back with empty (NaN) probabilities, and get no label here."""
PY_BISG = """bisg = aq.bisg(df.last_name, zcta=df.zip5, output="pandas")
bifsg = aq.bifsg(df.first_name, df.last_name, zcta=df.zip5, output="pandas")
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

def py_cells(kind):
    badge = (f"[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/{REPO}/blob/main/notebooks/quickstart_colab.ipynb)"
             if kind == "colab" else "*Same content as `quickstart_colab.ipynb`; this copy reads the key from an environment variable.*")
    key = PY_KEY_COLAB if kind == "colab" else PY_KEY_JUPYTER
    return [md(PY_INTRO.format(badge=badge)), code(PY_INSTALL), code(PY_SETUP), code(key), code(PY_HEALTH), md(PY_DATA_MD), code(PY_DATA),
            md(PY_GEO_MD), code(PY_GEO), md(PY_STRATA_MD), code(PY_STRATA), code(PY_CHECK), md(PY_BISG_MD), code(PY_BISG), md(PY_AGG_MD), code(PY_AGG), md(PY_END)]

# ------------------------------------------------------------------ R
R_INTRO = """# aqEthnicity quickstart (R): STRATA, BISG and BIFSG on made-up data
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/%s/blob/main/notebooks/quickstart_R_colab.ipynb)

**Use a Colab R runtime** (Runtime > Change runtime type > R). This notebook uses the **aqEthnicity** R package (`library(aqEthnicity)`); the package knows where the hosted service is, so you never type a URL. **Every person in it is invented** and every address is a **public landmark or business address**, so it shows *how to call the service*, not how accurate it is: **no performance number is computed here**.

Outputs are **estimated probabilities, not a statement about any individual's race**; use them for aggregate, population-level analysis only. In this first R release every call is hosted and needs a key (see the README).""" % REPO

R_INSTALL = """# PRE-RELEASE: aqEthnicity is not on CRAN yet. This installs the development version from GitHub
# (the repository is created when the package is released; until then this cell cannot succeed).
install.packages(c("remotes", "askpass"), quiet = TRUE)
remotes::install_github("tleitch/aqEthnicity", quiet = TRUE)"""

R_SETUP = """library(aqEthnicity)"""

R_KEY = """# Colab Secrets work from Python only, so in R the key comes from a hidden prompt (or from AEQUUM_API_KEY if it is set).
# It is never printed or logged, and it is never typed into a cell.
if (!nzchar(Sys.getenv("AEQUUM_API_KEY"))) {
  key <- askpass::askpass("Paste your aqEthnicity API key (input is hidden), then press Enter: ")
  if (is.null(key) || !nzchar(key)) stop("No key entered. No key yet? Email terry@aequum.ai for a free one (see the README).")
  aq_set_key(key); rm(key)
}
cat("API key set (not shown)\\n")"""

R_HEALTH = """str(aq_health())      # "ok" is TRUE when the service is up; "ready" is TRUE when the address routes are loaded (no key needed)"""

R_DATA = """set.seed(2026)
first <- c("MARIA", "WEI", "JAMES", "AISHA", "CARLOS", "PRIYA", "DAVID", "LATOYA", "MIGUEL", "SARAH", "ANDRE", "MEI", "JOHN", "FATIMA", "LUIS", "KEISHA", "ANH", "TOMAS", "NIA", "HIRO",
           "EMILY", "MICHAEL", "JESSICA", "ROBERT", "ASHLEY", "WILLIAM", "AMANDA", "THOMAS", "KAREN", "STEVEN")
last <- c("GARCIA", "CHEN", "SMITH", "OKAFOR", "RODRIGUEZ", "PATEL", "JOHNSON", "WASHINGTON", "MARTINEZ", "NGUYEN", "BROWN", "KIM", "WILLIAMS", "HERNANDEZ", "LEE", "JACKSON", "LOPEZ", "SINGH", "DAVIS", "TRAN",
          "MILLER", "ANDERSON", "TAYLOR", "MOORE", "CLARK", "WALKER", "WRIGHT", "SCOTT", "BAKER", "NELSON")
places <- data.frame(   # public landmarks and businesses
  address = c("233 S Wacker Dr", "20 W 34th St", "400 Broad St", "300 Alamo Plaza", "600 Biscayne Blvd", "225 Baker St NW",
              "4 S Market St", "401 E Jefferson St", "409 Blackwell St", "2000 Brush St", "1 Infinite Loop", "1600 Pennsylvania Ave NW"),
  city = c("Chicago", "New York", "Seattle", "San Antonio", "Miami", "Atlanta", "Boston", "Phoenix", "Durham", "Detroit", "Cupertino", "Washington"),
  state = c("IL", "NY", "WA", "TX", "FL", "GA", "MA", "AZ", "NC", "MI", "CA", "DC"),
  zip5 = c("60606", "10001", "98109", "78205", "33132", "30313", "02109", "85004", "27701", "48226", "95014", "20500"),
  stringsAsFactors = FALSE)
pick <- places[sample(nrow(places), 300, replace = TRUE), ]
df <- data.frame(customer_id = sprintf("S%04d", 0:299), first_name = sample(first, 300, replace = TRUE),
                 last_name = sample(last, 300, replace = TRUE), pick, stringsAsFactors = FALSE, row.names = NULL)
head(df)"""

R_GEO = """geo <- geocode(places$address, places$city, places$state, places$zip5)
cbind(places[c("address", "city")], geo[c("lookup_level", "lookup_conf")])"""

R_STRATA = """res <- strata(df$first_name, df$last_name, address = df$address, city = df$city, state = df$state, zip5 = df$zip5,
               passthrough = list(customer_id = df$customer_id))
stopifnot(identical(res$customer_id, df$customer_id))      # answers come back in input order
head(res[c("customer_id", "p_white", "p_black", "p_hispanic", "p_asian", "p_other", "dominant_race", "iu", "lookup_level")])"""

R_CHECK = """p <- c("p_white", "p_black", "p_hispanic", "p_asian", "p_other")
cat("probabilities sum to 1 on every row:", all(abs(rowSums(res[p]) - 1) < 1e-3), "\\n")
print(table(res$lookup_level))
print(round(tapply(res$iu, res$lookup_level, mean), 3))     # higher = less certain"""

R_WRU_MD = """## 4. A wru-style wrapper: your data frame back, with probability columns
`predict_race_aq()` returns your data frame with `pred.whi`, `pred.bla`, `pred.his`, `pred.asi`, `pred.oth` added (the column names the `wru` package uses), plus `pred.iu` and `pred.level` for STRATA. `bisg()` and `bifsg()` are available too."""
R_WRU = """names(df)[2:3] <- c("first", "surname")                 # the wrapper's default column names
out <- predict_race_aq(df, address = "address", city = "city", state = "state", zip = "zip5")
head(out[c("customer_id", "pred.whi", "pred.bla", "pred.his", "pred.asi", "pred.oth", "pred.iu", "pred.level")])"""

R_BIFSG = """bif <- predict_race_aq(df, zip = "zip5", model = "bifsg")     # BIFSG: first name + surname + ZIP; four classes, so pred.oth is NA
cat("rows with a BIFSG answer:", sum(!is.na(bif$pred.whi)), "of", nrow(bif), "\\n")"""

R_AGG_MD = """## 5. An aggregate example: describe a group with expected counts, not labels
The probabilities are meant to be **added up**. For a group of people the *expected count* of a class is the sum of its probabilities; counting each person's single top class throws information away and is biased towards the biggest class. Everything below is about **groups**, not individuals, and the data are invented, so the numbers only show the mechanics."""
R_AGG = """expected <- colSums(res[p])
data.frame(class = sub("p_", "", p), expected_count = round(expected, 1), expected_share = round(expected / nrow(res), 3), row.names = NULL)"""
R_AGG2 = """by_city <- aggregate(res[p], by = list(city = df$city), FUN = mean)
by_city$n <- as.vector(table(df$city)[by_city$city])
by_city[by_city$n >= 20, ]"""
R_END = PY_END.replace("The API returns", "The service returns")

R_FRIENDLY_MD = """## 6. What the package says when something is wrong
Plain messages instead of long errors: a missing key, a key the service doesn't accept (HTTP 401), the daily limit (429), input it can't read (422), and the first minutes after a service restart (503, which the package waits out and retries). A misspelt argument such as `mname =` is refused before anything is sent."""
R_FRIENDLY = """r <- tryCatch(strata("MARIA", "GARCIA", mname = "L"), error = function(e) conditionMessage(e))
cat(r, "\\n")"""

def r_cells():
    return [md(R_INTRO), code(R_INSTALL), code(R_SETUP), code(R_KEY), code(R_HEALTH), md(PY_DATA_MD), code(R_DATA),
            md(PY_GEO_MD.replace("`aq.geocode()`", "`geocode()`")), code(R_GEO),
            md("## 3. aqEthnicity STRATA: five-class probabilities, uncertainty index, lookup level\n`strata()` picks the finest geography each address resolves to. The package batches large inputs and returns the answers **in your row order**; `passthrough` echoes `customer_id` back so you can check it."),
            code(R_STRATA), code(R_CHECK), md(R_WRU_MD), code(R_WRU), code(R_BIFSG), md(R_AGG_MD), code(R_AGG), code(R_AGG2), md(R_FRIENDLY_MD), code(R_FRIENDLY), md(R_END)]

def write_nb(name, cl, kernel, lang, extra_meta=None):
    for i, c in enumerate(cl): c["id"] = f"cell{i:02d}"
    nb = {"cells": cl, "metadata": {"kernelspec": kernel, "language_info": {"name": lang}}, "nbformat": 4, "nbformat_minor": 5}
    if extra_meta: nb["metadata"].update(extra_meta)
    p = os.path.join(ROOT, "notebooks", name)
    json.dump(nb, open(p, "w"), indent=1, ensure_ascii=False); open(p, "a").write("\n"); print("wrote", p)

def write_qmd():
    out = ["---", 'title: "aqEthnicity quickstart (R): STRATA, BISG and BIFSG on made-up data"', "format: html", "execute:", "  eval: true", "  warning: false", "---", ""]
    out.append("*Pre-release.* Needs the aqEthnicity R package (not on CRAN yet) and an API key in the `AEQUUM_API_KEY` environment variable, or a hidden prompt when run interactively. **Every person here is invented** and every address is a public landmark or business address, so no accuracy figure is computed. Outputs are estimates for groups, not statements about any individual's race.\n")
    out.append("## Install and key\n")
    out.append("```{r}\n#| eval: false\n# PRE-RELEASE: install the development version from GitHub (the repository is created at release time)\ninstall.packages(c(\"remotes\", \"askpass\"))\nremotes::install_github(\"tleitch/aqEthnicity\")\n```\n")
    out.append("```{r}\nlibrary(aqEthnicity)\nif (!nzchar(Sys.getenv(\"AEQUUM_API_KEY\")) && interactive()) aq_set_key()   # hidden prompt; never printed or logged\nstr(aq_health())\n```\n")
    out.append(PY_DATA_MD + "\n")
    out.append("```{r}\n" + R_DATA + "\n```\n")
    out.append("## Lookup level\n\n```{r}\n" + R_GEO + "\n```\n")
    out.append("## STRATA\n\n```{r}\n" + R_STRATA + "\n```\n\n```{r}\n" + R_CHECK + "\n```\n")
    out.append(R_WRU_MD + "\n\n```{r}\n" + R_WRU + "\n```\n\n```{r}\n" + R_BIFSG + "\n```\n")
    out.append(R_AGG_MD + "\n\n```{r}\n" + R_AGG + "\n```\n\n```{r}\n" + R_AGG2 + "\n```\n")
    out.append(R_FRIENDLY_MD + "\n\n```{r}\n" + R_FRIENDLY + "\n```\n")
    out.append(R_END + "\n")
    os.makedirs(os.path.join(ROOT, "R"), exist_ok=True)
    open(os.path.join(ROOT, "R", "quickstart.qmd"), "w").write("\n".join(out)); print("wrote R/quickstart.qmd")

for kind in ("colab", "jupyter"):
    extra = {"colab": {"name": "quickstart_colab.ipynb", "provenance": []}} if kind == "colab" else None
    write_nb(f"quickstart_{kind}.ipynb", py_cells(kind), {"display_name": "Python 3", "language": "python", "name": "python3"}, "python", extra)
write_nb("quickstart_R_colab.ipynb", r_cells(), {"display_name": "R", "language": "R", "name": "ir"}, "R", {"colab": {"name": "quickstart_R_colab.ipynb", "provenance": []}})
write_qmd()
