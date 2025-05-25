import numba
from numba.typed import List
@numba.njit(cache=True)
def resupply_ann_fn(annotations, weights):

    needed_qty = annotations[0][0].lower*1000
    available_qty = annotations[1][0].lower*1000

    required_qty = needed_qty - available_qty
    if required_qty >0:
        return round(required_qty*0.001, 6), 1
    else:
        return 0,0
