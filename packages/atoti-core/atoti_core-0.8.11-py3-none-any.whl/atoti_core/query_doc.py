QUERY_DOC = """Query the cube to retrieve the value of the passed measures on the given levels.

        In JupyterLab with the :mod:`atoti-jupyterlab <atoti_jupyterlab>` plugin installed, query results can be converted to interactive widgets with the :guilabel:`Convert to Widget Below` action available in the command palette or by right clicking on the representation of the returned Dataframe.

        {args}
"""

QUERY_ARGS_DOC = {
    "mode": """mode: The query mode.""",
    "pretty": """* ``"pretty"`` is best for queries returning small results:

                * A :class:`~atoti_query.QueryResult` will be returned and its rows will be sorted according to the level order.""",
    "raw": """* ``"raw"`` is best for benchmarks or large exports:

                * A faster and more efficient endpoint reducing the data transfer from Java to Python will be used.
                * A classic :class:`pandas.DataFrame` will be returned.
                * ``include_totals="True"`` will not be allowed.
                * The :guilabel:`Convert to Widget Below` action provided by the :mod:`atoti-jupyterlab <atoti_jupyterlab>` plugin will not be available.""",
    "timeout": """timeout: The duration the query execution can take before being aborted.""",
    "totals": """Totals can be useful but they make the DataFrame harder to work with since its index will have some empty values.""",
    "context": """context: Context values to use when executing the query.""",
}


