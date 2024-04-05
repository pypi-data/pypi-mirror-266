from functools import partial
import numpy as np
import operator
import einx
from .base import Backend


def is_leaf(key, x):
    return isinstance(x, (tuple, list, np.ndarray)) and all(
        isinstance(y, (int, np.integer)) for y in x
    )


def to_shape(shape):
    if isinstance(shape, np.ndarray):
        return tuple(shape.tolist())
    elif isinstance(shape, list):
        return tuple(shape)
    else:
        return shape


class Tensor:
    def __init__(self, shape):
        self.shape = to_shape(shape)

    @property
    def ndim(self):
        if self.shape is None:
            raise ValueError("Cannot get ndim of tensor with unknown shape")
        return len(self.shape)

    def __getitem__(self, key):
        return index(self, key, update=None, op="get_at")

    def __add__(self, other):
        return elementwise(self, other, op="add")

    def __radd__(self, other):
        return elementwise(other, self, op="add")

    def __sub__(self, other):
        return elementwise(self, other, op="subtract")

    def __rsub__(self, other):
        return elementwise(other, self, op="subtract")

    def __mul__(self, other):
        return elementwise(self, other, op="multiply")

    def __rmul__(self, other):
        return elementwise(other, self, op="multiply")

    def __truediv__(self, other):
        return elementwise(self, other, op="true_divide")

    def __rtruediv__(self, other):
        return elementwise(other, self, op="true_divide")

    def __floordiv__(self, other):
        return elementwise(self, other, op="floor_divide")

    def __rfloordiv__(self, other):
        return elementwise(other, self, op="floor_divide")

    def __div__(self, other):
        return elementwise(self, other, op="divide")

    def __rdiv__(self, other):
        return elementwise(other, self, op="divide")

    def __and__(self, other):
        return elementwise(self, other, op="logical_and")

    def __rand__(self, other):
        return elementwise(other, self, op="logical_and")

    def __or__(self, other):
        return elementwise(self, other, op="logical_or")

    def __ror__(self, other):
        return elementwise(other, self, op="logical_or")

    def __lt__(self, other):
        return elementwise(self, other, op="less")

    def __le__(self, other):
        return elementwise(self, other, op="less_equal")

    def __gt__(self, other):
        return elementwise(self, other, op="greater")

    def __ge__(self, other):
        return elementwise(self, other, op="greater_equal")

    def __eq__(self, other):
        return elementwise(self, other, op="equal")

    def __ne__(self, other):
        return elementwise(self, other, op="not_equal")


class Input(Tensor):
    def __init__(self, shape, index, original_type=None):
        super().__init__(shape)
        self.index = index
        self.original_type = original_type

    def __str__(self):
        return f"Input({self.shape})"

    def __hash__(self):
        return 712873 + hash(self.shape) + hash(self.original_type)

    def __eq__(self, other):
        return (
            isinstance(other, Input)
            and self.shape == other.shape
            and self.original_type == other.original_type
        )


class Op:
    def __init__(self, op, tracable):
        assert not isinstance(op, VmappedOp)
        self.op = op
        self.tracable = tracable

    @property
    def __name__(self):
        if "__name__" in dir(self.op):
            return self.op.__name__
        else:
            return str(self.op)

    @property
    def requires_dynamic_shape_check(self):
        return not self.tracable

    def __call__(self, *args, **kwargs):
        assert self.tracable
        if isinstance(self.op, str):
            x = tracer
            for name in self.op.split("."):
                x = getattr(x, name)
            op = x
        else:
            op = self.op
        return op(*args, **kwargs)


