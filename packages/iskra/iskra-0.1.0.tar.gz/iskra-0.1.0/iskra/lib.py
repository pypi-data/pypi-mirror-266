import contextlib
from dataclasses import dataclass, field
from typing import (
    Callable,
    Concatenate,
    List,
    ParamSpec,
    TypeVar,
    Mapping,
    Generator,
    Dict,
    Any,
)


@dataclass
class TestExecution:
    pass


@dataclass
class TestCase:
    name: str
    test_fn: Callable[[], TestExecution]
    every_label: List[str] = field(default_factory=list)


@dataclass
class ExecutionScope:
    ctx: Dict[int, Any]
    exit_stack: contextlib.ExitStack


@dataclass
class TestGroup:
    name: str
    every_case: List[TestCase] = field(default_factory=list)
    execution_scope: ExecutionScope | None = None

    def add_case(self, case: TestCase) -> None:
        self.every_case.append(case)

    @contextlib.contextmanager
    def shared_scope(self) -> Generator[ExecutionScope, None, None]:
        with contextlib.ExitStack() as stack:
            execution_scope = ExecutionScope(ctx={}, exit_stack=stack)
            self.execution_scope = execution_scope
            yield execution_scope

    def scope(self) -> ExecutionScope:
        if self.execution_scope is None:
            raise RuntimeError()
        return self.execution_scope

    def run(self) -> List[TestExecution]:
        with contextlib.ExitStack() as stack:
            execution_scope = ExecutionScope(ctx={}, exit_stack=stack)
            self.execution_scope = execution_scope
            every_x = [case.test_fn() for case in self.every_case]
            self.execution_scope = None
        return every_x


@dataclass
class TestSuite:
    every_group: List[TestGroup] = field(default_factory=list)

    def add_group(self, group: TestGroup) -> None:
        self.every_group.append(group)

    def run(self) -> Mapping[str, List[TestExecution]]:
        return {group.name: group.run() for group in self.every_group}


def test_fn_from_fn(fn: Callable[[], None]) -> Callable[[], TestExecution]:
    def test_fn() -> TestExecution:
        try:
            fn()
        except AssertionError as _e:
            pass

        return TestExecution()

    return test_fn


def test_case(
    test_group: TestGroup,
    name: str,
) -> Callable[[Callable[[], None]], Callable[[], TestExecution]]:
    def decorator(fn: Callable[[], None]) -> Callable[[], TestExecution]:
        test_fn = test_fn_from_fn(fn)
        case = TestCase(name=name, test_fn=test_fn)
        test_group.add_case(case)
        return test_fn

    return decorator


P = ParamSpec("P")
X = TypeVar("X")
T = TypeVar("T")


def inject_fn(
    factory_fn: Callable[[], X],
    execution_scope_getter: Callable[[], ExecutionScope] | None = None,
) -> Callable[[Callable[Concatenate[X, P], T]], Callable[P, T]]:
    def decorator(fn: Callable[Concatenate[X, P], T]) -> Callable[P, T]:
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            if execution_scope_getter is not None:
                execution_scope = execution_scope_getter()
                h = hash(factory_fn)
                if h not in execution_scope.ctx:
                    execution_scope.ctx[h] = factory_fn()
                value = execution_scope.ctx[h]
                return fn(value, *args, **kwargs)
            return fn(factory_fn(), *args, **kwargs)

        return wrapper

    return decorator


def inject_gen_fn(
    gen_factory: Callable[[], Generator[X, None, None]],
    execution_scope_getter: Callable[[], ExecutionScope] | None = None,
) -> Callable[[Callable[Concatenate[X, P], T]], Callable[P, T]]:
    def decorator(fn: Callable[Concatenate[X, P], T]) -> Callable[P, T]:
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            if execution_scope_getter is not None:
                execution_scope = execution_scope_getter()
                h = hash(gen_factory)
                if h not in execution_scope.ctx:
                    cm = contextlib.contextmanager(gen_factory)
                    execution_scope.ctx[h] = execution_scope.exit_stack.enter_context(
                        cm()
                    )
                value = execution_scope.ctx[h]
                return fn(value, *args, **kwargs)
            cm = contextlib.contextmanager(gen_factory)
            with cm() as value:
                return fn(value, *args, **kwargs)

        return wrapper

    return decorator
