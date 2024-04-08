from dataclasses import dataclass
import pooch
import pandas as pd


@dataclass
class _GCB_National:
    sheet_name: str
    skiprows: int
    note: str
    methods: str
    citation: str
    name: str
    doi: str
    filename: str
    url: str
    hash: str
    license: str

    def __repr__(self):
        return f"""{self.name}
'{self.filename}' - '{self.sheet_name}'

License: {self.license}
https://doi.org/{self.doi}

{self.note}

{self.citation}"""

    def to_dataframe(self):
        file_path = pooch.retrieve(
            path=pooch.os_cache("openclimatedata"),
            fname=self.filename,
            url=self.url,
            known_hash=self.hash,
        )
        return pd.read_excel(
            file_path, sheet_name=self.sheet_name, skiprows=self.skiprows, index_col=0
        )

    def to_long_dataframe(self):
        df = self.to_dataframe()
        df.index.name = "Year"
        value_vars = df.columns
        return df.reset_index().melt(
            id_vars=["Year"],
            value_vars=value_vars,
            var_name="Area",
            value_name="Value",
        )


GCB_National_Emissions = {
    "2022_territorial": _GCB_National(
        name="National Fossil Carbon Emissions 2022 v1.0",
        doi="10.18160/gcp-2022",
        filename="National_Fossil_Carbon_Emissions_2022v1.0.xlsx",
        url="https://data.icos-cp.eu/licence_accept?ids=%5B%22zL1wtJrG7Q5xdvF39Ylg3lUw%22%5D",
        hash="sha256:ccbd70b49ac6ed0e7176f177f58960de5530034623241c6ca7d5b33ae6af5c01",
        sheet_name="Territorial Emissions",
        skiprows=11,
        note="""Fossil CO2 emissions by country (territorial)
All values in million tonnes of carbon per year. For values in million tonnes of CO2 per year, multiply the values below by 3.664
1MtC = 1 million tonne of carbon = 3.664 million tonnes of CO2
""",
        citation="""Cite as: Friedlingstein et al. (2022)""",
        methods="""Full details of the method are described in Friedlingstein et al (2022) and Andrew and Peters (2021)
(1) National estimates include emissions from fossil fuel combustion and oxidation and cement production and excludes emissions from bunker fuels. World totals include emissions from bunker fuels.
(2) Bunker fuels: Emissions from fuels used for international aviation and maritime transport
(3) The disaggregations of regions (e.g. the former Soviet Union prior to 1992) are based on the shares of emissions in the first year after the countries are disaggregated (e.g., 1992 for the Former Soviet Union).
(4) The statistical difference presented on column HX is the difference between the world emissions and the sum of the emissions for each countries and for the bunker fuels.
""",
        license="CC BY 4.0",
    ),
    "2021_territorial": _GCB_National(
        name="National Fossil Carbon Emissions 2021 v1.0",
        doi="10.18160/gcp-2021",
        filename="National_Carbon_Emissions_2021v1.0.xlsx",
        url="https://data.icos-cp.eu/licence_accept?ids=%5B%22lApekzcmd4DRC34oGXQqOxbJ%22%5D",
        hash="sha256:940a5e9337267780d10b7e2819742a3b16c97fa41132274e4c5441696c991a70",
        sheet_name="Territorial Emissions",
        skiprows=11,
        note="""Fossil CO2 emissions by country (territorial)
All values in million tonnes of carbon per year. For values in million tonnes of CO2 per year, multiply the values below by 3.664
1MtC = 1 million tonne of carbon = 3.664 million tonnes of CO2""",
        citation="""Cite as: Friedlingstein et al. 2021""",
        methods="""Methods: Full details of the method are described in Friedlingstein et al. (2021) and Andrew and Peters (2021)
(1) National estimates include emissions from fossil fuel combustion and oxidation and cement production and excludes emissions from bunker fuels. World totals include emissions from bunker fuels.
(2) Bunker fuels: Emissions from fuels used for international aviation and maritime transport
(3) The disaggregations of regions (e.g. the former Soviet Union prior to 1992) are based on the shares of emissions in the first year after the countries are disaggregated (e.g., 1992 for the Former Soviet Union).
(4) The statistical difference presented on column HX is the difference between the world emissions and the sum of the emissions for each countries and for the bunker fuels.""",
        license="CC BY 4.0",
    ),
}
