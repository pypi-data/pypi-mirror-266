# Copyright 2022 DeepMind Technologies Limited. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""K-FAC tracing functionality for functions needed for curvature estimation."""
import functools
from typing import Any, Callable, Sequence, TypeVar, Tuple, Union, Dict, List

import jax
import jax.numpy as jnp
from kfac_jax._src import layers_and_loss_tags as tags
from kfac_jax._src import loss_functions
from kfac_jax._src import tag_graph_matcher as tgm
from kfac_jax._src import utils
from typing_extensions import TypeAlias

# Types for annotations
Array = utils.Array
Shape = utils.Shape
Params = utils.Params
FuncArgs = utils.FuncArgs
FuncOuts = utils.FuncOuts
Var = jax.core.Var
LossFunction = loss_functions.LossFunction
LossFunctionInputs = loss_functions.LossFunctionInputs

T = TypeVar("T")
# J = TypeVar("J", jax.core.Jaxpr, jax.core.ClosedJaxpr)
ProcJaxpr: TypeAlias = "ProcessedJaxpr"
TaggedFunction = Callable[..., Tuple[LossFunction, ...]]
FuncWithTags = Callable[..., Any]

FunctionTransformation = Callable[..., Union[ProcJaxpr, T]]
TransformedFunction = Callable[..., Union[ProcJaxpr, T]]

LossTagsVjp = Tuple[
    Tuple[LossFunction, ...],
    Callable[[Sequence[LossFunctionInputs]], Params]
]
LossTagsJvp = Tuple[
    Tuple[LossFunction, ...],
    Tuple[LossFunctionInputs, ...],
]
LayerTagVjp = Tuple[
    Tuple[LossFunction, ...],
    Callable[[Tuple[LossFunctionInputs, ...]], Tuple[Dict[str, Array], ...]]
]
JaxprOrClosedJaxpr = Union[jax.core.Jaxpr, jax.core.ClosedJaxpr]


def shape_and_type(x: Array) -> Tuple[Shape, jnp.dtype]:
  """Returns the shape and type of the given array."""
  return x.shape, x.dtype


def make_cache_key(
    func_args: FuncArgs,
    *args: Any
) -> Tuple[utils.PyTreeDef, Tuple[Tuple[Shape, jnp.dtype], ...]]:
  """Creates a key for caching Jax function arguments."""

  args_flat, tree_structure = jax.tree_util.tree_flatten((func_args, args))

  return tree_structure, tuple(map(shape_and_type, args_flat))


def extract_tags(
    jaxpr: jax.core.Jaxpr
) -> Tuple[Tuple[tags.LayerTagEqn, ...], Tuple[tags.LossTagEqn, ...]]:
  """Extracts the layer and the loss tags from the given Jaxpr."""

  return (tuple(eqn for eqn in jaxpr.eqns
                if isinstance(eqn.primitive, tags.LayerTag)),
          tuple(eqn for eqn in jaxpr.eqns
                if isinstance(eqn.primitive, tags.LossTag)))


def order_layer_tags(
    params_vars_flat: Sequence[Var],
    layer_tags: Sequence[tags.LayerTagEqn],
    allow_left_out_params: bool = False,
) -> Tuple[Tuple[tags.LayerTagEqn, ...], Tuple[Tuple[int, ...], ...]]:
  """Sorts the layer tags based on the index of the parameters they contain.

  Args:
    params_vars_flat: A sequence of all parameter variables.
    layer_tags: A sequence of all layer tags.
    allow_left_out_params: Whether to raise an error if there are any parameter
      variables which are not part of a layer tag.

  Returns:
    A pair of tuples ``(layer_tags, tags_indices)``, where ``layer_tags`` has
    the ordered sequence of the input ``layer_tags`` and ``tags_indices``
    contains a sequence of tuples, where each tuple has the indices of the
    parameters associated with the corresponding layer tag.
  """
  tags_param_indices = []
  used_indices = set()

  for eqn in layer_tags:

    # Collect the equation parameter indices
    _, _, tag_vars = eqn.primitive.split_all_inputs(eqn.invars)
    vars_indices = tuple(params_vars_flat.index(v) for v in tag_vars)

    if any(i in used_indices for i in vars_indices):
      raise ValueError("Reusing variable in a second block.")

    used_indices = used_indices.union(vars_indices)
    tags_param_indices.append(vars_indices)

  left_out_indices = set(range(len(params_vars_flat))) - used_indices

  if left_out_indices and not allow_left_out_params:
    raise ValueError("The following parameter indices were not assigned a "
                     f"block: {left_out_indices}.")

  if not layer_tags:
    return (), ()
  else:
    # Sort by the vars minimum index
    sorted_index_and_blocks = sorted(zip(layer_tags, tags_param_indices),
                                     key=lambda x: min(x[1]))
    return tuple(zip(*sorted_index_and_blocks))


