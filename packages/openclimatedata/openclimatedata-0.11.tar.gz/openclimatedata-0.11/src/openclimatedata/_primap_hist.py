from dataclasses import dataclass
import pooch
import pandas as pd

paper_2016 = """Gütschow, J.; Jeffery, L.; Gieseke, R.; Gebel, R.; Stevens, D.; Krapp, M.; Rocha, M. (2016): The PRIMAP-hist national historical emissions time series, Earth Syst. Sci. Data, 8, 571-603, doi:10.5194/essd-8-571-2016"""

name_2_2 = "PRIMAP-hist 2.2"
doi_2_2 = "10.5281/zenodo.4479172"
published_2_2 = "2021-02-09"
citation_2_2 = (
    "Gütschow, J.; Günther, A.; Jeffery, L.; Gieseke, R. (2021): The PRIMAP-hist national historical emissions time series v2.2 (1850-2018). zenodo. doi:10.5281/zenodo.4479172."
    + paper_2016
)

name_2_3 = "PRIMAP-hist 2.3"
doi_2_3 = "10.5281/zenodo.5175154"
published_2_3 = "2021-08-30"
citation_2_3 = (
    "Gütschow, J.; Günther, A.; Pflüger, M. (2021): The PRIMAP-hist national historical emissions time series v2.3 (1850-2019). zenodo. doi:10.5281/zenodo.5175154."
    + paper_2016
)

name_2_3_1 = "PRIMAP-hist 2.3.1"
doi_2_3_1 = "10.5281/zenodo.5494497"
published_2_3_1 = "2021-09-22"
citation_2_3_1 = (
    """Gütschow, J.; Günther, A.; Pflüger, M. (2021): The PRIMAP-hist national historical emissions time series v2.3.1 (1850-2019). zenodo. doi:10.5281/zenodo.5494497.

"""
    + paper_2016
)

name_2_4 = "PRIMAP-hist 2.4"
doi_2_4 = "10.5281/zenodo.7179775"
published_2_4 = "2022-10-17"
citation_2_4 = (
    """Gütschow, J.; Pflüger, M. (2022): The PRIMAP-hist national historical emissions time series v2.4 (1750-2021). zenodo. doi:10.5281/zenodo.7179775.

"""
    + paper_2016
)

name_2_4_1 = "PRIMAP-hist 2.4.1"
doi_2_4_1 = "10.5281/zenodo.7585420"
published_2_4_1 = "2023-02-20"
citation_2_4_1 = (
    """Gütschow, J.; Pflüger, M. (2023): The PRIMAP-hist national historical emissions time series v2.4.1 (1750-2021). zenodo. doi:10.5281/zenodo.7585420.

"""
    + paper_2016
)

name_2_4_2 = "PRIMAP-hist 2.4.2"
doi_2_4_2 = "10.5281/zenodo.7727475"
published_2_4_2 = "2023-03-15"
citation_2_4_2 = (
    """Gütschow, J.; Pflüger, M. (2023): The PRIMAP-hist national historical emissions time series v2.4.2 (1750-2021). zenodo. doi:10.5281/zenodo.7727475.

"""
    + paper_2016
)

name_2_5 = "PRIMAP-hist 2.5"
doi_2_5 = "10.5281/zenodo.10006301"
published_2_5 = "2023-10-15"
citation_2_5 = (
    """Gütschow, J., & Pflüger, M. (2023). The PRIMAP-hist national historical emissions time series (1750-2022) v2.5 (2.5) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.10006301

"""
    + paper_2016
)

name_2_5_1 = "PRIMAP-hist 2.5.1"
doi_2_5_1 = "10.5281/zenodo.10705513"
published_2_5_1 = "2024-02-27"
citation_2_5_1 = (
    """Gütschow, J., Pflüger, M., & Busch, D. (2024). The PRIMAP-hist national historical emissions time series (1750-2022) v2.5.1 (2.5.1) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.10705513

"""
    + paper_2016
)


@dataclass
class _PRIMAPHIST_2:
    filename: str
    known_hash: str
    note: str
    name: str
    doi: str
    published: str
    citation: str
    license: str = "CC BY 4.0"

    def __repr__(self):
        return f"""{self.name}
'{self.filename}'
{self.note}

License: {self.license}
https://doi.org/{self.doi}

Recommended citation:
{self.citation}
        """

    def to_dataframe(self):
        full_path = pooch.retrieve(
            path=pooch.os_cache("openclimatedata"),
            url=f"doi:{self.doi}/{self.filename}",
            known_hash=self.known_hash,
            progressbar=True,
        )
        return pd.read_csv(full_path)

    def to_long_dataframe(self):
        df = self.to_dataframe()

        # Pre 2.5 provenance not included.
        if "provenance" not in df.columns:
            df["provenance"] = None
        if self.published >= published_2_3:
            id_vars = [
                "source",
                "scenario (PRIMAP-hist)",
                "provenance",
                "area (ISO3)",
                "entity",
                "unit",
                "category (IPCC2006_PRIMAP)",
            ]
        else:
            id_vars = [
                "scenario",
                "provenance",
                "country",
                "category",
                "entity",
                "unit",
            ]

        df = df.melt(
            id_vars=id_vars,
            var_name="year",
            value_name="value",
        )
        df.year = df.year.astype(int)
        return df

    def to_ocd(self):
        """Long DataFrame with all column names shortened."""
        df = self.to_long_dataframe()
        if self.published >= published_2_3:
            df = df.rename(
                columns={
                    "scenario (PRIMAP-hist)": "scenario",
                    "area (ISO3)": "code",
                    "category (IPCC2006_PRIMAP)": "category",
                }
            )
        else:
            df = df.rename(columns={"country": "code"})
        return df


