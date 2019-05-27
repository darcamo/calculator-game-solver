"""Module docstring"""

# pylint: disable=C0111
# pylint: disable=W0212
# pylint: disable=R0913

import copy
import unittest
import operations as op


class Node:
    def __init__(self, value, current_op, available_ops, num_remaining_moves,
                 parent=None, memory=None, warp=None):
        """
        data : tuple[int, list, list]
        value : int
            The current value
        current_op : A subclass of op.Operation
            The operation that was applied to get the current value.
        available_ops : list[op.Operation]
           The list of operations that this node can apply to get child nodes.
        num_remaining_moves : int
            Number remaining moves (children are only created if
            num_remaining_moves > 0)
        parent : Node
            The parent Node
        memory : int
            Valued stored in the last call to the StorageAction. If not
            provided and parent was provided then it will be taken from parent.
        warp : op.WarpAction
            Warp action to be called after every action. Note that the warp
            action does not decrement the number of remaining moves.
        """
        self._value = value
        self._current_op = current_op
        self._available_ops = available_ops

        self._num_remaining_moves = num_remaining_moves

        self._children = []
        self._parent = parent

        self._memory = memory
        self._warp = warp

        # If memory was not provided but parent was provided, then we take the
        # memory from parent
        if parent is not None and memory is None:
            self._memory = parent._memory

    def __repr__(self):
        return (f"Node(value={self._value},"
                f"current_op={self._current_op},"
                f"num_children={len(self._children)},"
                f"rem_moves={self._num_remaining_moves},"
                f"ops={self._available_ops})")

    @property
    def value(self):
        return self._value

    @property
    def num_remaining_moves(self):
        return self._num_remaining_moves

    @property
    def parent(self):
        return self._parent

    @property
    def current_op(self):
        return self._current_op

    @staticmethod
    def apply_operation_and_create_child(node, operation):
        """Apply a Operation to the node and create a new node as the result

        Parameters
        ----------
        node : Node
            The Node object to apply the operation to
        operation : op.Operation
            The operation to apply to the Node object

        Returns
        -------
        Node
            The node resulting from applying `operation` to `node`
        """
        # __init__(self, value, current_op, available_ops, num_remaining_moves,
        # parent=None)
        parent = node
        memory = None
        num_remaining_moves = node.num_remaining_moves - 1
        available_ops = node._available_ops
        warp = node._warp

        if isinstance(operation, op.ModifyButtons_AddValue):
            available_ops = [copy.copy(i) for i in node._available_ops
                             if i is not operation]
            mb = op.ModifyButtons_AddValue(available_ops, operation._value)
            available_ops.append(mb)
            value = mb.apply(node.value)
        elif isinstance(operation, op.StorageAction):
            if node.value == node._memory:
                raise ValueError("Can't store the same value")
            value = node.value
            num_remaining_moves = node.num_remaining_moves
            memory = value

        elif isinstance(operation, op.RetrieveAction):
            value = op.add_digits(node.value, node._memory)
        else:
            value = operation.apply(node.value)

        if warp is not None:
            value = warp.apply(value)

        return Node(value, operation, available_ops, num_remaining_moves,
                    parent, memory, warp=warp)

    def create_children(self):
        if self._num_remaining_moves > 0:
            for current_op in self._available_ops:
                try:
                    child = Node.apply_operation_and_create_child(
                        self, current_op)
                    self._children.append(child)
                except ValueError:
                    pass

        for child in self._children:
            child.create_children()


def find_solution_node_in_tree(current_node, target_value):
    if current_node.num_remaining_moves == 0:
        if current_node.value == target_value:
            return current_node
        return None

    for child in current_node._children:
        value = find_solution_node_in_tree(child, target_value)
        if value is not None:
            return value
    return None


def parse_operations_until_node(node):
    operations = []

    while node is not None and node.current_op is not None:
        operations.append(node.current_op.name)
        node = node.parent

    return list(reversed(operations))


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
        except ValueError:
            pass
    return result
    # return [(op.apply(value), current_ops + [op]) for op in operations]


# xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