class ProcessedJaxpr(utils.Finalizable):
  """A wrapper around Jaxpr, with useful additional data.

  Attributes:
    jaxpr: The original Jaxpr that is being wrapped.
    consts: The constants returned from the tracing of the original Jaxpr.
    in_tree: The PyTree structure of the inputs to the function that the
      original Jaxpr has been created from.
    params_index: Specifies, which inputs to the function are to be considered
      a parameter variable. Specifically - ``inputs[params_index]``.
    loss_tags: A tuple of all of the loss tags in the original Jaxpr.
    layer_tags: A sorted tuple of all of the layer tags in the original Jaxpr.
      The sorting order is based on the indices of the parameters associated
      with each layer tag.
    layer_indices: A sequence of tuples, where each tuple has the indices of the
      parameters associated with the corresponding layer tag.
  """

  def __init__(
      self,
      jaxpr: jax.core.Jaxpr,
      consts: Sequence[Any],
      in_tree: utils.PyTreeDef,
      params_index: int,
      allow_left_out_params: bool = False,
    ):
    """Initializes the instance.

    Args:
      jaxpr: The raw Jaxpr.
      consts: The constants needed for evaluation of the raw Jaxpr.
      in_tree: The PyTree structure of the inputs to the function that the
        ``jaxpr`` has been created from.
      params_index: Specifies, which inputs to the function are to be considered
        a parameter variable. Specifically - ``inputs[params_index]``.
      allow_left_out_params: Whether to raise an error if any of the parameter
        variables is not included in any layer tag.
    """
    super().__init__()
    self.jaxpr = jaxpr
    self.consts = consts
    self.in_tree = in_tree
    self.params_index = params_index
    self.layer_tags, self.loss_tags = extract_tags(jaxpr)
    self.layer_tags, self.layer_indices = order_layer_tags(
        params_vars_flat=self.params_vars_flat,
        layer_tags=self.layer_tags,
        allow_left_out_params=allow_left_out_params,
    )
    self.finalize()

  @property
  def in_vars_flat(self) -> List[Var]:
    """A flat list of all of the abstract input variables."""
    return self.jaxpr.invars

  @property
  def in_vars(self) -> utils.PyTree[Var]:
    """The abstract input variables, as an un-flatten structure."""
    return jax.tree_util.tree_unflatten(self.in_tree, self.in_vars_flat)

  @property
  def params_vars(self) -> utils.PyTree[Var]:
    """The abstract parameter variables, as an un-flatten structure."""
    return self.in_vars[self.params_index]

  @property
  def params_vars_flat(self) -> List[Var]:
    """A flat list of all abstract parameter variables."""
    return jax.tree_util.tree_leaves(self.params_vars)

  @property
  def params_tree(self) -> utils.PyTreeDef:
    """The PyTree structure of the parameter variables."""
    return jax.tree_util.tree_structure(self.params_vars)

  @classmethod
  def make_from_func(
      cls,
      func: utils.Func,
      func_args: FuncArgs,
      params_index: int = 0,
      auto_register_tags: bool = True,
      allow_left_out_params: bool = False,
      ** auto_registration_kwargs: Any,
  ) -> ProcJaxpr:
    """Constructs a :class:`~ProcessedJaxpr` from a the given function.

    Args:
      func: The model function, which will be traced.
      func_args: Function arguments to use for tracing.
      params_index: The variables from the function arguments which are at this
        index (e.g. ``func_args[params_index]``) are to be considered model
        parameters.
      auto_register_tags: Whether to run an automatic layer registration on the
        function (e.g. :func:`~auto_register_tags`).
      allow_left_out_params: If this is set to ``False`` an error would be
        raised if there are any model parameters that have not be assigned to a
        layer tag.
      **auto_registration_kwargs: Any additional keyword arguments, to be passed
        to the automatic registration pass.

    Returns:
      A :class:`~ProcessedJaxpr` representing the model function.
    """
    func_args = tuple(func_args)

    if auto_register_tags:
      func = tgm.auto_register_tags(
          func=func,
          func_args=func_args,
          params_index=params_index,
          **auto_registration_kwargs)

    typed_jaxpr = jax.make_jaxpr(func)(*func_args)
    jaxpr, consts = typed_jaxpr.jaxpr, typed_jaxpr.literals

    in_tree = jax.tree_util.tree_structure(func_args)

    return ProcessedJaxpr(
        jaxpr=jaxpr,
        consts=consts,
        in_tree=in_tree,
        params_index=params_index,
        allow_left_out_params=allow_left_out_params,
    )

  def __eq__(self, other: ProcJaxpr) -> bool:
    """Compares two ProcessedJaxpr instances by tree structure."""

    # Verify whether input trees are equivalent
    if self.in_tree != other.in_tree:
      return False

    # Verify whether layer indices are equivalent
    if len(self.layer_indices) != len(other.layer_indices):
      return False

    for ref_l_index, l_index in zip(self.layer_indices, other.layer_indices):

      if len(ref_l_index) != len(l_index):
        return False

      if any(p_i != p_j for p_i, p_j in zip(ref_l_index, l_index)):
        return False

    # Verify layer tags are equivalent
    if len(self.layer_tags) != len(other.layer_tags):
      return False

    if any(ref_tag.primitive != tag.primitive
           for ref_tag, tag in zip(self.layer_tags, other.layer_tags)):
      return False

    # Verify whether parameter shapes are equivalent
    if any(p_i.aval.shape != p_j.aval.shape  # pytype: disable=attribute-error  # always-use-property-annotation
           for p_i, p_j in zip(self.params_vars_flat, other.params_vars_flat)):
      return False

    return True


