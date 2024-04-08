import os

import pytest
from pytest import approx

from openclimatedata import CEDS

from pandas.testing import assert_series_equal

GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"

versions = CEDS.keys()


def test_ceds():
    for version in versions:
        assert CEDS[version].name
        assert CEDS[version].doi
        assert CEDS[version].published

        assert len(CEDS[version].entities) > 0


@pytest.mark.skipif(GITHUB_ACTIONS, reason="Test requires downloading.")
def test_ceds_reshaping():
    for version in versions:
        if int(CEDS[version].published[:4]) < 2024:
            df = CEDS[version]["CO"]["by_sector_country"].to_dataframe()

            if "iso" in df.columns:  # 2019 version
                code = "iso"
                value = 0.00018696315423434
            else:
                code = "country"
                value = 0.0288382599890555

            assert df[
                (df[code] == "abw") & (df.sector == "1A1a_Electricity-autoproducer")
            ]["X2014"].values[0] == approx(value)
            assert (
                df[
                    (df[code] == "abw") & (df.sector == "1A1a_Electricity-autoproducer")
                ]["X1750"].values[0]
                == 0
            )

            ocdf = CEDS[version]["CO"]["by_sector_country"].to_ocd()

            assert_series_equal(
                df[
                    (df[code] == "abw") & (df.sector == "1A1a_Electricity-autoproducer")
                ]["X1750"],
                ocdf[
                    (ocdf.code == "ABW")
                    & (ocdf.sector == "1A1a_Electricity-autoproducer")
                    & (ocdf.year == 1750)
                ]["value"],
                check_index=False,
                check_names=False,
            )
            assert_series_equal(
                df[
                    (df[code] == "abw") & (df.sector == "1A1a_Electricity-autoproducer")
                ]["X2014"],
                ocdf[
                    (ocdf.code == "ABW")
                    & (ocdf.sector == "1A1a_Electricity-autoproducer")
                    & (ocdf.year == 2014)
                ]["value"],
                check_index=False,
                check_names=False,
            )
        else:  # > 2024
            df = CEDS[version]["CO"]["by_sector_country"].to_dataframe()

            value = 0.0146970051332098
            assert df[
                (df["country"] == "abw")
                & (df.sector == "1A1a_Electricity-autoproducer")
            ]["X2022"].values[0] == approx(value)
            assert (
                df[
                    (df["country"] == "abw")
                    & (df.sector == "1A1a_Electricity-autoproducer")
                ]["X1750"].values[0]
                == 0
            )

            ocdf = CEDS[version]["CO"]["by_sector_country"].to_ocd()

            assert_series_equal(
                df[
                    (df["country"] == "abw")
                    & (df.sector == "1A1a_Electricity-autoproducer")
                ]["X1750"],
                ocdf[
                    (ocdf.code == "ABW")
                    & (ocdf.sector == "1A1a_Electricity-autoproducer")
                    & (ocdf.year == 1750)
                ]["value"],
                check_index=False,
                check_names=False,
            )
            assert_series_equal(
                df[
                    (df["country"] == "abw")
                    & (df.sector == "1A1a_Electricity-autoproducer")
                ]["X2022"],
                ocdf[
                    (ocdf.code == "ABW")
                    & (ocdf.sector == "1A1a_Electricity-autoproducer")
                    & (ocdf.year == 2022)
                ]["value"],
                check_index=False,
                check_names=False,
            )
