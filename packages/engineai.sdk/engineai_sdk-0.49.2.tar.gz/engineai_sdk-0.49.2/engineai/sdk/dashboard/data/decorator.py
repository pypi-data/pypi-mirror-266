"""Data Decorator Module."""
import functools
import inspect
import itertools
import logging
from typing import Any
from typing import Callable
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple
from typing import Union
from typing import cast

import pandas as pd

from engineai.sdk.dashboard.config import SKIP_DATA_VALIDATION
from engineai.sdk.dashboard.data.exceptions import DataProcessError
from engineai.sdk.dashboard.data.exceptions import DataRouteWithArgumentsError
from engineai.sdk.dashboard.data.exceptions import DataValidationError
from engineai.sdk.dashboard.exceptions import BaseDataValidationError
from engineai.sdk.dashboard.interface import OperationInterface as OperationItem
from engineai.sdk.dashboard.links import WidgetField
from engineai.sdk.dashboard.links.typing import GenericLink
from engineai.sdk.dashboard.utils import generate_progressbar
from engineai.sdk.internal.rubik import Rubik

from .file_keys_handler import DataKeysReader
from .file_keys_handler import DataKeysWriter
from .manager.interface import DependencyManagerInterface as DependencyManager
from .manager.interface import StaticDataType

Func = Callable[..., StaticDataType]

logger = logging.getLogger(__name__)


