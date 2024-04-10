"""Specs for Dependencies Graph."""
import concurrent.futures
import contextvars
from threading import Thread
from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple
from typing import Union
from typing import cast

import networkx as nx
from typing_extensions import Unpack

from engineai.sdk.dashboard.config import TOTAL_WORKERS
from engineai.sdk.dashboard.interface import WidgetInterface as Widget
from engineai.sdk.dashboard.utils import generate_progressbar

from ..abstract.typing import PrepareParams
from ..data.file_keys_handler import DataKeysReader
from .page.route import Route


class _ThreadExecutor(concurrent.futures.ThreadPoolExecutor):
    """Custom ThreadPoolExecutor class that has an exceptions handler."""

    def __init__(self, max_workers: Optional[int] = None):
        """Initializes a new ThreadPoolExecutor instance.

        Args:
            max_workers: The maximum number of threads that can be used to
                execute the given calls.
        """
        self.parent_ctx = contextvars.copy_context()

        super().__init__(
            initializer=self._set_context,
            max_workers=max_workers,
            thread_name_prefix="dashboard-factory",
        )

    def _set_context(self) -> None:
        for var, value in self.parent_ctx.items():
            var.set(value)

    def custom_shutdown(
        self,
    ) -> None:
        cast(Set[Thread], self._threads).clear()


class Node:
    """Specs for dependency node."""

    def __init__(self, name: str, component: Union[Widget, Route]) -> None:
        """Node constructor."""
        self.name = name
        self.component = component
        self.args = {repr(dep) for dep in ([d.args for d in self.component.data])}

        self.kwargs = {repr(d.kwargs) for d in self.component.data}

    def __str__(self) -> str:
        return (
            f"{self.name}{tuple(self.args) if self.args else ''}"
            f"{tuple(self.kwargs) if self.kwargs else ''}"
        )

    def __repr__(self) -> str:
        return (
            f"{self.name}{tuple(self.args) if self.args else ''}"
            f"{tuple(self.kwargs) if self.kwargs else ''}"
        )

    def __hash__(self) -> int:
        return hash(f"{self.name}_{''.join(self.args)}_{''.join(self.kwargs)}")

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Node):
            return (
                self.name == other.name
                and self.args == other.args
                and self.kwargs == other.kwargs
            )
        else:
            return False


class Graph:
    """Dependencies graph that will be used to manage the store process."""

    def __init__(
        self,
        widgets: List[List[Widget]],
        routes: List[Union[Route, None]],
        **kwargs: Unpack[PrepareParams],
    ) -> None:
        """Constructor for dependencies graph."""
        self.__instance: nx.DiGraph = nx.DiGraph()
        self.__add_nodes(widgets=self.__filter_widgets(widgets), routes=routes)
        self.__start_store_data(**kwargs)

    def __start_store_data(self, **kwargs: Unpack[PrepareParams]) -> None:
        DataKeysReader.delete()
        self.__store_data(**kwargs)

    def __filter_widgets(self, widgets: List[List[Widget]]) -> List[Widget]:
        filter_set = set()
        result = []
        for elements in widgets:
            for widget in elements:
                key = self.__generate_key(widget)
                if key not in filter_set:
                    filter_set.add(key)
                    result.append(widget)
        return result

    def __generate_key(self, widget: Widget) -> Optional[str]:
        data = widget.data

        # return none if is json data
        if data is None:
            return None

        base_path = "@".join({d.base_path for d in data})

        args = (repr(dep) for d in data for dep in d.args)

        kwargs = {repr(d.kwargs) for d in data}

        return f"{base_path}_{args}_{kwargs}"

    def __add_nodes(
        self, widgets: List[Widget], routes: List[Union[Route, None]]
    ) -> None:
        for route in routes:
            if route is not None:
                for element in route.data:
                    self.__instance.add_node(
                        Node(
                            element.base_path,  # type: ignore
                            route,
                        )
                    )

        for element in widgets:
            data = element.data
            if data is None:
                continue
            base_path = "@".join({d.base_path for d in data})
            self.__instance.add_node(Node(base_path, element))
            self.__add_edges(next(iter(data)).args, base_path, element)
            self.__add_edges(element.widget_fields, base_path, element)

    def __add_edges(
        self, iterable: Iterable[Any], base_path: str, element: Widget
    ) -> None:
        for dep in iterable:
            for d in dep.link_component.data:
                self.__instance.add_edge(
                    Node(d.base_path, dep.link_component),
                    Node(base_path, element),
                )

    def __store_data(self, **kwargs: Unpack[PrepareParams]) -> None:
        """Stores items data."""
        futures: Dict[Node, Any] = {}
        completed: List[Node] = []
        instance_copy = self.__instance.copy()
        with _ThreadExecutor(max_workers=TOTAL_WORKERS) as executor:
            with generate_progressbar(
                total=len(self.__instance), additional=True
            ) as pbar:
                while len(completed) != len(self.__instance):
                    blocked: List[Node] = []
                    for node in nx.topological_sort(instance_copy):
                        pred = self.__instance.predecessors(node)
                        dependencies, blocked = self.__process_dependencies(
                            node, pred, blocked, futures
                        )

                        if node in blocked:
                            continue

                        done, not_done = concurrent.futures.wait(
                            dependencies,
                            return_when=concurrent.futures.FIRST_COMPLETED,
                        )

                        self.__handle_exceptions(executor, done)

                        if len(not_done) > 0:
                            blocked.append(node)
                            continue

                        completed.append(node)
                        kwargs.update(
                            {"write": len(self.__instance.out_edges(node)) > 0}
                        )
                        future = executor.submit(node.component.store_data, **kwargs)
                        future.add_done_callback(lambda _: pbar.update(1))
                        future.add_done_callback(lambda _: pbar.refresh(nolock=True))
                        futures[node] = future
                    instance_copy.remove_nodes_from(completed)
                self.__handle_exceptions(
                    executor, concurrent.futures.as_completed(futures.values())
                )
                pbar.set_description_str(
                    "✅ All data stored..✅ ",
                )

    def __process_dependencies(
        self,
        node: Node,
        pred: Any,
        blocked: List[Node],
        futures: Dict[Node, Any],
    ) -> Tuple[List[Any], List[Node]]:
        dependencies: List[Any] = []
        for dependency in pred:
            if dependency in blocked:
                blocked.append(node)
                break
            dependencies.append(futures[dependency])
        return dependencies, blocked

    def __handle_exceptions(self, executor: _ThreadExecutor, tasks: Any) -> None:
        for task in tasks:
            if task.exception() is not None:
                try:
                    task.result()
                except BaseException as e:
                    executor.custom_shutdown()
                    raise e
