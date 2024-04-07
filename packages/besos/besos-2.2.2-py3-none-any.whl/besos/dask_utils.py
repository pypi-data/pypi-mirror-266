"""
Dask related helper functions.
"""

# External Libraries
import dask.bag as db


def dask_map(f, l):
    dask_bag = db.from_sequence(l)
    map_result = db.map(f, dask_bag).compute()
    return map_result