def cached_transformation(
    func: utils.Func,
    transformation: FunctionTransformation[T],
    params_index: int = 0,
    auto_register_tags: bool = True,
    allow_left_out_params: bool = False,
    allow_no_losses: bool = False,
    raise_error_on_diff_jaxpr: bool = True,
    **auto_registration_kwargs: Any,
) -> TransformedFunction[T]:
  """Caches ``transformation(preprocessed_jaxpr, func_args, *args)``.

  The caching mechanism uses the ``func_args`` PyTree, dtypes and shapes for
  hashing.

  Args:
    func: The main model function, which will be transformed.
    transformation: The actual transformation of ``func``.
    params_index: The variables from the function arguments which are at this
      index (e.g. ``func_args[params_index]``) are to be considered model
      parameters.
    auto_register_tags: Whether to run an automatic layer registration on the
      function (e.g. :func:`~auto_register_tags`).
    allow_left_out_params: If this is set to ``False`` an error would be raised
      if there are any model parameters that have not be assigned to a layer
      tag.
    allow_no_losses: If this is set to ``False`` an error would be raised if no
      registered losses have been found when tracing the function.
    raise_error_on_diff_jaxpr: Whether to raise an exception if the function has
      been traced before, with different arguments, and the new Jaxpr graph
      differs in more than just the shapes and dtypes of the Jaxpr equations.
    **auto_registration_kwargs: Any additional keyword arguments, to be passed
      to the automatic registration pass.

  Returns:
    A function with a signature ``f(func_args, *args, return_only_jaxpr)`` which
    evaluates the transformation of ``func`` at ``func_args``. The extra
    ``args`` are any additional array arguments passed to the transformation,
    while the last flag indicates whether to just return the
    :class:`~ProcessedJaxpr` instead of the transformation output.
  """
  cache = {}

  @functools.wraps(transformation)
  def wrapped_transformation(
      func_args: FuncArgs,
      *args: Any,
      return_only_jaxpr: bool = False,
  ) -> Union[ProcessedJaxpr, T]:
    # Construct a key and check cache for hits
    key = make_cache_key(func_args)
    jaxpr, f = cache.get(key, (None, None))

    if jaxpr is None:
      assert f is None
      # Process the function
      jaxpr = ProcessedJaxpr.make_from_func(
          func=func,
          func_args=func_args,
          params_index=params_index,
          auto_register_tags=auto_register_tags,
          allow_left_out_params=allow_left_out_params,
          **auto_registration_kwargs
      )

      if not allow_no_losses and not jaxpr.loss_tags:
        raise ValueError("No registered losses have been found during tracing.")

      if cache and raise_error_on_diff_jaxpr:

        # If any previous `ProcessedJaxpr` exists verify that it is equivalent
        ref_jaxpr, _ = cache[next(iter(cache))]

        if ref_jaxpr != jaxpr:
          raise ValueError("The consecutive tracing of the provided function "
                           "yielded a non-equivalent `ProcessedJaxpr`.")

      f = functools.partial(transformation, jaxpr)
      cache[key] = (jaxpr, f)

    if return_only_jaxpr:
      return jaxpr
    else:
      return f(func_args, *args)

  return wrapped_transformation


