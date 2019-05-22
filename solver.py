"""Module docstring"""

import operations as op


def apply_operations(value_and_ops, operations):
    """
    Apply each opeation to the value in the first element in value_and_ops and
    append the applied operation to the second element in value_and_ops.
    """
    value, current_ops = value_and_ops
    result = []
    for operation in operations:
        try:
            result.append((operation.apply(value), current_ops + [operation]))
        except RuntimeError:
            pass
    return result
    # return [(op.apply(value), current_ops + [op]) for op in operations]


if __name__ == '__main__':
    # xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    ## O nível 127 foi o que me fez criar esse programa
    # start_value = -1
    # target_value = 2020
    # num_moves = 8

    # operations = [op.MultiplyX(3),
    #               op.SumX(2),
    #               op.SumX(8),
    #               op.Mirror(),
    #               op.Reverse()]
    # xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

    # xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    ## Some level
    start_value = 0
    target_value = 28
    num_moves = 5

    operations = [op.AddDigits(1),
                  op.SumX(2),
                  # op.SumX(2),
                  # op.Mirror(),
                  # op.Reverse()
                  ]

    # mb = op.ModifyButtons_AddValue(operations, 3)
    # operations.append(mb)
    # xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

    values_and_ops = [(start_value, [])]
    for move_idx in range(num_moves):
        new_values_and_ops = []
        for v_and_ops in values_and_ops:
            new_values_and_ops.extend(apply_operations(v_and_ops, operations))
        values_and_ops = new_values_and_ops

    print("Tested plays: ", len(values_and_ops))
    for i, ops in values_and_ops:
        if i == target_value:
            print(i)
            print(ops)
            # break