PRIMAPHIST = {
    "2.2": _PRIMAPHIST_2(
        filename="PRIMAP-hist_v2.2_19-Jan-2021.csv",
        known_hash="md5:a3a8c25f7b784fdb85c89fbff29f5fd3",
        note="With numerical extrapolation of all time series to 2018.",
        name=name_2_2,
        doi=doi_2_2,
        published=published_2_2,
        citation=citation_2_2,
    ),
    "2.3": _PRIMAPHIST_2(
        filename="Guetschow-et-al-2021-PRIMAP-hist_v2.3_28_Jul_2021.csv",
        known_hash="md5:7b29dfb49ca97dcf594bc639767f1e2a",
        note="The main dataset with numerical extrapolation of all time series to 2019 and three significant digits.",
        name=name_2_3,
        doi=doi_2_3,
        published=published_2_3,
        citation=citation_2_3,
    ),
    "2.3.1": _PRIMAPHIST_2(
        filename="Guetschow-et-al-2021-PRIMAP-hist_v2.3.1_20-Sep_2021.csv",
        known_hash="md5:f4cb55a55e4d5e5dcfb1513b677ae318",
        note="The main dataset with numerical extrapolation of all time series to 2019 and three significant digits.",
        name=name_2_3_1,
        doi=doi_2_3_1,
        published=published_2_3_1,
        citation=citation_2_3_1,
    ),
    "2.3.1_no_extrap": _PRIMAPHIST_2(
        filename="Guetschow-et-al-2021-PRIMAP-hist_v2.3.1_no_extrap_20-Sep_2021.csv",
        known_hash="md5:870bf6d47e74f9245d9f9803d7be80ea",
        note="Variant without numerical extrapolation of missing values and not including country groups (three significant digits).",
        name=name_2_3_1,
        doi=doi_2_3_1,
        published=published_2_3_1,
        citation=citation_2_3_1,
    ),
    "2.3.1_no_extrap_no_rounding": _PRIMAPHIST_2(
        filename="Guetschow-et-al-2021-PRIMAP-hist_v2.3.1_no_extrap_no_rounding_20-Sep_2021.csv",
        known_hash="md5:f0b9afb73aefbf40693d475ea3dcc6ad",
        note="Variant without numerical extrapolation of missing values and not including country groups (eleven significant digits).",
        name=name_2_3_1,
        doi=doi_2_3_1,
        published=published_2_3_1,
        citation=citation_2_3_1,
    ),
    "2.4": _PRIMAPHIST_2(
        filename="Guetschow-et-al-2022-PRIMAP-hist_v2.4_11-Oct-2022.csv",
        known_hash="md5:502b68fb811fac25af8680e91898c324",
        note="The main dataset with numerical extrapolation of all time series to 2021 and three significant digits.",
        name=name_2_4,
        doi=doi_2_4,
        published=published_2_4,
        citation=citation_2_4,
    ),
    "2.4.1": _PRIMAPHIST_2(
        filename="Guetschow-et-al-2023-PRIMAP-hist_v2.4.1_final_16-Feb-2023.csv",
        known_hash="md5:220b45725161685f00ba48032f911b28",
        note="The main dataset with numerical extrapolation of all time series to 2021 and three significant digits.",
        name=name_2_4_1,
        doi=doi_2_4_1,
        published=published_2_4_1,
        citation=citation_2_4_1,
    ),
    "2.4.2": _PRIMAPHIST_2(
        filename="Guetschow-et-al-2023a-PRIMAP-hist_v2.4.2_final_09-Mar-2023.csv",
        known_hash="md5:4cd6ac6cf2cc53c211f7bbf6e951e3f1",
        note="The main dataset with numerical extrapolation of all time series to 2021 and three significant digits.",
        name=name_2_4_2,
        doi=doi_2_4_2,
        published=published_2_4_2,
        citation=citation_2_4_2,
    ),
    "2.5": _PRIMAPHIST_2(
        filename="Guetschow_et_al_2023b-PRIMAP-hist_v2.5_final_15-Oct-2023.csv",
        known_hash="md5:77405ac4eb5e915a7a9bfc25ff84d7c8",
        note="The main dataset with numerical extrapolation of all time series to 2022 and three significant digits.",
        name=name_2_5,
        doi=doi_2_5,
        published=published_2_5,
        citation=citation_2_5,
    ),
    "2.5.1": _PRIMAPHIST_2(
        filename="Guetschow_et_al_2024-PRIMAP-hist_v2.5.1_final_27-Feb-2024.csv",
        known_hash="md5:7de949e90dfc924c3829aa25d32afe1b",
        note="The main dataset with numerical extrapolation of all time series to 2022 and three significant digits.",
        name=name_2_5_1,
        doi=doi_2_5_1,
        published=published_2_5_1,
        citation=citation_2_5_1,
    ),
}