def construct_compute_losses_inputs(
    jaxpr: jax.core.Jaxpr,
    consts: Sequence[Any],
    num_losses: int,
    primal_func_args: FuncArgs,
    params_index: int,
) -> Callable[
    [Params],
    Tuple[Tuple[LossFunctionInputs, ...], Tuple[LossFunction, ...]],
]:
  """Constructs a function that computes the inputs to all loss tags.

  The returned function takes as input only the parameters, as specified by
  ``params_index``, and returns a tuple containing the input values to the first
  ``num_losses`` loss tags in the Jaxpr. This is done by iterating sequentially
  over all equations in the Jaxpr, evaluating each equation, until the correct
  number of loss tags have been discovered and returning the values of their
  inputs.

  Args:
    jaxpr: The Jaxpr to be iterated over.
    consts: Any constants to be used for the computation (see docs on Jaxpr).
    num_losses: The number of loss tags after which to terminate iteration. If
      the Jaxpr has less loss tags, it will return all of them.
    primal_func_args: The concrete values for the inputs to the Jaxpr.
    params_index: The variables from the function arguments which are at this
      index (e.g. ``func_args[params_index]``) are to be considered model
      parameters.

  Returns:
    A function which computes the inputs to the first ``num_losses`` loss tags.
  """

  def forward_compute_losses(
      primal_params: Params
  ) -> Tuple[Tuple[LossFunctionInputs, ...], Tuple[LossFunction, ...]]:
    """Computes and returns the inputs to the first ``num_losses`` loss tags."""

    # Check the provided inputs match the original primals.
    local_func_args = list(primal_func_args)
    original_params = local_func_args[params_index]

    if not utils.abstract_objects_equal(original_params, primal_params):
      raise ValueError("The `primal_params` should have the same abstract "
                       "structure as the original parameters passed in to the "
                       "function.")

    local_func_args[params_index] = primal_params
    flat_args = jax.tree_util.tree_leaves(local_func_args)

    # Mapping from variable -> value
    env = {}
    read = functools.partial(tgm.read_env, env)
    write = functools.partial(tgm.write_env, env)

    # Bind args and consts to environment
    write(jaxpr.invars, flat_args)
    write(jaxpr.constvars, consts)

    # Loop through equations and evaluate primitives using `bind`
    losses_so_far = 0
    losses = []
    losses_p_deps = []
    losses_inputs = []
    for eqn in jaxpr.eqns:
      write(eqn.outvars, tgm.eval_jaxpr_eqn(eqn, read(eqn.invars)))

      if isinstance(eqn.primitive, tags.LossTag):
        loss_tag: tags.LossTag = eqn.primitive
        losses_inputs.append(read(eqn.invars))
        losses.append(loss_tag.loss(*losses_inputs[-1], **eqn.params))
        losses_p_deps.append(loss_tag.extract_parameter_dependants(
            *losses_inputs[-1], **eqn.params))
        losses_so_far += 1

      if num_losses is not None and losses_so_far == num_losses:
        break

    return tuple(losses_p_deps), tuple(losses)

  return forward_compute_losses


def _compute_all_losses(
    p_jaxpr: ProcessedJaxpr,
    primal_func_args: FuncArgs,
) -> Tuple[LossFunction, ...]:
  """Returns all loss functions objects."""
  if not p_jaxpr.loss_tags:
    raise ValueError("The provided `ProcessedJaxpr` has no loss tags.")

  losses_func = construct_compute_losses_inputs(
      jaxpr=p_jaxpr.jaxpr,
      consts=p_jaxpr.consts,
      num_losses=len(p_jaxpr.loss_tags),
      primal_func_args=primal_func_args,
      params_index=p_jaxpr.params_index,
  )
  _, losses = losses_func(primal_func_args[p_jaxpr.params_index])
  return losses


def _loss_tags_vjp(
    p_jaxpr: ProcessedJaxpr,
    primal_func_args: FuncArgs,
) -> LossTagsVjp:
  """Computes a (backward-mode) vector-Jacobian product w.r.t. all loss tags.

  The function has similar interface to :func:`jax.vjp`. It takes as inputs the
  concrete values of the primals at which the Jacobian will be evaluated. It
  returns a pair of ``(losses, losses_vjp)``, where losses is a tuple of
  :class:`~LossFunction` objects and ``vjp_func`` is a function
  taking as inputs the concrete values of the tangents of the inputs for each
  loss tag (corresponding to a loss object in ``losses``) and returns the
  corresponding tangents of the parameters.

  Args:
    p_jaxpr: The :class:``~ProcessedJaxpr`` representing the model function.
      This must include at least one loss tag.
    primal_func_args: The primals at which to evaluate the Jacobian.

  Returns:
    The computed ``losses`` and ``losses_vjp`` pair.
  """

  if not p_jaxpr.loss_tags:
    raise ValueError("The provided `ProcessedJaxpr` has no loss tags.")

  losses_func = construct_compute_losses_inputs(
      jaxpr=p_jaxpr.jaxpr,
      consts=p_jaxpr.consts,
      num_losses=len(p_jaxpr.loss_tags),
      primal_func_args=primal_func_args,
      params_index=p_jaxpr.params_index)

  primal_params = primal_func_args[p_jaxpr.params_index]
  _, full_vjp_func, losses = jax.vjp(losses_func, primal_params, has_aux=True)

  def losses_vjp_func(losses_tangents: Sequence[LossFunctionInputs]) -> Params:
    """Computes the vector-Jacobian product w.r.t. the parameters.

    Args:
      losses_tangents: The tangents to all loss tag's inputs.

    Returns:
      The parameters' tangents, as a result of the vector-Jacobian product.
    """

    if len(losses_tangents) != len(p_jaxpr.loss_tags):
      raise ValueError("The argument `tangents` must be a sequence of the "
                       "tangents to each loss tag in the same order as the "
                       "loss objects that have been returned. The number of "
                       f"loss_tags is {len(p_jaxpr.loss_tags)}, but the length "
                       f"of `tangents` is {len(losses_tangents)}.")

    for i, loss_tangents in enumerate(losses_tangents):
      if not isinstance(loss_tangents, Sequence):
        raise ValueError("Each element of the argument `tangents` must be "
                         f"a sequence, but tangents[{i}] has type "
                         f"{type(loss_tangents)}.")

    [params_tangents] = full_vjp_func(losses_tangents)

    return params_tangents

  return losses, losses_vjp_func