class OpApplication:
    def __init__(self, op, args=None, kwargs=None, output_shapes=None):
        if kwargs is None:
            kwargs = {}
        if args is None:
            args = []
        if not isinstance(op, (Op, VmappedOp)):
            op = Op(op, tracable=isinstance(op, str))
        assert not isinstance(op, Op) or (
            not op.tracable or isinstance(op.op, str)
        ), f"{op} {op.op}"
        self.op = op
        self.args = args
        self.kwargs = kwargs
        self.output_shapes = einx.tree_util.tree_map_with_key(
            lambda shape, key: tuple(int(i) for i in shape), output_shapes, is_leaf=is_leaf
        )
        self.output_tracers = einx.tree_util.tree_map_with_key(
            lambda shape, key: OpOutput(self, shape, key), self.output_shapes, is_leaf=is_leaf
        )
        assert "backend" not in self.kwargs


class OpOutput(Tensor):
    def __init__(self, application, shape, key):
        super().__init__(shape)
        self.application = application
        self.key = key


def drop_axis(shape, axis):
    if axis is None:
        return shape
    else:
        return shape[:axis] + shape[axis + 1 :]


class VmappedOp:
    def __init__(self, op, in_axes, out_axes, input_shapes, output_shapes):
        self.in_axes = in_axes
        self.out_axes = out_axes
        self.input_shapes = input_shapes
        self.output_shapes = output_shapes

        if not isinstance(op, VmappedOp):
            # Trace vmapped functions again
            if isinstance(op, Op):
                assert op.tracable
                op = op.op
            input_tracers = [Input(shape, i) for i, shape in enumerate(self.inner_input_shapes)]
            output_tracers = op(*input_tracers)
            op = Graph(output_tracers, args=input_tracers, kwargs={}, backend=einx.backend.tracer)
        self.op = op

    @property
    def tracable(self):
        return False

    @property
    def requires_dynamic_shape_check(self):
        return False

    @property
    def inner_input_shapes(self):
        return [drop_axis(shape, axis) for shape, axis in zip(self.input_shapes, self.in_axes)]

    @property
    def inner_output_shapes(self):
        return [drop_axis(shape, axis) for shape, axis in zip(self.output_shapes, self.out_axes)]

    def __call__(self, *args, **kwargs):
        return OpApplication(
            self, args=args, kwargs=kwargs, output_shapes=self.output_shapes
        ).output_tracers


