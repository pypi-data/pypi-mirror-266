"""Chart Base Series.

This class will be used to define series configuration for those widgets that uses
charts.
"""
import re
from typing import Optional
from typing import Union

from engineai.sdk.dashboard.links import WidgetField
from engineai.sdk.dashboard.links.abstract import AbstractFactoryLinkItemsHandler
from engineai.sdk.dashboard.links.typing import GenericLink

from ..exceptions import SeriesMissingLabelError
from ..exceptions import SeriesUnsupportedDataColumnError


class ChartSeriesBase(AbstractFactoryLinkItemsHandler):
    """Chart Base Series class."""

    _API_TYPE: Optional[str] = None

    def __init__(
        self,
        name: Optional[Union[str, GenericLink]] = None,
        data_column: Optional[Union[str, GenericLink]] = None,
    ) -> None:
        """Constructor for Chart Base Series class.

        Args:
            name (Optional[Union[str, GenericLink]]): name
                that will be used to identify the series.
            data_column (Optional[Union[str, WidgetField]]): column
                in dataframe(s) that will be transformed to be series name.
        """
        super().__init__()
        self.__name = self._set_name(name=name, data_column=data_column)

    @property
    def _api_type(self) -> str:
        if self._API_TYPE is None:
            raise NotImplementedError(
                f"Class {self.__class__.__name__} does not have the variable "
                f"`_API_TYPE` initialized. Please add the proper value or overwrite "
                f"this method {self.__class__.__name__}._api_type."
            )
        return self._API_TYPE

    @property
    def name(self) -> Union[str, GenericLink]:
        """Returns name of series.

        Returns:
            Union[str, WidgetField]: name
        """
        return self.__name

    def _set_name(
        self,
        name: Optional[Union[str, GenericLink]],
        data_column: Optional[Union[str, GenericLink]],
    ) -> Union[str, GenericLink]:
        """Sets the series label based on the data column, if no `name` is added.

        If `name` is not None, the name will prevail. Otherwise data column will be
            transformed to the series label.
        """
        if name is not None:
            return name
        elif name is None and data_column is None:
            raise SeriesMissingLabelError(class_name=self.__class__.__name__)
        elif isinstance(data_column, str):
            if re.search("{{(.*?)}}", data_column):
                return data_column
            else:
                return data_column.replace("_", " ").title()
        elif isinstance(data_column, WidgetField):
            return data_column
        else:
            raise SeriesUnsupportedDataColumnError(class_name=self.__class__.__name__)