def _loss_tags_jvp(
    p_jaxpr: ProcessedJaxpr,
    primal_func_args: FuncArgs,
    params_tangents: Params,
) -> LossTagsJvp:
  """Computes a (forward-mode) Jacobian-vector product w.r.t. all loss tags.

  The function has similar interface to :func:`jax.jvp`. It takes as inputs the
  concrete values of the primals at which the Jacobian will be evaluated at and
  the concrete values of the tangents for the **parameters**, as specified by
  ``processed_jaxpr.params_index``. It returns a pair of
  ``(losses, losses_tangents)``, where ``losses`` is a tuple of
  :class:`~LossFunction` objects, and ``losses_tangents`` is
  a tuple containing the tangents of the inputs for each loss tag (corresponding
  to a loss object in ``losses``).

  Args:
    p_jaxpr: The :class:`~ProcessedJaxpr` representing the model function. This
      must include at least one loss tag.
    primal_func_args: The primals at which to evaluate the Jacobian.
    params_tangents: The vector of tangents which to multiply with the Jacobian.

  Returns:
    The computed ``losses`` and ``losses_tangents`` pair.
  """

  if not p_jaxpr.loss_tags:
    raise ValueError("The provided `ProcessedJaxpr` has no loss tags.")

  losses_func = construct_compute_losses_inputs(
      jaxpr=p_jaxpr.jaxpr,
      consts=p_jaxpr.consts,
      num_losses=len(p_jaxpr.loss_tags),
      primal_func_args=primal_func_args,
      params_index=p_jaxpr.params_index)

  primal_params = (primal_func_args[p_jaxpr.params_index],)

  tangents = (params_tangents,)

  (_, losses_tangents, losses) = jax.jvp(
      losses_func, primal_params, tangents, has_aux=True)

  return losses, losses_tangents


def _loss_tags_hvp(
    processed_jaxpr: ProcessedJaxpr,
    primal_func_args: FuncArgs,
    params_tangents: Params,
) -> Tuple[Params, Tuple[LossFunction, ...]]:
  """Computes a Hessian-vector product of the function w.r.t. all loss tags.

  The function takes as inputs the concrete values of the primals for the
  function arguments at which the Hessian will be evaluated at and the concrete
  values of the tangents for the **parameters**, as specified by
  ``processed_jaxpr.params_index``. It returns the product of the Hessian with
  this tangents via backward-over-forward mode.

  Args:
    processed_jaxpr: The :class:`~ProcessedJaxpr` representing the model
      function. This must include at least one loss tag.
    primal_func_args: The primals at which to evaluate the Hessian.
    params_tangents: The vector of tangents which to multiply with the Hessian.

  Returns:
    The parameter-structured vector representing the Hessian-vector product and
    the resulting :class:`~LossFunction` objects that correspond to every
    loss tag.
  """

  if not processed_jaxpr.loss_tags:
    raise ValueError("The provided `ProcessedJaxpr` has no loss tags.")

  losses_func = construct_compute_losses_inputs(
      jaxpr=processed_jaxpr.jaxpr,
      consts=processed_jaxpr.consts,
      num_losses=len(processed_jaxpr.loss_tags),
      primal_func_args=primal_func_args,
      params_index=processed_jaxpr.params_index)

  def losses_sum(param_primals: Params) -> Array:
    # This computes the sum of losses evaluated. Makes it easier because we can
    # now use jax.grad rather than jax.vjp for taking derivatives.
    _, losses = losses_func(param_primals)
    return sum(jnp.sum(loss.evaluate()) for loss in losses)

  # Directional derivative function
  df_dot_dv = lambda p: (jax.jvp(losses_sum, [p], [params_tangents])[1])
  hvp = jax.grad(df_dot_dv)(primal_func_args[processed_jaxpr.params_index])

  _, losses = losses_func(primal_func_args[processed_jaxpr.params_index])
  return hvp, losses


