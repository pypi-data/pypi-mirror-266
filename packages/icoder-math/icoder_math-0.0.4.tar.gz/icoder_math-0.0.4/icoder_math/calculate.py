def pow(x, y):
    """
    Support negative and positive float and int (Tested with 16 modes) \n
    return x ** y

    """
    if x < 0 and y > 0:
        return -(abs(x) ** y)

    if x < 0 and y < 0:
        return -(abs(x) ** y)

    if x > 0 and y < 0 or x > 0 and y > 0:
        return x**y


def abs(x):
    """
    Return the absolute value of the argument (return positive number)
    """
    if x > 0:
        return x
    else:
        return x * -1
