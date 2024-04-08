import os
import pytest
from pytest import approx

import pandas as pd

from openclimatedata import GCB_Global_Carbon_Budget

GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"


versions = GCB_Global_Carbon_Budget.keys()


def test_gcb():
    for version in versions:
        assert GCB_Global_Carbon_Budget[version].name
        assert GCB_Global_Carbon_Budget[version].doi
        assert GCB_Global_Carbon_Budget[version].published


@pytest.mark.skipif(GITHUB_ACTIONS, reason="Test requires downloading.")
def test_gcb_sheet_names():
    for version in versions:
        sheet_names = GCB_Global_Carbon_Budget[version].keys()

        assert "Global Carbon Budget" in sheet_names
        assert "Historical Budget" in sheet_names
        assert "Fossil Emissions by Category" in sheet_names
        assert "Land-Use Change Emissions" in sheet_names
        assert "Ocean Sink" in sheet_names
        assert "Terrestrial Sink" in sheet_names
        assert "Cement Carbonation Sink" in sheet_names


@pytest.mark.skipif(GITHUB_ACTIONS, reason="Test requires downloading.")
def test_gcb_dataframes_for_subtables_only():
    # In sheets with subtables, `to_dataframe` etc. should only be available
    # for tables, not on the main sheet.
    for version in versions:

        sheet_names = GCB_Global_Carbon_Budget[version].keys()

        for sheet_name in sheet_names:
            if len(GCB_Global_Carbon_Budget[version][sheet_name].keys()) > 0:
                assert "to_dataframe" not in dir(
                    GCB_Global_Carbon_Budget[version][sheet_name]
                )
                assert "to_long_dataframe" not in dir(
                    GCB_Global_Carbon_Budget[version][sheet_name]
                )


@pytest.mark.skipif(GITHUB_ACTIONS, reason="Test requires downloading.")
def test_gcb_2023():
    year = "2023"
    global_carbon_budget = GCB_Global_Carbon_Budget[year][
        "Global Carbon Budget"
    ].to_dataframe()
    historical_budget = GCB_Global_Carbon_Budget[year][
        "Historical Budget"
    ].to_dataframe()
    fossil_emissions_by_category = GCB_Global_Carbon_Budget[year][
        "Fossil Emissions by Category"
    ].to_dataframe()
    luc_emissions_gcb = GCB_Global_Carbon_Budget[year]["Land-Use Change Emissions"][
        "GCB"
    ].to_dataframe()
    luc_emisssions_individual_models = GCB_Global_Carbon_Budget[year][
        "Land-Use Change Emissions"
    ]["Individual models (NET) - Does not include peat emissions"].to_dataframe()
    ocean_sink_gcb = GCB_Global_Carbon_Budget[year]["Ocean Sink"]["GCB"].to_dataframe()
    ocean_sink_data_based_products = GCB_Global_Carbon_Budget[year]["Ocean Sink"][
        "Data-based products"
    ].to_dataframe()
    terrestrial_sink_gcb = GCB_Global_Carbon_Budget[year]["Terrestrial Sink"][
        "GCB"
    ].to_dataframe()
    terrestrial_sink_individual_models = GCB_Global_Carbon_Budget[year][
        "Terrestrial Sink"
    ]["Individual models"].to_dataframe()
    cement_carbonation_sink = GCB_Global_Carbon_Budget[year][
        "Cement Carbonation Sink"
    ].to_dataframe()

    assert global_carbon_budget["fossil emissions excluding carbonation"].loc[
        1959
    ] == approx(2.41666545551985)
    assert global_carbon_budget["budget imbalance"].loc[2022] == approx(
        -0.0921741721108096
    )

    assert historical_budget["fossil emissions excluding carbonation"].loc[
        1750
    ] == approx(0.00253982996724891)
    assert historical_budget["budget imbalance"].loc[2022] == approx(
        -0.0921741721108091
    )

    assert fossil_emissions_by_category["fossil.emissions.excluding.carbonation"].loc[
        1850
    ] == approx(53.6986807874229)
    assert fossil_emissions_by_category["Per.Capita"].loc[2022] == approx(
        1.27134792448779
    )

    assert luc_emissions_gcb.Net.loc[1959] == approx(2.12152666666667)
    assert luc_emisssions_individual_models["Model Spread (sd)"].loc[2022] == approx(
        0.607291045665856
    )

    assert ocean_sink_gcb.GCB.loc[1959] == approx(0.992419800030039)
    assert ocean_sink_data_based_products["sd data-products (excl. Watson.)"].loc[
        2022
    ] == approx(0.31727790009081)

    assert terrestrial_sink_gcb.GCB.loc[1959] == approx(0.430358951653902)
    assert terrestrial_sink_individual_models["Model Spread (sd)"].loc[2022] == approx(
        0.829692166272794
    )

    assert cement_carbonation_sink.GCB.loc[1959] == approx(12.542147)
    assert cement_carbonation_sink.GCB.loc[2022] == approx(217.464615)
    assert pd.isna(cement_carbonation_sink.Huang[2022])