def _layer_tag_vjp(
    processed_jaxpr: ProcessedJaxpr,
    primal_func_args: FuncArgs,
) -> LayerTagVjp:
  """Computes primal values and tangents w.r.t. all layer tags.

  The function has similar interface to :func:`jax.vjp`. It takes as inputs the
  concrete values of the primals at which the Jacobian will be evaluated. It
  returns a pair of ``(losses, vjp_func)``, where losses is a tuple of
  :class:`~LossFunction` objects and ``vjp_func`` is a function
  taking as inputs the concrete values of the tangents of the inputs for each
  loss tag (corresponding to a loss object in ``losses``) and returns a list of
  quantities computed for each layer tag in ``processed_jaxpr``. Each entry of
  the list is a dictionary with the following self-explanatory keys:
  ``inputs, outputs, params, outputs_tangents, params_tangents``.

  Args:
    processed_jaxpr: The :class:`~ProcessedJaxpr` representing the model
      function. This must include at least one loss tag.
    primal_func_args: The primals at which to evaluate the Hessian.

  Returns:
    The computed ``losses`` and ``vjp_func`` pair.
  """
  layer_vars_flat = jax.tree_util.tree_leaves(
      [tag.invars for tag in processed_jaxpr.layer_tags])
  layer_input_vars = tuple(set(layer_vars_flat))

  def forward() -> Tuple[Array, ...]:
    """Computes the values of all inputs to all **layer** tags."""

    own_func_args = primal_func_args

    # Mapping from variable -> value
    env = {}
    read = functools.partial(tgm.read_env, env)
    write = functools.partial(tgm.write_env, env)

    # Bind args and consts to environment
    write(processed_jaxpr.jaxpr.invars,
          jax.tree_util.tree_leaves(own_func_args))
    write(processed_jaxpr.jaxpr.constvars, processed_jaxpr.consts)

    # Loop through equations and evaluate them
    num_losses_passed = 0
    for eqn in processed_jaxpr.jaxpr.eqns:

      write(eqn.outvars, tgm.eval_jaxpr_eqn(eqn, read(eqn.invars)))

      if isinstance(eqn.primitive, tags.LossTag):

        num_losses_passed += 1

        if num_losses_passed == len(processed_jaxpr.loss_tags):
          break

    assert num_losses_passed == len(processed_jaxpr.loss_tags)

    return read(layer_input_vars)

  def forward_aux(
      aux: Dict[Var, Array]
  ) -> Tuple[Tuple[LossFunctionInputs, ...], Tuple[LossFunctionInputs, ...]]:
    """Computes the inputs and kwargs of all **loss** tags.

    Args:
      aux: A mapping from an Jaxpr variable to an additional auxiliary value.
        For each variable in this mapping, we add to the value computed during
        standard evaluation the auxiliary value. This is done in order to be
        able to compute gradients wrt all intermediate expressions
        corresponding to the Jaxpr variables in this mapping

    Returns:
      The pair of ``(losses_inputs, losses_kwargs)`` where ``losses_inputs``
      is a tuple of the input values for each loss tag, and ``losses_kwargs``
      is a tuple of the kwargs values of each loss tag.
    """

    own_func_args = primal_func_args

    # Mapping from variable -> value
    env = {}
    read = functools.partial(tgm.read_env, env)

    def write(var, val):

      tgm.write_env(env, var, val)  # pytype: disable=wrong-arg-types  # numpy-scalars

      if not isinstance(var, list):
        var = [var]

      assert isinstance(var, list)

      for v in var:
        if not isinstance(v, jax.core.Literal) and v in aux:
          env[v] = env[v] + aux[v]

    # Bind args and consts to environment
    write(processed_jaxpr.jaxpr.invars,
          jax.tree_util.tree_leaves(own_func_args))

    write(processed_jaxpr.jaxpr.constvars, processed_jaxpr.consts)

    # Loop through equations and evaluate primitives using `bind`
    num_losses_passed = 0
    losses_p_dependants = []
    losses_inputs_values = []

    for eqn in processed_jaxpr.jaxpr.eqns:

      input_values = tuple(read(eqn.invars))
      write(eqn.outvars, tgm.eval_jaxpr_eqn(eqn, read(eqn.invars)))

      if isinstance(eqn.primitive, tags.LossTag):
        loss = eqn.primitive.loss(*input_values, **eqn.params)

        losses_p_dependants.append(loss.parameter_dependants)
        losses_inputs_values.append(input_values)

        num_losses_passed += 1

        if num_losses_passed == len(processed_jaxpr.loss_tags):
          break

    assert num_losses_passed == len(processed_jaxpr.loss_tags)

    # Read the inputs to the loss functions, but also return the target values
    return tuple(losses_p_dependants), tuple(losses_inputs_values)

  # First compute the primal values for the inputs to all layer tags
  layer_input_values = forward()
  primals_dict = dict(zip(layer_input_vars, layer_input_values))

  # Update with the values of all parameters, which are inputs to the function
  primals_dict.update(zip(processed_jaxpr.jaxpr.invars,
                          jax.tree_util.tree_leaves(primal_func_args)))

  # Create auxiliary values all equal to zero.
  aux_values = jax.tree_util.tree_map(jnp.zeros_like, layer_input_values)

  # Create a mapping from all layer tag inputs to the zero values
  aux_dict = dict(zip(layer_input_vars, aux_values))

  # These values would now allow us to compute gradients wrt the layer tags
  # inputs, which are intermediate expressions in the Jaxpr.
  _, aux_vjp, losses_inputs = jax.vjp(
      forward_aux, aux_dict, has_aux=True)

  # Compute the actual loss objects.
  losses = tuple(tag.primitive.loss(*inputs, **tag.params) for tag, inputs in
                 zip(processed_jaxpr.loss_tags, losses_inputs))

  def vjp_func(
      tangents: Tuple[LossFunctionInputs, ...]
  ) -> Tuple[Dict[str, Array], ...]:
    """Computes a (reverse-mode) vector-Jacobian product w.r.t. all layer tags.

    Args:
      tangents: The concrete tangent values for the tangents of the inputs to
        all **loss** tags.

    Returns:
      A tuple containing both the primal and tangent values for the inputs to
      all **layer** tags. The values are provided as a dictionary with keys:
      ``inputs, outputs, params, outputs_tangent, params_tangent``.
    """
    all_tangents = aux_vjp(tangents)
    tangents_dict, inputs_tangents = all_tangents[0], all_tangents[1:]
    inputs_tangents = jax.tree_util.tree_leaves(inputs_tangents)
    tangents_dict.update(zip(processed_jaxpr.jaxpr.invars, inputs_tangents))

    read_primals = functools.partial(tgm.read_env, primals_dict)
    read_tangents = functools.partial(tgm.read_env, tangents_dict)
    layers_info = []

    for tag in processed_jaxpr.layer_tags:

      info = {}

      primals = jax.util.safe_map(read_primals, tuple(tag.invars))

      (info["outputs"],
       info["inputs"],
       info["params"]) = tag.primitive.split_all_inputs(primals)

      # Due to the ability to preprocess inputs for tags the input gradients
      # could be potentially wrong (e.g. zero) so we don't include them.
      tangents = jax.util.safe_map(read_tangents, tuple(tag.invars))

      # inputs_tangent won't be correct for BN layers, but that won't matter
      (info["outputs_tangent"],
       info["inputs_tangent"],
       info["params_tangent"]) = tag.primitive.split_all_inputs(tangents)

      layers_info.append(info)

    return tuple(layers_info)  # pytype: disable=bad-return-type  # numpy-scalars

  return losses, vjp_func