class Scope:
    def __init__(self, backend, parent_scope=None):
        self.backend = backend
        self.parent_scope = parent_scope
        self.constants = [] if parent_scope is None else None
        self.locals = {}
        self.lines = []
        self.used_functions = set()

    @property
    def root_scope(self):
        scope = self
        while scope.parent_scope is not None:
            scope = scope.parent_scope
        return scope

    def __str__(self):
        string = ""
        string += f"# backend: einx.backend.{self.backend.name}\n"
        for const_name, value in self.root_scope.constants:
            string += f"# {const_name}: {str(type(value))} = {value}\n"
        string += "\n".join(self.lines)
        return string

    def exec(self, names):
        scope_globals = dict(self.constants)
        scope_globals["einx"] = einx
        scope_globals["partial"] = partial
        scope_globals["backend"] = self.backend
        scope_locals = {}
        exec("\n".join(self.lines), scope_globals, scope_locals)
        return einx.tree_util.tree_map(lambda name: scope_locals[name], names)

    def get_name_for(self, x):
        if id(x) in self.locals:
            return self.locals[id(x)]
        elif self.parent_scope is not None:
            return self.parent_scope.get_name_for(x)
        else:
            return None

    def name_exists(self, name):
        if name in self.locals.values():
            return True
        elif self.parent_scope is not None:
            return self.parent_scope.name_exists(name)
        else:
            return False

    def declare_local_name_for(self, x, prefix="x"):
        if x is None:

            def x():
                return 1  # Unique new object

        i = 0
        while self.name_exists(name := f"{prefix}{i}"):
            i += 1
        self.locals[id(x)] = name
        return name

    def define_function(self, graph):
        name = self.declare_local_name_for(graph, prefix="op")

        function_scope = Scope(self.backend, parent_scope=self)

        lines = []
        output = function_scope.eval(graph.output)
        params = [function_scope.eval(x) for x in graph.input_tracers] + [
            op + "=" + op for op in function_scope.used_functions
        ]
        lines.insert(
            0,
            f"def {name}({', '.join(params)}):",
        )
        for line in function_scope.lines:
            lines.append(f"    {line}")
        lines.append(f"    return {output}")

        self.lines.extend(lines)

        return name

    def eval(self, x):
        if (x_try := self.get_name_for(x)) is not None:
            return x_try

        if isinstance(x, Input):
            name = f"i{x.index}"
        elif isinstance(x, Graph):
            name = self.root_scope.define_function(x)
            self.used_functions.add(name)
        elif isinstance(x, Op):
            if isinstance(x.op, str):
                op = f"backend.{x.op}"
            else:
                if not callable(x.op):
                    raise TypeError(f"Expected callable, got {type(x.op)}")

                if x.op == einx.param.instantiate:
                    op = "einx.param.instantiate"
                else:
                    op = self.eval(x.op)
                    if self.backend == einx.backend.tracer:
                        wrapped_op = self.declare_local_name_for(None, prefix="op")
                        self.lines.append(f"{wrapped_op} = backend.op({op})")
                        op = wrapped_op
            name = op
        elif isinstance(x, OpApplication):
            if x.op.op == operator.getitem:
                # tensor[...]
                assert len(x.args) == 2 and len(x.kwargs) == 0
                tensor = self.eval(x.args[0])

                slices = x.args[1]
                if not isinstance(slices, tuple):
                    slices = (slices,)
                assert isinstance(slices, tuple)
                assert len(slices) > 0

                def slice_to_str(s):
                    if isinstance(s, slice):
                        x = ""
                        if s.start is not None:
                            x += str(s.start)
                        x += ":"
                        if s.stop is not None:
                            x += str(s.stop)
                        if s.step is not None:
                            x += ":" + str(s.step)
                        return x
                    else:
                        return self.eval(s)

                slices = ", ".join(slice_to_str(s) for s in slices)

                name = self.declare_local_name_for(x)

                line = f"{name} = {tensor}[" + slices + "]"
                self.lines.append(line)
            else:
                args = x.args
                kwargs = x.kwargs

                name = self.declare_local_name_for(x)

                if self.backend == einx.backend.tracer and not isinstance(x.op.op, str):
                    op = self.eval(x.op)

                    args = self.eval(args)
                    kwargs = self.eval(kwargs)

                    self.lines.append(
                        f"{name} = backend.apply({op}, args={args}, kwargs={kwargs}, "
                        f"output_shapes={self.eval(x.output_shapes)})"
                    )
                else:
                    op = self.eval(x.op)
                    args = [self.eval(a) for a in args] + [
                        f"{k}={self.eval(v)}" for k, v in kwargs.items()
                    ]
                    if op == "einx.param.instantiate":
                        args += ["backend=backend"]
                    args = ", ".join(args)

                    self.lines.append(f"{name} = {op}(" + args + ")")

                # Shape assertion
                if self.backend != einx.backend.tracer and x.op.requires_dynamic_shape_check:

                    def assertion(tracer, shape):
                        self.lines.append(f"assert {self.eval(tracer)}.shape == {self.eval(shape)}")

                    einx.tree_util.tree_map(assertion, x.output_tracers, x.output_shapes)
        elif isinstance(x, OpOutput):
            name = self.eval(x.application)
            for k in x.key:
                name += f"[{self.eval(k)}]"
        elif isinstance(x, VmappedOp):
            old_name = self.eval(x.op)
            name = self.declare_local_name_for(None, prefix="op")
            if self.backend == einx.backend.tracer:
                self.lines.append(
                    f"{name} = backend.vmap({old_name}, in_axes={self.eval(x.in_axes)}, "
                    f"out_axes={self.eval(x.out_axes)}, input_shapes={self.eval(x.input_shapes)}, "
                    f"output_shapes={self.eval(x.output_shapes)})"
                )
            else:
                self.lines.append(
                    f"{name} = backend.vmap({old_name}, in_axes={self.eval(x.in_axes)}, "
                    f"out_axes={self.eval(x.out_axes)})"
                )
        elif isinstance(x, str):
            name = f'"{x}"'
        elif isinstance(x, tuple):
            name = "(" + ", ".join(self.eval(a) for a in x) + ("," if len(x) == 1 else "") + ")"
        elif isinstance(x, list):
            name = "[" + ", ".join(self.eval(a) for a in x) + "]"
        elif isinstance(x, dict):
            name = "{" + ", ".join(f'"{k}": {self.eval(v)}' for k, v in x.items()) + "}"
        elif isinstance(x, (int, float, np.integer, np.floating)):
            name = str(x)
        elif isinstance(x, slice):
            if x.step is not None:
                return f"slice({self.eval(x.start)}, {self.eval(x.stop)}, {self.eval(x.step)})"
            elif x.stop is not None:
                return f"slice({self.eval(x.start)}, {self.eval(x.stop)})"
            else:
                return f"slice({self.eval(x.start)})"
        elif x is None:
            name = "None"
        else:
            # Add to root scope as constant
            name = self.declare_local_name_for(x, prefix="const")
            self.root_scope.constants.append((name, x))
            self.root_scope.locals[id(x)] = name
            return name  # Don't add to locals

        assert name is not None
        self.locals[id(x)] = name
        return name