def get_query_args_doc(*, is_query_session: bool) -> str:
    lines = (
        [
            'session = tt.QuerySession(f"http://localhost:{session.port}")',
            "cube = session.cubes[cube.name]",
        ]
        if is_query_session
        else []
    ) + ["h, l, m = cube.hierarchies, cube.levels, cube.measures"]
    example_lines = "\n                        ".join([f">>> {line}" for line in lines])
    default_context = (
        "\n\n                Defaults to :attr:`atoti.Cube.shared_context`."
    )
    keys_argument = """{"Continent", "Country", "Currency", "Year", "Month"}"""

    return f"""Args:
            measures: The measures to query.
            filter: The filtering condition.

                Examples:

                    .. doctest:: query

                        >>> df = pd.DataFrame(
                        ...     columns=["Continent", "Country", "Currency", "Year", "Month", "Price"],
                        ...     data=[
                        ...         ("Europe", "France", "EUR", 2023, 10, 200.0),
                        ...         ("Europe", "Germany", "EUR", 2024, 2, 150.0),
                        ...         ("Europe", "United Kingdom", "GBP", 2022, 10, 120.0),
                        ...         ("America", "United states", "USD", 2020, 5, 240.0),
                        ...         ("America", "Mexico", "MXN", 2021, 3, 270.0),
                        ...     ],
                        ... )
                        >>> table = session.read_pandas(
                        ...     df,
                        ...     keys={keys_argument},
                        ...     table_name="Prices",
                        ... )
                        >>> cube = session.create_cube(table)
                        >>> del cube.hierarchies["Continent"]
                        >>> del cube.hierarchies["Country"]
                        >>> cube.hierarchies["Geography"] = [
                        ...     table["Continent"],
                        ...     table["Country"],
                        ... ]
                        >>> del cube.hierarchies["Year"]
                        >>> del cube.hierarchies["Month"]
                        >>> cube.hierarchies["Date"] = [
                        ...     table["Year"],
                        ...     table["Month"],
                        ... ]
                        >>> cube.measures["American Price"] = tt.where(
                        ...     cube.levels["Continent"] == "America",
                        ...     cube.measures["Price.SUM"],
                        ... )
                        {example_lines}

                    Single equality condition:

                    .. doctest:: query

                        >>> cube.query(
                        ...     m["Price.SUM"],
                        ...     levels=[l["Country"]],
                        ...     filter=l["Continent"] == "Europe",
                        ... )
                                                 Price.SUM
                        Continent Country
                        Europe    France            200.00
                                  Germany           150.00
                                  United Kingdom    120.00

                    Combined equality condition:

                    .. doctest:: query

                        >>> cube.query(
                        ...     m["Price.SUM"],
                        ...     levels=[l["Country"], l["Currency"]],
                        ...     filter=(
                        ...         (l["Continent"] == "Europe")
                        ...         & (l["Currency"] == "EUR")
                        ...     ),
                        ... )
                                                   Price.SUM
                        Continent Country Currency
                        Europe    France  EUR         200.00
                                  Germany EUR         150.00

                    Hierarchy condition:

                    .. doctest:: query

                        >>> cube.query(
                        ...     m["Price.SUM"],
                        ...     levels=[l["Country"]],
                        ...     filter=h["Geography"].isin(
                        ...         ("America",), ("Europe", "Germany")
                        ...     ),
                        ... )
                                                Price.SUM
                        Continent Country
                        America   Mexico           270.00
                                  United states    240.00
                        Europe    Germany          150.00

                    Inequality condition:

                    .. doctest:: query

                        >>> cube.query(
                        ...     m["Price.SUM"],
                        ...     levels=[l["Country"], l["Currency"]],
                        ...     # Equivalent to `filter=(l["Currency"] != "GBP") & (l["Currency"] != "MXN")`
                        ...     filter=~l["Currency"].isin("GBP", "MXN"),
                        ... )
                                                         Price.SUM
                        Continent Country       Currency
                        America   United states USD         240.00
                        Europe    France        EUR         200.00
                                  Germany       EUR         150.00
                        >>> cube.query(
                        ...     m["Price.SUM"],
                        ...     levels=[l["Year"]],
                        ...     filter=l["Year"] >= 2022,
                        ... )
                             Price.SUM
                        Year
                        2022    120.00
                        2023    200.00
                        2024    150.00

                    Deep level of a multilevel hierarchy condition:

                    .. doctest:: query

                        >>> cube.query(
                        ...     m["Price.SUM"],
                        ...     levels=[l["Month"]],
                        ...     filter=l["Month"] == 10,
                        ... )
                                   Price.SUM
                        Year Month
                        2022 10       120.00
                        2023 10       200.00

            include_empty_rows: Whether to keep the rows where all the requested measures have no value.

                Example:

                    .. doctest:: query

                            >>> cube.query(
                            ...     m["American Price"],
                            ...     levels=[l["Continent"]],
                            ...     include_empty_rows=True,
                            ... )
                                      American Price
                            Continent
                            America           510.00
                            Europe


            include_totals: Whether to query the grand total and subtotals and keep them in the returned DataFrame.
                {QUERY_ARGS_DOC["totals"]}

                Example:

                    .. doctest:: query

                            >>> cube.query(
                            ...     m["Price.SUM"],
                            ...     levels=[l["Country"], l["Currency"]],
                            ...     include_totals=True,
                            ... )
                                                              Price.SUM
                            Continent Country        Currency
                            Total                                980.00
                            America                              510.00
                                      Mexico                     270.00
                                                     MXN         270.00
                                      United states              240.00
                                                     USD         240.00
                            Europe                               470.00
                                      France                     200.00
                                                     EUR         200.00
                                      Germany                    150.00
                                                     EUR         150.00
                                      United Kingdom             120.00
                                                     GBP         120.00

            levels: The levels to split on.
                If ``None``, the value of the measures at the top of the cube is returned.
            scenario: The scenario to query.
            {QUERY_ARGS_DOC["timeout"]}
            {QUERY_ARGS_DOC["mode"]}

              {QUERY_ARGS_DOC["pretty"]}

                .. doctest:: query

                    >>> cube.query(
                    ...     m["Price.SUM"],
                    ...     levels=[l["Continent"]],
                    ...     mode="pretty",
                    ... )
                              Price.SUM
                    Continent
                    America      510.00
                    Europe       470.00

              {QUERY_ARGS_DOC["raw"]}

                .. doctest:: query

                    >>> cube.query(
                    ...     m["Price.SUM"],
                    ...     levels=[l["Continent"]],
                    ...     mode="raw",
                    ... )
                      Continent  Price.SUM
                    0    Europe      470.0
                    1   America      510.0

            {QUERY_ARGS_DOC["context"] if is_query_session else QUERY_ARGS_DOC["context"] + default_context}
"""
