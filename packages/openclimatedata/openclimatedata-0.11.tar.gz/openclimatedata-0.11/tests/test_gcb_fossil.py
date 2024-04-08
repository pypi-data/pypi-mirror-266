import math
import os
import pytest
from pytest import approx

from openclimatedata import GCB_Fossil_Emissions

GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"


versions = GCB_Fossil_Emissions.keys()


def test_gcb_fossil():
    for version in versions:
        assert GCB_Fossil_Emissions[version].name
        assert GCB_Fossil_Emissions[version].doi
        assert GCB_Fossil_Emissions[version].published


@pytest.mark.skipif(GITHUB_ACTIONS, reason="Test requires downloading.")
def test_gcb_fossil_2023v28():
    df = GCB_Fossil_Emissions["2023v28"].to_dataframe()
    assert df.iloc[0]["Total"] == 0
    assert df.iloc[-1]["Per Capita"] == approx(4.663492)

    ocdf = GCB_Fossil_Emissions["2023v28"].to_ocd()
    # First and last value should be the same after re-shaping.
    assert ocdf.iloc[0]["value"] == df.iloc[0]["Total"]
    assert ocdf.iloc[-1]["value"] == df.iloc[-1]["Per Capita"]


@pytest.mark.skipif(GITHUB_ACTIONS, reason="Test requires downloading.")
def test_gcb_fossil_2023v36():
    df = GCB_Fossil_Emissions["2023v36"].to_dataframe()
    assert df.iloc[0]["Total"] == 0
    assert df.iloc[-1]["Per Capita"] == approx(4.658219)

    ocdf = GCB_Fossil_Emissions["2023v36"].to_ocd()
    # First and last value should be the same after re-shaping.
    assert ocdf.iloc[0]["value"] == df.iloc[0]["Total"]
    assert ocdf.iloc[-1]["value"] == df.iloc[-1]["Per Capita"]


@pytest.mark.skipif(GITHUB_ACTIONS, reason="Test requires downloading.")
def test_gcb_fossil_all_codes_set():
    df = GCB_Fossil_Emissions["2023v36"].to_dataframe()
    leeward_islands = df[df.Country == "Leeward Islands"]

    df_long = GCB_Fossil_Emissions["2023v36"].to_long_dataframe()

    assert (
        df_long[
            (df_long.Code == "Leeward Islands")
            & (df_long.Year == 1950)
            & (df_long.Category == "Total")
        ].Value.values[0]
        == leeward_islands[leeward_islands.Year == 1950].Total.values[0]
    )

    assert sum(df_long.Code.isnull()) == 0


@pytest.mark.skipif(GITHUB_ACTIONS, reason="Test requires downloading.")
def test_gcb_fossil_2023v43():
    df = GCB_Fossil_Emissions["2023v43"].to_dataframe()
    # This version has Cement with zero and Total as `nan`.
    assert math.isnan(df.iloc[0]["Total"])
    assert df.iloc[-1]["Per Capita"] == approx(4.658365)

    ocdf = GCB_Fossil_Emissions["2023v43"].to_ocd()
    # First and last value should be the same after re-shaping.
    assert math.isnan(ocdf.iloc[0]["value"]) and ocdf.iloc[0]["category"] == "Total"
    assert ocdf.iloc[-1]["value"] == df.iloc[-1]["Per Capita"]


@pytest.mark.skipif(GITHUB_ACTIONS, reason="Test requires downloading.")
def test_unique_code_name_combinations():
    # Saint Kitts and Nevis is included twice in GCB Fossil with code 'KNA'.
    # The second time the name is 'St-Kitts-Nevis-Anguilla'.
    # This should be handled in the long DataFrame which drops the country.
    for version in versions:
        df = GCB_Fossil_Emissions[version].to_dataframe()
        dfl = GCB_Fossil_Emissions[version].to_long_dataframe()
        assert len(df.Country.unique()) == len(dfl.Code.unique())


@pytest.mark.skipif(GITHUB_ACTIONS, reason="Test requires downloading.")
def test_kosovo_country_code():
    df = GCB_Fossil_Emissions["2023v43"].to_long_dataframe()

    assert len(df[df.Code == "XKX"]) == 0
    assert len(df[df.Code == "KSV"]) > 0

    ocdf = GCB_Fossil_Emissions["2023v43"].to_ocd()
    assert len(ocdf[ocdf.code == "KSV"]) == 0
    assert len(ocdf[ocdf.code == "XKX"]) > 0
