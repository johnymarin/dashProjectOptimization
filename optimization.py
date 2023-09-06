def bisection(f, a, b, tol=1e-6, max_iter=100):
    # check if the function changes sign in the interval
    if f(a) * f(b) > 0:
        raise ValueError("f(a) and f(b) must have opposit signs")

    # initializa the iteration counter and the error
    n = 0
    err = tol + 1

    # create a list to store the table rows
    rows = []

    # loop until the error is smaller than the tolerance or the maximun  number of iterations is reached
    while err > tol and n < max_iter:
        # find the midpoint  of the interval
        c = (a + b) / 2
        a_initial = a
        b_initial = b
        # evaluate the function at the midpoint
        fc = f(c)

        rows.append([n, b, a, c, f(b), f(a), fc, f(a) * fc, b - a])

        # update the interval based on the sign of fc
        if fc == 0:  # c is root
            return c
        elif f(a) * fc < 0:  # root is in [a, c]
            b = c
        else:  # root is in in [c, b]
            a = c

        # update the error and the iteration counter
        err = abs(b - a)
        n += 1

    # return the approximate root
    return c, rows

def quadratic_interpolation(f, x_vals, tol=1e-6, max_iter=100):
    x1, x2, x3 = x_vals
    f1, f2, f3 = f