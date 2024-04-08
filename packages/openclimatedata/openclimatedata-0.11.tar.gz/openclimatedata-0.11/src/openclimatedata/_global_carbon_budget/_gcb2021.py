from ._core import _Global_Carbon_Budget_Release

GCB2021 = _Global_Carbon_Budget_Release(
    name="Global Carbon Budget 2021",
    version="1.0",
    doi="10.18160/gcp-2021",
    doi_article="10.5194/essd-14-1917-2022",
    published="2022-03-21",
    citation="Global Carbon Project. (2021). Supplemental data of Global Carbon Budget 2021 (Version 1.0) [Data set]. Global Carbon Project. https://doi.org/10.18160/gcp-2021",
    citation_article="Friedlingstein, P., Jones, M. W., O'Sullivan, M., Andrew, R. M., Bakker, D. C. E., Hauck, J., Le Quéré, C., Peters, G. P., Peters, W., Pongratz, J., Sitch, S., Canadell, J. G., Ciais, P., Jackson, R. B., Alin, S. R., Anthoni, P., Bates, N. R., Becker, M., Bellouin, N., Bopp, L., Chau, T. T. T., Chevallier, F., Chini, L. P., Cronin, M., Currie, K. I., Decharme, B., Djeutchouang, L. M., Dou, X., Evans, W., Feely, R. A., Feng, L., Gasser, T., Gilfillan, D., Gkritzalis, T., Grassi, G., Gregor, L., Gruber, N., Gürses, Ö., Harris, I., Houghton, R. A., Hurtt, G. C., Iida, Y., Ilyina, T., Luijkx, I. T., Jain, A., Jones, S. D., Kato, E., Kennedy, D., Klein Goldewijk, K., Knauer, J., Korsbakken, J. I., Körtzinger, A., Landschützer, P., Lauvset, S. K., Lefèvre, N., Lienert, S., Liu, J., Marland, G., McGuire, P. C., Melton, J. R., Munro, D. R., Nabel, J. E. M. S., Nakaoka, S.-I., Niwa, Y., Ono, T., Pierrot, D., Poulter, B., Rehder, G., Resplandy, L., Robertson, E., Rödenbeck, C., Rosan, T. M., Schwinger, J., Schwingshackl, C., Séférian, R., Sutton, A. J., Sweeney, C., Tanhua, T., Tans, P. P., Tian, H., Tilbrook, B., Tubiello, F., van der Werf, G. R., Vuichard, N., Wada, C., Wanninkhof, R., Watson, A. J., Willis, D., Wiltshire, A. J., Yuan, W., Yue, C., Yue, X., Zaehle, S., and Zeng, J.: Global Carbon Budget 2021, Earth Syst. Sci. Data, 14, 1917–2005, https://doi.org/10.5194/essd-14-1917-2022, 2022.",
    license="CC BY 4.0",
    filename="Global_Carbon_Budget_2021v1.0.xlsx",
    url="https://data.icos-cp.eu/licence_accept?ids=%5B%22Ayyw1HeihXdTUoO000dGcxrP%22%5D",
    known_hash="032cb0d477a28577535283b4d34746731acf19303eac44824564e492456a692a",
    sheets=[
        {
            "sheet_name": "Global Carbon Budget",
            "skiprows": 20,
        },
        {
            "sheet_name": "Historical Budget",
            "skiprows": 15,
        },
        {"sheet_name": "Fossil Emissions by Category", "skiprows": 8},
        {
            "sheet_name": "Land-Use Change Emissions",
            "skiprows": 27,
            "tables": [
                {
                    "table_name": "GCB",
                    "skiprows": 30,
                    "columns": "A:D",
                },
                {
                    "table_name": "H&N",
                    "skiprows": 30,
                    "columns": "A,F:H",
                },
                {
                    "table_name": "BLUE",
                    "skiprows": 30,
                    "columns": "A,I:K",
                },
                {
                    "table_name": "OSCAR",
                    "skiprows": 30,
                    "columns": "A,L:N",
                },
                {
                    "table_name": "Individual models",
                    "skiprows": list(range(29)) + [30],
                    "columns": "A,P:AF,AH:AI",
                },
            ],
        },
        {
            "sheet_name": "Ocean Sink",
            "skiprows": 25,
            "tables": [
                {"table_name": "GCB", "skiprows": 27, "columns": "A:C"},
                {
                    "table_name": "Individual models",
                    "skiprows": 27,
                    "columns": "A,E:L,N:O",
                },
                {
                    "table_name": "Data-based products",
                    "skiprows": 27,
                    "columns": "A,Q:Z",
                },
            ],
        },
        {
            "sheet_name": "Terrestrial Sink",
            "skiprows": 22,
            "tables": [
                {"table_name": "GCB", "skiprows": 24, "columns": "A:B"},
                {
                    "table_name": "Individual models",
                    "skiprows": 24,
                    "columns": "A,D:T,V:W",
                },
            ],
        },
        {"sheet_name": "Cement Carbonation Sink", "skiprows": 9, "columns": "A,B,D,E"},
    ],
)
