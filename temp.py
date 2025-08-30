import numpy as np
from fractions import Fraction


a = np.array([[4, 2, 1, 11], [1, 3, 2, 10], [2, 1, 5, 13]], dtype=float)

a[1] = a[1] - (1/4)*a[0]
a[2] = a[2] - (2/4)*a[0]
# Print the matrix with each value as a/b form
for row in a:
    print([str(Fraction(val).limit_denominator()) for val in row])
