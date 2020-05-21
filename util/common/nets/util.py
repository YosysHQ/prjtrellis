# Useful functions for constructing nets.
def char_range(c1, c2):
    """Generates the characters from `c1` to `c2`, exclusive."""
    for c in range(ord(c1), ord(c2)):
        yield chr(c)

def net_product(net_list, range_iter):
    return [n.format(i) for i in range_iter for n in net_list]
