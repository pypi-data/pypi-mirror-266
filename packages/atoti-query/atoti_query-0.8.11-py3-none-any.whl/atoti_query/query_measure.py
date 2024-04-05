from typing import Optional

from atoti_core import BaseMeasure, MeasureIdentifier
from typing_extensions import override


class QueryMeasure(BaseMeasure):
    def __init__(
        self,
        identifier: MeasureIdentifier,
        /,
        *,
        description: Optional[str],
        folder: Optional[str],
        formatter: Optional[str],
        visible: bool,
    ) -> None:
        super().__init__(identifier)

        self._description = description
        self._folder = folder
        self._formatter = formatter
        self._visible = visible

    @property
    @override
    def folder(self) -> Optional[str]:
        """Folder of the measure."""
        return self._folder

    @property
    @override
    def visible(self) -> bool:
        """Whether the measure is visible or not."""
        return self._visible

    @property
    @override
    def description(self) -> Optional[str]:
        """Description of the measure."""
        return self._description

    @property
    @override
    def formatter(self) -> Optional[str]:
        """Formatter of the measure."""
        return self._formatter