def optimize(output, backend):
    new_nodes = {}

    def _optimize(node):
        if id(node) in new_nodes:
            return new_nodes[id(node)]

        if isinstance(node, OpApplication):
            if (
                node.op.op == "reshape"
                and isinstance(node.args[0], OpOutput)
                and node.args[0].application.op.op == "reshape"
            ):
                # Merge consecutive reshape ops
                new_node = OpApplication(
                    "reshape",
                    args=[node.args[0].application.args[0], node.output_shapes],
                    output_shapes=node.output_shapes,
                )
            elif (
                node.op.op == "to_tensor"
                and isinstance(node.args[0], OpOutput)
                and node.args[0].application.op.op == "to_tensor"
            ):
                # Merge consecutive to_tensor ops
                new_node = _optimize(node.args[0].application)
            else:
                new_node = OpApplication(
                    node.op,
                    args=[_optimize(a) for a in node.args],
                    kwargs={k: _optimize(v) for k, v in node.kwargs.items()},
                    output_shapes=node.output_shapes,
                )
        elif isinstance(node, OpOutput):
            if (
                node.application.op.op == "to_tensor"
                and backend != einx.backend.tracer
                and isinstance(node.application.args[0], Input)
                and node.application.args[0].original_type is not None
                and issubclass(node.application.args[0].original_type, backend.tensor)
            ):
                # Skip to_tensor op if tensor already has right type
                new_node = _optimize(node.application.args[0])
            elif (
                node.application.op.op == "reshape" and node.application.args[0].shape == node.shape
            ):
                # Skip reshape op if tensor already has right shape
                new_node = _optimize(node.application.args[0])
            elif (
                node.application.op.op == "broadcast_to"
                and node.application.args[0].shape == node.shape
            ):
                # Skip broadcast_to op if tensor already has right shape
                new_node = _optimize(node.application.args[0])
            elif node.application.op.op == "transpose" and list(node.application.args[1]) == list(
                range(len(node.shape))
            ):
                # Skip transpose op if permutation is identity
                new_node = _optimize(node.application.args[0])
            else:
                new_node = OpOutput(_optimize(node.application), node.shape, node.key)
        elif isinstance(node, VmappedOp):
            new_node = VmappedOp(
                _optimize(node.op),
                node.in_axes,
                node.out_axes,
                node.input_shapes,
                node.output_shapes,
            )
        elif isinstance(node, Op):
            new_node = Op(_optimize(node.op), tracable=node.tracable)
        elif isinstance(node, Input):
            new_node = node
        elif isinstance(node, Graph):
            raise AssertionError("TODO")
        elif isinstance(node, list):
            new_node = [_optimize(x) for x in node]
        elif isinstance(node, tuple):
            new_node = tuple(_optimize(x) for x in node)
        elif isinstance(node, dict):
            new_node = {k: _optimize(v) for k, v in node.items()}
        else:
            new_node = node

        new_nodes[id(node)] = new_node
        return new_node

    new_output = _optimize(output)
    return new_output


