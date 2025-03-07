# Standard Library
from typing import Any, List, Optional  # noqa: F401

# Sematic
from sematic.abstract_future import AbstractFuture, FutureState
from sematic.resolver import Resolver
from sematic.resolvers.local_resolver import LocalResolver
from sematic.resolvers.resource_requirements import ResourceRequirements
from sematic.resolvers.silent_resolver import SilentResolver


class Future(AbstractFuture):
    """
    Class representing a future function execution.

    A future is essentially a tuple of with two elements:

    * The function to execute
    * A set of input arguments, that can be concrete values or futures themselves
    """

    def resolve(
        self, resolver: Optional[Resolver] = None, tracking: bool = True
    ) -> Any:
        """
        Trigger the resolution of the future and all its nested futures.

        Parameters
        ----------
        resolver: Optional[Resolver]
            The `Resolver` to use to execute this future.
        tracking: bool
            Enable tracking. Defaults to `True`. If `True`, the future's
            execution as well as that of all its nested future will be tracked
            in the database and viewable in the UI. If `False`, no tracking is
            persisted to the DB.
        """
        if self.state != FutureState.RESOLVED:
            default_resolver = LocalResolver if tracking else SilentResolver
            resolver = resolver or default_resolver()

            self.value = resolver.resolve(self)

        return self.value

    def set(self, **kwargs):
        """
        Set future properties: `name`, `tags`.

        Parameters
        ----------
        name: str
            The future's name. This will be used to name the run in the UI.

        inline: bool
            When using the `CloudResolver`, whether the instrumented function
            should be executed inside the same process and worker that is executing
            the `Resolver` itself.

            Defaults to `True`, as most pipeline functions are expected to be
            lightweight. Explicitly set this to `False` in order to distribute its
            execution to a worker and parallelize its execution.

        resource_requirements: ResourceRequirements
            When using the `CloudResolver`, specifies what special execution
            resources the function requires. Defaults to `None`.

        tags: List[str]
            A list of strings tags to attach to the resulting run.

        Returns
        -------
        Future
            The current `Future` object. This enables chaining.
        """
        mutable_fields = {"name", "inline", "resource_requirements", "tags"}
        invalid_fields = set(kwargs) - mutable_fields
        if len(invalid_fields) > 0:
            raise ValueError(f"Cannot mutate fields: {invalid_fields}")

        if "name" in kwargs:
            value = kwargs["name"]
            if not (isinstance(value, str) and len(value) > 0):
                raise ValueError(
                    f"Invalid `name`, must be a non-empty string: {repr(value)}"
                )

        if "inline" in kwargs:
            value = kwargs["inline"]
            if not (isinstance(value, bool)):
                raise ValueError(f"Invalid `inline`, must be a bool: {repr(value)}")

        if "resource_requirements" in kwargs:
            value = kwargs["resource_requirements"]
            if not (isinstance(value, ResourceRequirements)):
                raise ValueError(
                    f"Invalid `resource_requirements`, must be a ResourceRequirements: "
                    f"{repr(value)}"
                )

        if "tags" in kwargs:
            value = kwargs["tags"]
            if not (
                isinstance(value, list)
                and all(isinstance(tag, str) and len(tag) > 0 for tag in value)
            ):
                raise ValueError(
                    f"Invalid `tags`, must be a list of non empty strings: {repr(value)}"
                )

        # at this point, kwargs contains only mutable properties,
        # and they have all been checked
        for name, value in kwargs.items():
            setattr(self._props, name, value)

        return self

    def __getitem__(self, index):
        raise NotImplementedError(
            "Future.__getitem__ is not supported yet. Find a workaround at https://docs.sematic.dev/diving-deeper/future-algebra#attribute-and-item-access"  # noqa: E501
        )

    def __iter__(self):
        raise NotImplementedError(
            "Future.__iter__ is not supported yet. Find a workaround at https://docs.sematic.dev/diving-deeper/future-algebra#unpacking-and-iteration"  # noqa: E501
        )

    def __bool__(self):
        raise NotImplementedError(
            "Future.__bool__ is not supported yet. Find a workaround at https://docs.sematic.dev/diving-deeper/future-algebra#arithmetic-operations"  # noqa: E501
        )

    def __not__(self):
        raise NotImplementedError(
            "Future.__not__ is not supported yet. Find a workaround at https://docs.sematic.dev/diving-deeper/future-algebra#arithmetic-operations"  # noqa: E501
        )

    def __add__(self, _):
        raise NotImplementedError(
            "Future.__add__ is not supported yet. Find a workaround at https://docs.sematic.dev/diving-deeper/future-algebra#arithmetic-operations"  # noqa: E501
        )

    def __iadd__(self, _):
        raise NotImplementedError(
            "Future.__iadd__ is not supported yet. Find a workaround at https://docs.sematic.dev/diving-deeper/future-algebra#arithmetic-operations"  # noqa: E501
        )

    def __mul__(self, _):
        raise NotImplementedError(
            "Future.__mul__ is not supported yet. Find a workaround at https://docs.sematic.dev/diving-deeper/future-algebra#arithmetic-operations"  # noqa: E501
        )

    def __imul__(self, _):
        raise NotImplementedError(
            "Future.__imul__ is not supported yet. Find a workaround at https://docs.sematic.dev/diving-deeper/future-algebra#arithmetic-operations"  # noqa: E501
        )

    def __truediv__(self, _):
        raise NotImplementedError(
            "Future.__truediv__ is not supported yet. Find a workaround at https://docs.sematic.dev/diving-deeper/future-algebra#arithmetic-operations"  # noqa: E501
        )

    def __itruediv__(self, _):
        raise NotImplementedError(
            "Future.__itruediv__ is not supported yet. Find a workaround at https://docs.sematic.dev/diving-deeper/future-algebra#arithmetic-operations"  # noqa: E501
        )
