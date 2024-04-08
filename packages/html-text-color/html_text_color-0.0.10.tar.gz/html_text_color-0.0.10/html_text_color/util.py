def convert_to_ranks(lili: list[list[int]]) -> list[list[int]]:
    """
    Converts a list of lists of integers to a list of lists of ranks.
    """
    positional_li = sum(
        [[[x, i, j] for j, x in enumerate(l)] for i, l in enumerate(lili)], []
    )
    positional_li.sort(key=lambda x: x[0])
    pos = 0
    num = -float("inf")
    for entry in positional_li:
        gt = entry[0] > num
        entry[0] = pos
        pos += gt

    out_lili = [x.copy() for x in lili]
    for val, i, j in positional_li:
        out_lili[i][j] = val

    return out_lili
