import sys
import os
import ssl
from typing import List, Literal
from urllib.parse import quote
import urllib

ssl._create_default_https_context = ssl._create_unverified_context
# import pandas
try:
    import pandas as pd

    pd.read_csv(
        f"https://shiny.ens-paris-saclay.fr/guni/corpus=presse_test_from=1789_to=1950"
    )
    print(sys.executable)
except:
    print("install pandas...")
    # install pandas as a subprocess if needed
    os.system(sys.executable + " -m pip install pandas")
    os.system(sys.executable + " " + " ".join(sys.argv))
    exit()

# ------------------------
# API CALL


def pyllicagram(
    recherche: List[str] | str,
    corpus: Literal["lemonde", "livres", "presse"] = "presse",
    debut: int = 1789,
    fin: int = 1950,
    resolution: Literal["default", "annee", "mois"] = "default",
    somme: bool = False,
):
    if not isinstance(recherche, str) and not isinstance(recherche, list):
        raise ValueError("La recherche doit être une chaîne de caractères ou une liste")
    if not isinstance(recherche, list):
        recherche = [recherche]
    assert corpus in [
        "lemonde",
        "livres",
        "presse",
    ], 'Vous devez choisir le corpus parmi "lemonde","livres" et "presse"'
    assert resolution in [
        "default",
        "annee",
        "mois",
    ], 'Vous devez choisir la résolution parmi "default", "annee" ou "mois"'
    result = pd.DataFrame()
    for gram in recherche:
        format_gram = quote(gram, encoding="utf-8")
        df = pd.read_csv(
            f"https://shiny.ens-paris-saclay.fr/guni/corpus={corpus}_{format_gram}_from={debut}_to={fin}"
        )
        if resolution == "mois" and corpus != "livres":
            df = (
                df.groupby(["annee", "mois", "gram"])
                .agg({"n": "sum", "total": "sum"})
                .reset_index()
            )
        if resolution == "annee":
            df = (
                df.groupby(["annee", "gram"])
                .agg({"n": "sum", "total": "sum"})
                .reset_index()
            )
        result = pd.concat([result, df])
    if somme:
        result = (
            result.groupby(
                [
                    "annee",
                    *(("mois",) if "mois" in result.columns else ()),
                    *(("jour",) if "jour" in result.columns else ()),
                ]
            )
            .agg({"n": "sum", "total": "mean"})
            .reset_index()
        )
        result["gram"] = "+".join(recherche)

    # ensure ratio is not NaN
    def calc_ratio(row: pd.Series):
        if row.total == 0:
            return 0
        return row.n / row.total

    result["ratio"] = result.apply(lambda row: calc_ratio(row), axis=1)
    return result


def joker(gram, corpus="presse", debut=1789, fin=1950, after=True, n_joker=20):
    if not isinstance(gram, str) and not isinstance(gram, list):
        raise ValueError("La recherche doit être une chaîne de caractères ou une liste")
    assert corpus in [
        "lemonde",
        "livres",
        "presse",
    ], 'Vous devez choisir le corpus parmi "lemonde","livres" et "presse"'
    gram = urllib.parse.quote_plus(gram.lower()).replace("-", " ").replace(" ", "%20")
    df = pd.read_csv(
        f"https://shiny.ens-paris-saclay.fr/guni/joker?corpus={corpus}&mot={gram}&from={debut}&to={fin}&after={after}&n_joker={n_joker}"
    )
    return df


def contain(mot1, mot2, corpus="presse", debut=1789, fin=1950):
    if not isinstance(mot1, str) or not isinstance(mot2, str):
        raise ValueError("La recherche doit être une chaîne de caractères ou une liste")
    assert corpus in [
        "lemonde",
        "livres",
        "presse",
    ], 'Vous devez choisir le corpus parmi "lemonde","livres" et "presse"'
    mot1 = urllib.parse.quote_plus(mot1.lower()).replace("-", " ").replace(" ", "%20")
    mot2 = urllib.parse.quote_plus(mot2.lower()).replace("-", " ").replace(" ", "%20")
    df = pd.read_csv(
        f"https://shiny.ens-paris-saclay.fr/guni/contain?corpus={corpus}&mot1={mot1}&mot2={mot2}&from={debut}&to={fin}"
    )
    return df