class TestSolver(unittest.TestCase):
    @staticmethod
    def solve(start_value, target_value, num_moves, operations, warp=None):
        root = Node(value=start_value, current_op=None,
                    available_ops=operations, num_remaining_moves=num_moves,
                    warp=warp)
        root.create_children()

        n = find_solution_node_in_tree(root, target_value)
        solution = parse_operations_until_node(n)
        return solution

    def test_level_127(self):
        start_value = -1
        target_value = 2020
        num_moves = 8
        operations = [op.MultiplyX(3),
                      op.SumX(2),
                      op.SumX(8),
                      op.Mirror(),
                      op.Reverse()]
        solution = self.solve(start_value, target_value, num_moves, operations)
        self.assertEqual(solution,
                         ['sum with 8', 'multiply by 3', 'reverse',
                          'sum with 8', 'mirror', 'sum with 2', 'sum with 8',
                          'sum with 8'])

    def test_level_139(self):
        start_value = 5
        target_value = 41
        num_moves = 4

        operations = [op.MultiplyX(3),
                      op.SumX(4),
                      op.SumX(8)]
        mb = op.ModifyButtons_AddValue(operations, 2)
        operations.append(mb)
        solution = self.solve(start_value, target_value, num_moves, operations)
        self.assertEqual(
            solution,
            ['[+]2', 'multiply by 5', 'sum with 6', 'sum with 10'])

    def test_level_142(self):
        start_value = 1
        target_value = 1111
        num_moves = 2

        storage = op.StorageAction()
        retrieve = op.RetrieveAction()

        operations = [storage, retrieve]
        solution = self.solve(start_value, target_value, num_moves, operations)
        self.assertEqual(solution, ['Store', 'Retrieve', 'Store', 'Retrieve'])

    def test_level_149(self):
        start_value = 15
        target_value = 16
        num_moves = 4

        storage = op.StorageAction()
        retrieve = op.RetrieveAction()

        operations = [
            op.SumDigits(),
            op.Replace(11, "33"),
            op.Reverse(),
            storage,
            retrieve,
        ]
        solution = self.solve(start_value, target_value, num_moves, operations)
        self.assertEqual(
            solution,
            ['Store', 'reverse', 'Retrieve', 'Replace 11 with 33', 'Sum'])

    def test_solution_159(self):
        start_value = 21
        target_value = 12
        num_moves = 3

        operations = [
            op.SumX(-7),
            op.MultiplyX(5),
            op.Inv10EachDigit()
        ]
        solution = self.solve(start_value, target_value, num_moves, operations)
        self.assertEqual(solution, ['multiply by 5', 'sum with -7', 'Inv10'])

    def test_solution_180(self):
        # This level is the first one with Warp
        start_value = 99
        target_value = 10
        num_moves = 3

        operations = [
            op.AddDigits(1),
            op.SumX(-1),
        ]

        warp = op.WarpAction(2, 0)

        solution = self.solve(start_value, target_value, num_moves, operations,
                              warp)
        self.assertEqual(solution, ['Add digit 1', 'Add digit 1', 'sum with -1'])


if __name__ == '__main__1':
    unittest.main()


if __name__ == '__main__':
    # xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    # MODIFY THE VALUES HERE

    start_value = 3002
    target_value = 3507
    num_moves = 6

    # Note that when there is the memory button, you need to add both store and
    # retrieve actions to `operations`
    storage = op.StorageAction()
    retrieve = op.RetrieveAction()

    # Uncomment and modify the necessary buttons according to the level
    operations = [
        # op.SumX(6),
        # op.MultiplyX(3),
        # op.DivideX(2),
        # op.ShiftLeft(),
        op.CircularShiftRight(),
        # op.InvertSign(),
        op.AddDigits(7),
        # op.SumDigits(),
        op.Replace(3, "5"),
        # op.Mirror(),
        # op.CircularShiftRight(),
        # op.Reverse(),
        # op.SumDigits(),
        # storage,
        # retrieve,
        # op.SumX(2),
        # op.Mirror(),
        # op.Reverse()
        op.Inv10EachDigit()
    ]

    # # If there is the button that modify other buttons, uncomment the following two lined.
    # mb = op.ModifyButtons_AddValue(operations, 1)
    # operations.append(mb)

    warp = None
    # Uncomment the line below if the level has the portls
    #
    # The first argument is the index of the enter portal while the second
    # argument is the index of the end portal (usually zero, since it is the
    # first digit)
    warp = op.WarpAction(4, 0)
    # xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

    # There is no need to change anything below
    root = Node(value=start_value, current_op=None, available_ops=operations,
                num_remaining_moves=num_moves, warp=warp)
    root.create_children()

    n = find_solution_node_in_tree(root, target_value)
    operations = parse_operations_until_node(n)
    print(operations)
