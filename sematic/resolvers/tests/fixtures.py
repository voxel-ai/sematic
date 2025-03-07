# Standard Library
from dataclasses import dataclass, replace
from typing import List, Optional, Tuple
from unittest import mock

# Third-party
import pytest

# Sematic
from sematic.plugins.abstract_external_resource import (
    AbstractExternalResource,
    ResourceState,
)
from sematic.tests.fixtures import MockStorage


@pytest.fixture
def mock_local_resolver_storage():
    mock_storage = MockStorage()
    with mock.patch(
        "sematic.resolvers.local_resolver.LocalStorage", return_value=mock_storage
    ):
        yield mock_storage


@pytest.fixture
def mock_cloud_resolver_storage():
    mock_storage = MockStorage()
    with mock.patch(
        "sematic.resolvers.cloud_resolver.S3Storage", return_value=mock_storage
    ):
        yield mock_storage


_fake_resource_history: List["FakeExternalResource"] = []
_fake_resource_call_history: List[Tuple["FakeExternalResource", str]] = []


@dataclass(frozen=True)
class FakeExternalResource(AbstractExternalResource):
    some_field: int = 0
    raise_on_activate: bool = False
    raise_on_deactivate: bool = False
    raise_on_update: bool = False

    @classmethod
    def reset_history(cls) -> None:
        _fake_resource_history.clear()
        _fake_resource_call_history.clear()

    @classmethod
    def all_resource_ids(cls) -> List[str]:
        return list({r.id for r in _fake_resource_history})

    @classmethod
    def history_by_id(cls, resource_id: Optional[str]) -> List["FakeExternalResource"]:
        return [
            r
            for r in _fake_resource_history
            if resource_id is None or r.id == resource_id
        ]

    @classmethod
    def state_history_by_id(cls, resource_id: Optional[str]) -> List[ResourceState]:
        history = cls.history_by_id(resource_id)
        states = []
        previous_state = None
        for resource in history:
            state = resource.status.state
            if state != previous_state:
                states.append(state)
            previous_state = state
        return states

    @classmethod
    def call_history_by_id(cls, resource_id: Optional[str]) -> List[str]:
        return [
            call
            for r, call in _fake_resource_call_history
            if resource_id is None or r.id == resource_id
        ]

    def __post_init__(self):
        result = super().__post_init__()
        _fake_resource_history.append(self)
        return result

    def use_resource(self) -> int:
        _fake_resource_call_history.append((self, "use_resource()"))
        if self.status.state != ResourceState.ACTIVE:
            raise RuntimeError(f"Resource used while in the state: {self.status.state}")
        return self.some_field

    def _do_activate(self, is_local: bool):
        _fake_resource_call_history.append((self, f"_do_activate({is_local})"))
        if self.raise_on_activate:
            raise ValueError("Intentional fail")
        return replace(
            self,
            status=replace(
                self.status,
                state=ResourceState.ACTIVATING,
                message="Allocating fake resource",
            ),
        )

    def _do_deactivate(self):
        if self.raise_on_deactivate:
            raise ValueError("Intentional fail")
        _fake_resource_call_history.append((self, "_do_deactivate()"))
        return replace(
            self,
            status=replace(
                self.status,
                state=ResourceState.DEACTIVATING,
                message="Deallocating fake resource",
            ),
        )

    def _do_update(self) -> "FakeExternalResource":
        _fake_resource_call_history.append((self, "_do_update()"))
        if self.raise_on_update:
            raise ValueError("Intentional fail")
        if self.status.state == ResourceState.ACTIVATING:
            return replace(
                self,
                status=replace(
                    self.status,
                    state=ResourceState.ACTIVE,
                    message="Resource is ready!",
                ),
            )
        elif self.status.state == ResourceState.DEACTIVATING:
            return replace(
                self,
                status=replace(
                    self.status,
                    state=ResourceState.DEACTIVATED,
                    message="Resource is cleaned!",
                ),
            )
        return replace(
            self,
            status=replace(
                self.status,
                state=self.status.state,
                message="Nothing has changed...",
            ),
        )