class Graph:
    def __init__(self, output, args, kwargs, backend):
        assert any(
            isinstance(x, Tensor) for x in einx.tree_util.tree_flatten(output)
        ), "No output value is traced"
        self.output = optimize(output, backend)
        self.args = args
        self.kwargs = kwargs
        self.backend = backend

        # Get input tracers
        self.input_tracers = []
        index = 0

        def map(x):
            nonlocal index
            if isinstance(x, Input):
                self.input_tracers.append(x)
                assert x.index == index
                index += 1
            return x

        einx.tree_util.tree_map(map, args)
        einx.tree_util.tree_map(map, kwargs)

        # Generate Python code for the graph
        self.scope = Scope(backend)
        name = self.scope.eval(self)

        # Just-in-time compile the graph
        self.op = self.scope.exec(name)

    def __call__(self, *tracer_values):
        return self.op(*tracer_values)

    def __str__(self):
        return str(self.scope)


def elementwise(*args, op):
    shape = None
    for a in args:
        if "shape" in dir(a):
            if shape is None:
                shape = a.shape
            else:
                shape2 = a.shape
                while len(shape) < len(shape2):
                    shape = (1,) + shape
                while len(shape2) < len(shape):
                    shape2 = (1,) + shape2
                shape = np.maximum(shape, shape2)
    return OpApplication(op, args=args, output_shapes=shape).output_tracers


def reduce(tensor, axis=None, *, op=None, **kwargs):
    keepdims = kwargs.get("keepdims", False)
    if axis is None:
        shape = [1] * len(tensor.shape)
    else:
        axes = [axis] if isinstance(axis, int) else axis
        shape = list(tensor.shape)
        if keepdims:
            for a in axes:
                shape[a] = 1
        else:
            for a in sorted(axes, reverse=True):
                del shape[a]
        kwargs = {**kwargs, **{"axis": axis}}
    return OpApplication(op, args=[tensor], kwargs=kwargs, output_shapes=shape).output_tracers


def map(tensor, axis, op, *args, **kwargs):
    return OpApplication(
        op, args=[tensor], kwargs={**kwargs, **{"axis": axis}}, output_shapes=tensor.shape
    ).output_tracers


