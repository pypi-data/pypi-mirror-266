from ._core import _Global_Carbon_Budget_Release

GCB2022 = _Global_Carbon_Budget_Release(
    name="Global Carbon Budget 2022",
    version="1.0",
    doi="10.18160/gcp-2022",
    doi_article="10.5194/essd-14-4811-2022",
    published="2022-11-11",
    citation="Global Carbon Project. (2022). Supplemental data of Global Carbon Budget 2022 (Version 1.0) [Data set]. Global Carbon Project. https://doi.org/10.18160/gcp-2022",
    citation_article="Friedlingstein, P., O'Sullivan, M., Jones, M. W., Andrew, R. M., Gregor, L., Hauck, J., Le Quéré, C., Luijkx, I. T., Olsen, A., Peters, G. P., Peters, W., Pongratz, J., Schwingshackl, C., Sitch, S., Canadell, J. G., Ciais, P., Jackson, R. B., Alin, S. R., Alkama, R., Arneth, A., Arora, V. K., Bates, N. R., Becker, M., Bellouin, N., Bittig, H. C., Bopp, L., Chevallier, F., Chini, L. P., Cronin, M., Evans, W., Falk, S., Feely, R. A., Gasser, T., Gehlen, M., Gkritzalis, T., Gloege, L., Grassi, G., Gruber, N., Gürses, Ö., Harris, I., Hefner, M., Houghton, R. A., Hurtt, G. C., Iida, Y., Ilyina, T., Jain, A. K., Jersild, A., Kadono, K., Kato, E., Kennedy, D., Klein Goldewijk, K., Knauer, J., Korsbakken, J. I., Landschützer, P., Lefèvre, N., Lindsay, K., Liu, J., Liu, Z., Marland, G., Mayot, N., McGrath, M. J., Metzl, N., Monacci, N. M., Munro, D. R., Nakaoka, S.-I., Niwa, Y., O'Brien, K., Ono, T., Palmer, P. I., Pan, N., Pierrot, D., Pocock, K., Poulter, B., Resplandy, L., Robertson, E., Rödenbeck, C., Rodriguez, C., Rosan, T. M., Schwinger, J., Séférian, R., Shutler, J. D., Skjelvan, I., Steinhoff, T., Sun, Q., Sutton, A. J., Sweeney, C., Takao, S., Tanhua, T., Tans, P. P., Tian, X., Tian, H., Tilbrook, B., Tsujino, H., Tubiello, F., van der Werf, G. R., Walker, A. P., Wanninkhof, R., Whitehead, C., Willstrand Wranne, A., Wright, R., Yuan, W., Yue, C., Yue, X., Zaehle, S., Zeng, J., and Zheng, B.: Global Carbon Budget 2022, Earth Syst. Sci. Data, 14, 4811–4900, https://doi.org/10.5194/essd-14-4811-2022, 2022.",
    license="CC BY 4.0",
    filename="Global_Carbon_Budget_2022v1.0.xlsx",
    url="https://data.icos-cp.eu/licence_accept?ids=%5B%221umMtgeUlhS2Y1YW_Qp94bu3%22%5D",
    known_hash="d6e98cb607949614b6635616fd0a7de1bbb790fccaeaa96b9ff183db216c2b4d",
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
            "skiprows": 26,
            "tables": [
                {
                    "table_name": "GCB",
                    "skiprows": 29,
                    "columns": "A:D",
                },
                {
                    "table_name": "H&N",
                    "skiprows": 29,
                    "columns": "A,F:H",
                },
                {
                    "table_name": "BLUE",
                    "skiprows": 29,
                    "columns": "A,I:K",
                },
                {
                    "table_name": "OSCAR",
                    "skiprows": 29,
                    "columns": "A,L:N",
                },
                {
                    "table_name": "Individual models",
                    "skiprows": list(range(28)) + [29],
                    "columns": "A,P:AE,AG:AH",
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
            "skiprows": 21,
            "tables": [
                {"table_name": "GCB", "skiprows": 23, "columns": "A:B"},
                {
                    "table_name": "Individual models",
                    "skiprows": 23,
                    "columns": "A,D:S,U:V",
                },
            ],
        },
        {"sheet_name": "Cement Carbonation Sink", "skiprows": 9, "columns": "A,B,D,E"},
    ],
)