class DataSource:
    """Decorator Class that stores data in the Dashboard Storage."""

    def __init__(
        self,
        func: Union[Func, StaticDataType],
        *args: GenericLink,
        operations: Optional[List[OperationItem]] = None,
        base_path: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Decorator Class that stores data in the Dashboard Storage."""
        self.func: Func = (
            cast(Func, (lambda: func))
            if isinstance(func, (pd.DataFrame, Dict))
            else func
        )

        self.args: Tuple[GenericLink, ...] = args
        self.__base_path = (
            base_path
            if base_path is not None
            else f"{self.func.__module__}.{self.func.__name__}".replace(".", "/")
        )
        self.__separator = "/"
        self.__duplicates: Set[str] = set()
        self.kwargs: Dict[str, Any] = kwargs
        self.__operations: Optional[List[OperationItem]] = operations
        self.__component: DependencyManager

    @property
    def component(self) -> DependencyManager:
        """Component."""
        return self.__component

    @component.setter
    def component(self, component: DependencyManager) -> None:
        """Set component."""
        self.__component = component

    @property
    def operations(self) -> Optional[List[OperationItem]]:
        """Get Operations."""
        return self.__operations

    def __validate_route_args(self, component: Any) -> None:
        if component.data_id == "route" and self.args:
            raise DataRouteWithArgumentsError()

    @classmethod
    def decorator(
        cls,
        _func: Optional[Func] = None,
    ) -> Any:
        """Decorator to store data in the Dashboard Storage. Call as @data_source.

        Args:
            _func (Optional[Func], optional): Function to be decorated.
        """

        def inner_decorator(func: Func) -> "Any":
            @functools.wraps(func)
            def wrapper(*args: GenericLink, **kwargs: Any) -> "DataSource":
                return cls(
                    func,
                    *args,
                    **kwargs,
                )

            return wrapper

        if _func is None:
            return inner_decorator
        else:
            return inner_decorator(_func)

    @property
    def base_path(self) -> str:
        """Returns the base path of the data."""
        return self.__base_path

    @property
    def separator(self) -> str:
        """Returns the separator of the data."""
        return self.__separator

    @property
    def func_args(self) -> List[Any]:
        """Returns data source signature."""
        return list(
            filter(
                lambda x: x if "*" not in str(x) else None,
                list(inspect.signature(self.func).parameters.values()),
            )
        )

    def __call__(
        self,
        storage: Rubik,
        write_keys: bool,
    ) -> None:
        """Stores the data in the storage."""
        try:
            self.__validate_route_args(self.component)
            self.__store_data(
                storage=storage,
                write_keys=write_keys,
                function_name=self.__base_path,
            )
        except Exception as error:  # Force the parallel task to raise
            raise error

    def __store_data(
        self,
        storage: Rubik,
        write_keys: bool,
        function_name: Optional[str],
    ) -> None:
        iterable = self.get_args_data(storage) if self.args else iter([None])
        with generate_progressbar(progress_bar=False) as pbar:
            with DataKeysWriter(self.__base_path, write_keys=write_keys) as data_keys:
                for options in iterable:
                    try:
                        options_data = options if options else None
                        data = (
                            self.func(*options_data, **self.kwargs)
                            if options_data is not None
                            else self.func(**self.kwargs)
                        )
                    except BaseException as error:
                        raise DataProcessError(
                            data_id=self.component.data_id,
                            class_name=self.component.__class__.__name__,
                            error_string=str(error),
                            function_name=function_name,
                            options=options,
                            function_arguments=self.func_args,
                        ) from error

                    pbar.set_description_str(
                        f"Store {self._resolve_path(options_data)} ...", refresh=True
                    )

                    if self.component.data_id == "route":
                        for row in cast(pd.DataFrame, data).itertuples(index=False):
                            self._validate_and_store(
                                storage=storage,
                                data=pd.DataFrame([row]),
                                options=[getattr(row, self.component.query_parameter)],
                                function_name=function_name,
                            )

                    else:
                        self._validate_and_store(
                            storage=storage,
                            data=data,
                            options=options_data,
                            function_name=function_name,
                        )

                    data_keys.write(options_data)
            pbar.set_description_str(
                f"✅ All {self.component.data_id} data stored..✅",
                refresh=True,
            )

    def get_args_data(self, storage: Rubik) -> Iterable[Tuple[str, ...]]:
        """Merge the arguments with the data."""
        paths = self.resolve_paths()
        for data in itertools.product(
            *(
                self.get_data(
                    storage=storage,
                    arg=arg,
                    field=self.args[i].field,
                )
                for i, arg in enumerate(paths)
            )
        ):
            yield data

    def resolve_paths(self) -> List[Tuple[str, GenericLink]]:
        """Get paths from the arguments."""
        return [self._get_arg_path(arg) for arg in self.args] if self.args else []

    def _get_arg_path(self, arg) -> Tuple[str, GenericLink]:
        separator = (
            self.__separator
            if not isinstance(arg, WidgetField)
            or any(d.args for d in arg.link_component.data)
            else ""
        )
        return (
            f"{next(iter(arg.link_component.data)).base_path}{separator}",
            arg.link_component,
        )

    def get_data(
        self, storage: Rubik, arg: Tuple[str, GenericLink], field: str
    ) -> Iterable[Any]:
        """Get data from the storage, based on the path inserted."""
        path, component = arg
        logger.debug("Get DATA path: '%s'.", path)

        for key in DataKeysReader.keys(path, self.separator):
            if component.data_id != "route":
                values = cast(pd.DataFrame, storage[key])
                for value in values[field].tolist():
                    yield value
            else:
                yield key.replace(path, "")

        logger.debug("Finished get data.")

    def _validate_and_store(
        self,
        storage: Rubik,
        data: StaticDataType,
        options: Optional[List[str]],
        function_name: Optional[str],
    ) -> None:
        if not SKIP_DATA_VALIDATION:
            try:
                self.component.validate(data, storage=storage)
            except BaseDataValidationError as error:
                raise DataValidationError(
                    data_id=self.component.data_id,
                    class_name=self.component.__class__.__name__,
                    error_string=str(error),
                    function_name=function_name,
                    options=options,
                ) from error

        path = self._resolve_path(options)
        if path not in self.__duplicates:
            self.__duplicates.add(path)
            storage[path] = self.component.post_process_data(data)

    def _resolve_path(
        self,
        options: Optional[List[str]],
    ) -> str:
        if self.__base_path == options:
            return self.__base_path

        return (
            f"{self.__base_path}/"
            f"{f'{self.__separator}'.join(tuple(map(str, options)))}"
            if options
            else self.__base_path
        )


data_source = DataSource.decorator
