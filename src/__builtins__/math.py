import math

from src.utils import definition


@definition(return_type='double', arg_types=['double'])
def sqrt(a):
    return math.sqrt(a)