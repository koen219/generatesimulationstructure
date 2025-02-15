import itertools


def product_of_parameters(parameters):
    """Compute the Cartesian product of search parameters."""
    param_list = [
        [(name, par) for par in values] for name, values in parameters.items()
    ]
    return list(itertools.product(*param_list))


def check_parameter(params):
    """Ensure parameter dictionary contains required keys and valid 'with' structure."""
    assert (
        "with" in params and "search" in params
    ), "Missing required keys: 'with' and 'search'"

    # Ensure 'with' parameters have equal lengths
    if params["with"]:  # Only check if 'with' is non-empty
        lengths = {len(values) for values in params["with"].values()}
        assert (
            len(lengths) == 1
        ), "All parameter lists in 'with' must have the same length"


def parse_parameter(params):
    """Compute all possible parameter combinations for simulations."""
    output = []

    product = product_of_parameters(params["search"])

    if params["with"]:
        with_params = [
            [(name, params["with"][name][i]) for name in params["with"]]
            for i in range(len(next(iter(params["with"].values()))))
        ]

        output = [tuple(w) + p for w in with_params for p in product]
    else:
        output = product  # If 'with' is empty, only use 'search' parameters

    #    print("-- Generating:")
    #    for pars in output:
    #        print(pars)

    return output
