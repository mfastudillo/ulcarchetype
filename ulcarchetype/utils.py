import brightway2 as bw
import pandas as pd
import numpy as np
import math

def is_method_uncertain(method):
    """check if method is uncertain"""
    cfs = bw.Method(method).load()
    cf_values = [cf_value for flow, cf_value in cfs]

    return any(isinstance(x, dict) for x in cf_values)


def uncertain_archetype_dict(biosphere_database=bw.Database("biosphere3")):
    """returns a dict with the key for all the flows without archetype defiend"""

    biosphere_dict_unclassified = {}
    for f in biosphere_database:
        compartments = f["categories"]
        compartment = compartments[0]

        if len(compartments) != 2:
            biosphere_dict_unclassified[(f["database"], f["code"])] = (
                f["name"],
                compartment,
            )

    # reverse it to: code: (name,compartment)
    biosphere_dict_unclassified_rev = {
        v: k for k, v in biosphere_dict_unclassified.items()
    }
    return biosphere_dict_unclassified_rev



def minmax_archetype(cf_df):
    """
    args:
        a pandas dataframe as formated by the function get_cf_info
    returns: returns a pandas dataframe with columns:
    - code: elementary flow key
    - name: elementary flow name
    - amount: best guess of CF (loc?)
    - minimum: maximum value of CF
    - maximum: minimum value of CF

    only for the flows with uncertainty associated to the archetype

    returns none if the method does not have any "uncertain" CF.
    """

    # dict with the keys of flows with unespecified archetype
    biosphere_dict_unclassified_rev = uncertain_archetype_dict()

    if None not in cf_df.subcompartment.unique():
        # case where there's no undefined subcompartment case
        df_minmax = None
    
    elif (cf_df.subcompartment.unique() == np.array(None)).all():
        df_minmax = None
    else:
        # calculate range
        df_minmax = (
        cf_df.set_index(["name", "compartment", "subcompartment"])["amount"]
        .unstack("subcompartment")
        .rename({np.nan: "undefined"}, axis=1)
        .drop("undefined", axis=1)
        .apply(["min", "max"], axis=1)
        )

        # if only defined in "undefined" there are nones in the min max
        df_minmax = df_minmax.dropna(axis="index")

        # add default
        df_minmax["amount"] = cf_df[cf_df.subcompartment.isna()].set_index(
            ["name", "compartment"]
            )["amount"]

        # min max is undefined because only
        # unspecified subcompartmet exists
        df_minmax = df_minmax.dropna(axis=0, how="all")

        # add the biosphere key code to the dataframe with ranges
        df_minmax = df_minmax.reset_index().rename(
        {"level_0": "name", "level_1": "compartment"}, axis=1
        )

        df_minmax["key"] = list(zip(df_minmax["name"], df_minmax["compartment"]))
        df_minmax["code"] = df_minmax["key"].map(biosphere_dict_unclassified_rev)

        # I forgot why this is needed
        df_minmax = df_minmax[df_minmax.code.notna()]

        # translate to naming convention expected in the uncertainty dict
        df_minmax = df_minmax.rename({"min": "minimum", "max": "maximum"}, axis=1)

    
        # eliminate cases where they are nearly the same
        df_minmax = df_minmax[~df_minmax.apply(lambda x:math.isclose(x.minimum,
        x.maximum,rel_tol=0.001),axis=1)]
        

        # drop cases with undefined amount
        df_minmax = df_minmax[df_minmax.amount.notna()]

        df_minmax = df_minmax[
            ["code", "name", "amount", "minimum", "maximum", "compartment"]
        ]

        # if just one cf is defined and it is for the undefined archetype
        # this will generate nans, that are not needed
        df_minmax = df_minmax.dropna(axis=1)

    return df_minmax


def get_cf_info(m):
    """extracts info on the characterisation factors of a method
    given the name. Currently prepared only for methods without
    uncertainty, where CF are only a tuple (key,amount)"""

    assert m in bw.methods

    M = bw.Method(m)
    cfs = M.load()
    info = []
    for cf in cfs:
        key,value = cf
        flow = bw.get_activity(key)
        compartiments = flow["categories"]
        compartiment = compartiments[0]
        try:
            subcompartment = compartiments[1]
        except IndexError:
            subcompartment = None
        info.append(
            (
                flow["database"],
                flow["code"],
                flow["name"],
                value,
                flow["unit"],
                flow["type"],
                compartiment,
                subcompartment,
            )
        )

    df = pd.DataFrame(
        info,
        columns=[
            "database",
            "code",
            "name",
            "amount",
            "unit",
            "type",
            "compartment",
            "subcompartment",
        ],
    )

    return df



def cf_add_uncertainty(method, uncertainty_type=4):
    """returns the cf with the uncertainty associated to the archetype
    if existing. Otherwise it returns a None value"""

    cf_df = get_cf_info(method)
    number_cf = len(cf_df)
    df_minmax = minmax_archetype(cf_df)

    # cond 1: method does not have uncertain CF
    cond1 = pd.api.types.is_object_dtype(cf_df.amount)
    # cond 2,3 and 4 validate if there are cases to be calculated
    cond2 = cf_df.subcompartment.isna().sum() == 0
    cond3 = df_minmax is None

    if cond3:
        cond4 = False
    else:
        cond4 = len(df_minmax) == 0

    if cond1 or cond2 or cond3 or cond4:
        cflist = None
    else:
        
        cf_df["key"] = list(zip(cf_df["database"], cf_df["code"]))

        # eleminate the static cf for the cases where an uncertain cf
        # is defined
        cf_df = cf_df.set_index("key").drop(df_minmax["code"].unique())

        cflist_certain = list(zip(cf_df.index, cf_df["amount"]))

        if uncertainty_type == 4:
            df_minmax["uncertainty type"] = 4
            df_minmax = df_minmax.set_index("code")[
            ["amount", "maximum", "minimum", "uncertainty type"]
            ]
            cflist_uncertain = list(
            zip(df_minmax.index, df_minmax.to_dict(orient="records"))
            )

        elif uncertainty_type == 5:
            df_minmax["uncertainty type"] = 5
            df_minmax.loc[:, "loc"] = df_minmax.loc[:, "amount"]
            df_minmax = df_minmax.set_index("code")[
                ["amount", "maximum", "minimum", "loc", "uncertainty type"]
            ]
            cflist_uncertain = list(
            zip(df_minmax.index, df_minmax.to_dict(orient="records"))
            )
        else:
            raise ValueError(
            "uncertainty types only defined for uniform (4) or triangular (5)"
            )
        # add both
        cflist = cflist_certain + cflist_uncertain

        assert len(cflist_uncertain) + len(cflist_certain) == number_cf
    
    return cflist