def index(tensor, coordinates, update=None, op=None):
    if update is None:
        coordinates2 = (coordinates,) if not isinstance(coordinates, tuple) else coordinates
        if len(coordinates2) > len(tensor.shape):
            raise ValueError(f"Too many indices for tensor of dimension {len(tensor.shape)}")

        def is_multidim(c):
            if isinstance(c, (slice, int, np.integer)):
                return False
            elif isinstance(c, list):
                return True
            else:
                return c.ndim > 0

        if any(is_multidim(c) for c in coordinates2):
            # Got multi-dimensional indices

            # Find front and back slices
            front_slices = []
            back_slices = []
            i = 0
            is_front = True
            for i in range(tensor.ndim):
                if is_front:
                    if isinstance(coordinates2[i], slice):
                        front_slices.append(i)
                    else:
                        is_front = False
                else:
                    if isinstance(coordinates2[i], slice):
                        back_slices.append(i)

            # Broadcast coordinates expressions
            def broadcast(dims):
                dims = np.asarray(list({int(i) for i in dims}))
                assert np.all(dims > 0)
                if len(dims) > 2 or len(dims) == 2 and np.amin(dims) > 1:
                    raise ValueError("Cannot broadcast coordinates")
                return np.amax(dims)

            shapes = [c.shape for c in coordinates2 if not isinstance(c, slice)]
            if len({len(s) for s in shapes}) != 1:
                raise ValueError("Expected all coordinates to have same number of dimensions")
            shapes = np.asarray(shapes)
            shape = [broadcast(shapes[:, i]) for i in range(shapes.shape[1])]

            # Prepend and append slices
            shape = tuple(
                [tensor.shape[i] for i in front_slices]
                + shape
                + [tensor.shape[i] for i in back_slices]
            )
        else:
            output_shape = []
            input_shape = tensor.shape
            for s in coordinates:
                if isinstance(s, (int, np.integer)):
                    input_shape = input_shape[1:]
                elif isinstance(s, slice):
                    start, stop, step = s.indices(input_shape[0])
                    output_shape.append((stop - start) // step)
                    input_shape = input_shape[1:]
                elif s is None:
                    output_shape.append(1)
                elif isinstance(s, Tensor) and s.ndim == 0:
                    input_shape = input_shape[1:]
                else:
                    raise TypeError(f"Invalid coordinate type: {type(s)}")
            shape = tuple(output_shape) + tuple(input_shape)

        return OpApplication(op, args=[tensor, coordinates], output_shapes=shape).output_tracers
    else:
        return OpApplication(
            op, args=[tensor, coordinates, update], output_shapes=tensor.shape
        ).output_tracers


class tracer(Backend):
    Input = Input
    Graph = Graph

    def to_tensor(tensor):
        if isinstance(tensor, Tensor):
            return OpApplication(
                "to_tensor", args=[tensor], output_shapes=tensor.shape
            ).output_tracers
        else:
            return OpApplication(
                "to_tensor", args=[tensor], output_shapes=einx.param.get_shape(tensor)
            ).output_tracers

    tensor = Tensor
    name = "tracer"

    def op(op, tracable=False):
        if op is None:
            raise TypeError("op cannot be None")
        if isinstance(op, (Op, VmappedOp)):
            return op
        elif isinstance(op, str):
            return Op(op, tracable=True)
        else:
            return Op(op, tracable=tracable)

    @classmethod
    def apply(backend, op, args, kwargs, output_shapes):
        op = backend.op(op)
        if op.tracable:
            x = op(*args, **kwargs)

            got_output_shapes = einx.tree_util.tree_map(lambda x: x.shape, x)

            def assertion(tensor, shape):
                if tuple(tensor.shape) != tuple(shape):
                    raise ValueError(
                        f"Expected shapes {output_shapes} from custom op, got {got_output_shapes}"
                    )

            einx.tree_util.tree_map(assertion, x, output_shapes)
            return x
        else:
            return OpApplication(
                op, args=args, kwargs=kwargs, output_shapes=output_shapes
            ).output_tracers

    def cast(tensor, dtype):
        return OpApplication(
            "cast", args=[tensor], kwargs={"dtype": dtype}, output_shapes=tensor.shape
        ).output_tracers

    def reshape(tensor, shape):
        return OpApplication("reshape", args=[tensor, shape], output_shapes=shape).output_tracers

    def transpose(tensor, perm):
        shape = [tensor.shape[i] for i in perm]
        return OpApplication("transpose", args=[tensor, perm], output_shapes=shape).output_tracers

    def broadcast_to(tensor, shape):
        return OpApplication(
            "broadcast_to", args=[tensor, shape], output_shapes=shape
        ).output_tracers

    def einsum(eq, *tensors):
        exprs = eq.split("->")[0].split(",")
        if len(exprs) != len(tensors):
            raise ValueError(f"Expected {len(exprs)} tensors, got {len(tensors)}")
        values = {}
        for i, (expr, tensor) in enumerate(zip(exprs, tensors)):
            expr = expr.strip().replace(" ", "")
            if len(expr) != len(tensor.shape):
                raise ValueError(
                    f"Expected {len(expr)} axes, got {len(tensor.shape)} for {i}-th "
                    "(zero-based) input tensor"
                )
            for axis, value in zip(expr, tensor.shape):
                if axis in values:
                    if values[axis] != value:
                        raise ValueError(
                            f"Got conflicting values for axis {axis}: {values[axis]} and {value}"
                        )
                else:
                    values[axis] = value
        expr_out = eq.split("->")[-1].strip().replace(" ", "")
        shape_out = tuple(values[axis] for axis in expr_out)
        return OpApplication("einsum", args=[eq, *tensors], output_shapes=shape_out).output_tracers

    def swapaxes(a, axis1, axis2):
        shape = list(a.shape)
        shape[axis1], shape[axis2] = shape[axis2], shape[axis1]
        return OpApplication("swapaxes", args=[a, axis1, axis2], output_shapes=shape).output_tracers

    def arange(n, dtype="int32"):
        return OpApplication(
            "arange", args=[n], kwargs={"dtype": dtype}, output_shapes=(n,)
        ).output_tracers

    def stack(tensors, axis):
        shape = list(tensors[0].shape)
        shape.insert(axis, len(tensors))
        return OpApplication("stack", args=[tensors, axis], output_shapes=shape).output_tracers

    def concatenate(tensors, axis):
        shape = list(tensors[0].shape)
        shape[axis] = sum(tensor.shape[axis] for tensor in tensors)
        return OpApplication(
            "concatenate", args=[tensors, axis], output_shapes=shape
        ).output_tracers

    def zeros(shape, dtype="float32"):
        return OpApplication("zeros", args=[shape, dtype], output_shapes=shape).output_tracers

    def ones(shape, dtype="float32"):
        return OpApplication("ones", args=[shape, dtype], output_shapes=shape).output_tracers

    add = partial(elementwise, op="add")
    subtract = partial(elementwise, op="subtract")
    multiply = partial(elementwise, op="multiply")
    true_divide = partial(elementwise, op="true_divide")
    floor_divide = partial(elementwise, op="floor_divide")
    divide = partial(elementwise, op="divide")
    logical_and = partial(elementwise, op="logical_and")
    logical_or = partial(elementwise, op="logical_or")
    where = partial(elementwise, op="where")
    less = partial(elementwise, op="less")
    less_equal = partial(elementwise, op="less_equal")
    greater = partial(elementwise, op="greater")
    greater_equal = partial(elementwise, op="greater_equal")
    equal = partial(elementwise, op="equal")
    not_equal = partial(elementwise, op="not_equal")
    maximum = partial(elementwise, op="maximum")
    minimum = partial(elementwise, op="minimum")

    sum = partial(reduce, op="sum")
    mean = partial(reduce, op="mean")
    var = partial(reduce, op="var")
    std = partial(reduce, op="std")
    prod = partial(reduce, op="prod")
    count_nonzero = partial(reduce, op="count_nonzero")
    any = partial(reduce, op="any")
    all = partial(reduce, op="all")
    min = partial(reduce, op="min")
    max = partial(reduce, op="max")
    logsumexp = partial(reduce, op="logsumexp")

    get_at = partial(index, op="get_at")
    set_at = partial(index, op="set_at")
    add_at = partial(index, op="add_at")
    subtract_at = partial(index, op="subtract_at")

    flip = partial(map, op="flip")
    roll = partial(map, op="roll")
    softmax = partial(map, op="softmax")
    log_softmax = partial(map, op="log_softmax")

    def sqrt(tensor):
        return OpApplication("sqrt", args=[tensor], output_shapes=tensor.shape).output_tracers

    def rsqrt(tensor):
        return OpApplication("rsqrt", args=[tensor], output_shapes=tensor.shape).output_tracers

    def square(tensor):
        return OpApplication("square", args=[tensor], output_shapes=tensor.shape).output_tracers

    def allclose(a, b):
        return OpApplication("allclose", args=[a, b], shape=()).output_tracers

    def vmap(op, in_axes, out_axes, input_shapes, output_shapes):
        return VmappedOp(op, in_axes, out_axes, input_shapes, output_shapes)

    class random:
        def bernoulli(rng, p, shape):
            return OpApplication(
                "random.bernoulli", args=[rng, p, shape], output_shapes=shape
            ).output_tracers