def compute_all_losses(
    func: utils.Func,
    params_index: int = 0,
) -> TransformedFunction[Tuple[LossFunction, ...]]:
  """Creates a function that when called, returns all loss objects.

  The returned function takes as inputs the concrete values of the primals for
  which to compute the loss objects.

  Args:
    func: The model function, which must include at least one loss registration.
    params_index: The variables from the function arguments which are at this
      index (e.g. `func_args[params_index]`) are to be considered model
      parameters.

  Returns:
    A function that computes the Jacobian-vector product with signature
    `Callable[[FuncArgs], Tuple[LossFunction, ...]]`.
  """
  # Note that this function is independent of any layer tags, hence we can avoid
  # calling the auto registration.
  return cached_transformation(
      func=func,
      transformation=_compute_all_losses,
      verifier=lambda: None,
      params_index=params_index,
      auto_register_tags=False,
      allow_left_out_params=True,
  )


def loss_tags_vjp(
    func: utils.Func,
    params_index: int = 0,
) -> TransformedFunction[LossTagsVjp]:
  """Creates a function for the vector-Jacobian product w.r.t. all loss tags.

  The returned function has a similar interface to :func:`jax.vjp`. It takes as
  inputs the concrete values of the primals at which the Jacobian will be
  evaluated. It returns a pair ``(losses, losses_vjp)``, where losses is a
  tuple of :class:`~LossFunction` objects and ``vjp_func`` is a function taking
  as inputs the concrete values of the tangents of the inputs for each loss tag
  (corresponding to a loss object in ``losses``) and returns the corresponding
  tangents of the parameters.

  Args:
    func: The model function, which must include at least one loss registration.
    params_index: The variables from the function arguments which are at this
      index (e.g. `func_args[params_index]`) are to be considered model
      parameters.

  Returns:
    A function that computes the vector-Jacobian product with signature
    `Callable[[FuncArgs], LossTagsVjp]`.
  """
  # Note that this function is independent of any layer tags, hence we can avoid
  # calling the auto registration.
  return cached_transformation(
      func=func,
      transformation=_loss_tags_vjp,
      verifier=lambda: None,
      params_index=params_index,
      auto_register_tags=False,
      allow_left_out_params=True,
  )


