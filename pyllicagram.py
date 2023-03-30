#!/usr/bin/python
# -*-coding:Utf-8 -*
#
# pyllicagram.py:
#    Un micro package python pour importer des données de [Gallicagram]
#
import sys
import os
import collections
import ssl
from typing import List, Literal
from urllib.parse import quote

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
    def calc_ratio(row):
        if row.total == 0:
            return 0
        return row.n / row.total

    result["ratio"] = result.apply(lambda row: calc_ratio(row), axis=1)
    return result


# ------------------------
# COMMAND LINE HANDLER
def get_args():
    args = {}
    for i in range(len(sys.argv)):
        if sys.argv[i][0] == "-":
            try:
                if sys.argv[i + 1][0] != "-":
                    args[sys.argv[i]] = sys.argv[i + 1]
                else:
                    args[sys.argv[i]] = True
            except:
                args[sys.argv[i]] = True
        else:
            args[i] = sys.argv[i]
    return args


if __name__ == "__main__":
    # Get command line args
    args = get_args()
    recherche = args[1]
    somme = args.get("-s", "+" in recherche)
    recherche = recherche.replace(",", "+").split("+")
    corpus = args.get("-c", "presse")
    debut = args.get("-d", 1789)
    fin = args.get("-f", 1950)
    resolution = args.get("-r", "default")

    # Call API
    results = pyllicagram(
        recherche=recherche,
        corpus=corpus,
        debut=debut,
        fin=fin,
        resolution=resolution,
        somme=somme,
    )

    # Write results into file
    results.to_csv("results.csv", sep="\t")