@pytest.mark.skipif(GITHUB_ACTIONS, reason="Test requires downloading.")
def test_gcb_2022():
    year = "2022"
    global_carbon_budget = GCB_Global_Carbon_Budget[year][
        "Global Carbon Budget"
    ].to_dataframe()
    historical_budget = GCB_Global_Carbon_Budget[year][
        "Historical Budget"
    ].to_dataframe()
    fossil_emissions_by_category = GCB_Global_Carbon_Budget[year][
        "Fossil Emissions by Category"
    ].to_dataframe()
    luc_emissions_gcb = GCB_Global_Carbon_Budget[year]["Land-Use Change Emissions"][
        "GCB"
    ].to_dataframe()
    luc_emisssions_individual_models = GCB_Global_Carbon_Budget[year][
        "Land-Use Change Emissions"
    ]["Individual models"].to_dataframe()
    ocean_sink_gcb = GCB_Global_Carbon_Budget[year]["Ocean Sink"]["GCB"].to_dataframe()
    ocean_sink_data_based_products = GCB_Global_Carbon_Budget[year]["Ocean Sink"][
        "Data-based products"
    ].to_dataframe()
    terrestrial_sink_gcb = GCB_Global_Carbon_Budget[year]["Terrestrial Sink"][
        "GCB"
    ].to_dataframe()
    terrestrial_sink_individual_models = GCB_Global_Carbon_Budget[year][
        "Terrestrial Sink"
    ]["Individual models"].to_dataframe()
    cement_carbonation_sink = GCB_Global_Carbon_Budget[year][
        "Cement Carbonation Sink"
    ].to_dataframe()

    assert global_carbon_budget["fossil emissions excluding carbonation"].loc[
        1959
    ] == approx(2.41709093103705)
    assert global_carbon_budget["budget imbalance"].loc[2021] == approx(
        -0.57757145051883
    )

    assert historical_budget["fossil emissions excluding carbonation"].loc[
        1750
    ] == approx(0.002552)
    assert historical_budget["budget imbalance"].loc[2021] == approx(-0.57757145051883)

    assert fossil_emissions_by_category["fossil.emissions.excluding.carbonation"].loc[
        1850
    ] == approx(53.738)
    assert fossil_emissions_by_category["Per.Capita"].loc[2021] == approx(
        1.28103137304945
    )

    assert luc_emissions_gcb.Net.loc[1959] == approx(1.93893333333333)
    assert luc_emisssions_individual_models["Model Spread (sd)"].loc[2021] == approx(
        0.488150134956261
    )

    assert ocean_sink_gcb.GCB.loc[1959] == approx(0.975005218749614)
    assert ocean_sink_data_based_products["sd data-products (excl. Watson.)"].loc[
        2021
    ] == approx(0.24795776316279)

    assert terrestrial_sink_gcb.GCB.loc[1959] == approx(0.401805228689998)
    assert terrestrial_sink_individual_models["Model Spread (sd)"].loc[2021] == approx(
        0.888433352902292
    )

    assert cement_carbonation_sink.GCB.loc[1959] == approx(12.684256)
    assert cement_carbonation_sink.GCB.loc[2021] == approx(229.794956)
    assert pd.isna(cement_carbonation_sink.Guo[2021])


@pytest.mark.skipif(GITHUB_ACTIONS, reason="Test requires downloading.")
def test_gcb_2021():
    year = "2021"
    global_carbon_budget = GCB_Global_Carbon_Budget[year][
        "Global Carbon Budget"
    ].to_dataframe()
    historical_budget = GCB_Global_Carbon_Budget[year][
        "Historical Budget"
    ].to_dataframe()
    fossil_emissions_by_category = GCB_Global_Carbon_Budget[year][
        "Fossil Emissions by Category"
    ].to_dataframe()
    luc_emissions_gcb = GCB_Global_Carbon_Budget[year]["Land-Use Change Emissions"][
        "GCB"
    ].to_dataframe()
    luc_emisssions_individual_models = GCB_Global_Carbon_Budget[year][
        "Land-Use Change Emissions"
    ]["Individual models"].to_dataframe()
    ocean_sink_gcb = GCB_Global_Carbon_Budget[year]["Ocean Sink"]["GCB"].to_dataframe()
    ocean_sink_data_based_products = GCB_Global_Carbon_Budget[year]["Ocean Sink"][
        "Data-based products"
    ].to_dataframe()
    terrestrial_sink_gcb = GCB_Global_Carbon_Budget[year]["Terrestrial Sink"][
        "GCB"
    ].to_dataframe()
    terrestrial_sink_individual_models = GCB_Global_Carbon_Budget[year][
        "Terrestrial Sink"
    ]["Individual models"].to_dataframe()
    cement_carbonation_sink = GCB_Global_Carbon_Budget[year][
        "Cement Carbonation Sink"
    ].to_dataframe()

    assert global_carbon_budget["fossil emissions excluding carbonation"].loc[
        1959
    ] == approx(2.41713282396274)
    assert global_carbon_budget["budget imbalance"].loc[2020] == approx(
        -0.775025676533141
    )

    assert historical_budget["fossil emissions excluding carbonation"].loc[
        1750
    ] == approx(0.002552)
    assert historical_budget["budget imbalance"].loc[2020] == approx(-0.775025676531002)

    assert fossil_emissions_by_category["fossil.emissions.excluding.carbonation"].loc[
        1959
    ] == approx(2417.13282396274)
    assert fossil_emissions_by_category["Per.Capita"].loc[2020] == approx(
        1.21875600594367
    )

    assert luc_emissions_gcb.Net.loc[1959] == approx(1.84551880806033)
    assert luc_emisssions_individual_models["Model Spread (sd)"].loc[2020] == approx(
        0.730856668977054
    )

    assert ocean_sink_gcb.GCB.loc[1959] == approx(0.918022208427885)
    assert ocean_sink_data_based_products["sd data-products (excl. Watson.)"].loc[
        2020
    ] == approx(0.33545744617825)

    assert terrestrial_sink_gcb.GCB.loc[1959] == approx(0.395882352941176)
    assert terrestrial_sink_individual_models["Model Spread (sd)"].loc[2020] == approx(
        0.989381862876127
    )

    assert cement_carbonation_sink.GCB.loc[1959] == approx(12.68373)
    assert cement_carbonation_sink.GCB.loc[2020] == approx(218.796424)
    assert pd.isna(cement_carbonation_sink.Guo[2020])