def loss_tags_jvp(
    func: utils.Func,
    params_index: int = 0,
) -> ...:
  """Creates a function for the Jacobian-vector product w.r.t. all loss tags.

  The returned function has a similar interface to :func:`jax.jvp`. It takes as
  inputs the concrete values of the primals at which the Jacobian will be
  evaluated at and the concrete values of the tangents for the **parameters**,
  as specified by ``processed_jaxpr.params_index``. It returns a pair
  ``(losses, losses_tangents)``, where ``losses`` is a tuple of
  :class:`~LossFunction` objects, and ``losses_tangents`` is a tuple containing
  the tangents of the inputs for each loss tag (corresponding to a loss object
  in ``losses``).

  Args:
    func: The model function, which must include at least one loss registration.
    params_index: The variables from the function arguments which are at this
      index (e.g. `func_args[params_index]`) are to be considered model
      parameters.

  Returns:
    A function that computes the Jacobian-vector product with signature
    `Callable[[FuncArgs, Params], LossTagsVjp]`.
  """
  # Note that this function is independent of any layer tags, hence we can avoid
  # calling the auto registration.
  return cached_transformation(
      func=func,
      transformation=_loss_tags_jvp,
      verifier=lambda: None,
      params_index=params_index,
      auto_register_tags=False,
      allow_left_out_params=True,
  )


def loss_tags_hvp(
    func: utils.Func,
    params_index: int = 0,
) -> ...:
  """Creates a function for the Hessian-vector product w.r.t. all loss tags.

  The returned function takes as inputs the concrete values of the primals for
  the function arguments at which the Hessian will be evaluated at and the
  concrete values of the tangents for the **parameters**, as specified by
  ``processed_jaxpr.params_index``. It returns the product of the Hessian with
  these tangents via backward-over-forward mode autodiff.

  Args:
    func: The model function, which must include at least one loss registration.
    params_index: The variables from the function arguments which are at this
      index (e.g. `func_args[params_index]`) are to be considered model
      parameters.

  Returns:
    A function that computes the Hessian-vector product and also returns all
    losses, with signature `Callable[[FuncArgs, Params],
    Tuple[LossTagsVjp, Tuple[LossFunction, ...]]`.
  """
  # Note that this function is independent of any layer tags, hence we can avoid
  # calling the auto registration.
  return cached_transformation(
      func=func,
      transformation=_loss_tags_hvp,
      verifier=lambda: None,
      params_index=params_index,
      auto_register_tags=False,
      allow_left_out_params=True,
  )


def layer_tags_vjp(
    func: utils.Func,
    params_index: int = 0,
    auto_register_tags: bool = True,
    raise_error_on_diff_jaxpr: bool = True,
    **auto_registration_kwargs,
) -> ...:
  """Creates a function for primal values and tangents w.r.t. all layer tags.

  The returned function has a similar interface to :func:`jax.vjp`. It takes as
  inputs the concrete values of the primals at which the Jacobian will be
  evaluated. It returns a pair ``(losses, vjp_func)``, where ``losses`` is a
  tuple of :class:`~LossFunction` objects, and ``vjp_func`` is a function
  taking as inputs the concrete values of the tangents of the inputs for each
  loss tag (corresponding to a loss object in ``losses``) and returns a list of
  quantities computed for each layer tag in ``processed_jaxpr``. Each entry of
  the list is a dictionary with the following self-explanatory keys:
  ``inputs, outputs, params, outputs_tangents, params_tangents``.

  Args:
    func: The model function, which must include at least one loss registration.
    params_index: The variables from the function arguments which are at this
      index (e.g. ``func_args[params_index]``) are to be considered model
      parameters.
    auto_register_tags: Whether to run an automatic layer registration on the
      function (e.g. :func:`~auto_register_tags`).
    raise_error_on_diff_jaxpr: When tracing with different arguments, if the
      returned jaxpr has a different graph will raise an exception.
    **auto_registration_kwargs: Any additional keyword arguments, to be passed
      to the automatic registration pass.

  Returns:
    Returns a function that computes primal values and tangents wrt all layer
    tags, with signature `Callable[[FuncArgs, Params], LossTagsVjp]`.
  """

  return cached_transformation(
      func=func,
      transformation=_layer_tag_vjp,
      params_index=params_index,
      auto_register_tags=auto_register_tags,
      allow_left_out_params=False,
      raise_error_on_diff_jaxpr=raise_error_on_diff_jaxpr,
      **auto_registration_kwargs
  )
