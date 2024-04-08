from ._core import _Global_Carbon_Budget_Release

GCB2023 = _Global_Carbon_Budget_Release(
    name="Global Carbon Budget 2023",
    version="1.1",
    doi="10.18160/GCP-2023",
    doi_article="10.5194/essd-15-5301-2023",
    published="2023-12-05",
    citation="Global Carbon Project, 2023. Supplemental data of Global Carbon Budget 2023. https://doi.org/10.18160/GCP-2023",
    citation_article="Friedlingstein, P., O'Sullivan, M., Jones, M. W., Andrew, R. M., Bakker, D. C. E., Hauck, J., Landschützer, P., Le Quéré, C., Luijkx, I. T., Peters, G. P., Peters, W., Pongratz, J., Schwingshackl, C., Sitch, S., Canadell, J. G., Ciais, P., Jackson, R. B., Alin, S. R., Anthoni, P., Barbero, L., Bates, N. R., Becker, M., Bellouin, N., Decharme, B., Bopp, L., Brasika, I. B. M., Cadule, P., Chamberlain, M. A., Chandra, N., Chau, T.-T.-T., Chevallier, F., Chini, L. P., Cronin, M., Dou, X., Enyo, K., Evans, W., Falk, S., Feely, R. A., Feng, L., Ford, D. J., Gasser, T., Ghattas, J., Gkritzalis, T., Grassi, G., Gregor, L., Gruber, N., Gürses, Ö., Harris, I., Hefner, M., Heinke, J., Houghton, R. A., Hurtt, G. C., Iida, Y., Ilyina, T., Jacobson, A. R., Jain, A., Jarníková, T., Jersild, A., Jiang, F., Jin, Z., Joos, F., Kato, E., Keeling, R. F., Kennedy, D., Klein Goldewijk, K., Knauer, J., Korsbakken, J. I., Körtzinger, A., Lan, X., Lefèvre, N., Li, H., Liu, J., Liu, Z., Ma, L., Marland, G., Mayot, N., McGuire, P. C., McKinley, G. A., Meyer, G., Morgan, E. J., Munro, D. R., Nakaoka, S.-I., Niwa, Y., O'Brien, K. M., Olsen, A., Omar, A. M., Ono, T., Paulsen, M., Pierrot, D., Pocock, K., Poulter, B., Powis, C. M., Rehder, G., Resplandy, L., Robertson, E., Rödenbeck, C., Rosan, T. M., Schwinger, J., Séférian, R., Smallman, T. L., Smith, S. M., Sospedra-Alfonso, R., Sun, Q., Sutton, A. J., Sweeney, C., Takao, S., Tans, P. P., Tian, H., Tilbrook, B., Tsujino, H., Tubiello, F., van der Werf, G. R., van Ooijen, E., Wanninkhof, R., Watanabe, M., Wimart-Rousseau, C., Yang, D., Yang, X., Yuan, W., Yue, X., Zaehle, S., Zeng, J., and Zheng, B.: Global Carbon Budget 2023, Earth Syst. Sci. Data, 15, 5301–5369, https://doi.org/10.5194/essd-15-5301-2023, 2023.",
    license="CC BY 4.0",
    filename="Global_Carbon_Budget_2023v1.1.xlsx",
    url="https://data.icos-cp.eu/licence_accept?ids=%5B%22NMvAsIKjrLx4KUeha_ckfVPP%22%5D",
    known_hash="34cbc0b082a3acbc782947a16bf7247d53cf867ab4a0cd241e8491f2d00842b9",
    sheets=[
        {
            "sheet_name": "Global Carbon Budget",
            "skiprows": 21,
        },
        {
            "sheet_name": "Historical Budget",
            "skiprows": 15,
        },
        {"sheet_name": "Fossil Emissions by Category", "skiprows": 8},
        {
            "sheet_name": "Land-Use Change Emissions",
            "skiprows": 34,
            "tables": [
                {
                    "table_name": "GCB",
                    "skiprows": 37,
                    "columns": "A:G",
                },
                {
                    "table_name": "BLUE",
                    "skiprows": 37,
                    "columns": "A,I:M",
                },
                {
                    "table_name": "H&C2023",
                    "skiprows": 37,
                    "columns": "A,N:R",
                },
                {
                    "table_name": "OSCAR",
                    "skiprows": 37,
                    "columns": "A,S:W",
                },
                {
                    "table_name": "Peat Drainage & Peat Fires",
                    "skiprows": list(range(36)) + [37],
                    "columns": "A,Y:AA",
                },
                {
                    "table_name": "Individual models (NET) - Does not include peat emissions",
                    "skiprows": list(range(36)) + [37],
                    "columns": "A,AC:AV,AX:AY",
                },
            ],
        },
        {
            "sheet_name": "Ocean Sink",
            "skiprows": 28,
            "tables": [
                {"table_name": "GCB", "skiprows": 30, "columns": "A:C"},
                {
                    "table_name": "Individual models",
                    "skiprows": 30,
                    "columns": "A,E:N,P:Q",
                },
                {
                    "table_name": "Data-based products",
                    "skiprows": 30,
                    "columns": "A,S:AB",
                },
            ],
        },
        {
            "sheet_name": "Terrestrial Sink",
            "skiprows": 26,
            "tables": [
                {"table_name": "GCB", "skiprows": 27, "columns": "A:B"},
                {
                    "table_name": "Individual models",
                    "skiprows": 27,
                    "columns": "A,D:W,Y:Z",
                },
            ],
        },
        {"sheet_name": "Cement Carbonation Sink", "skiprows": 9, "columns": "A,B,D,E"},
    ],
)
