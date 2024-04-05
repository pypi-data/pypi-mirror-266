from collections import defaultdict
from collections.abc import Mapping
from typing import TypeVar

from typing_extensions import override

from .base_measure import BaseMeasure
from .repr_json import ReprJson, ReprJsonable

MeasureT_co = TypeVar("MeasureT_co", bound=BaseMeasure, covariant=True)


class BaseMeasures(Mapping[str, MeasureT_co], ReprJsonable):
    @override
    def _repr_json_(self) -> ReprJson:
        """Return the JSON representation of measures."""
        measures_json: dict[str, dict[str, object]] = defaultdict(dict)
        no_folder = {}
        for measure in self.values():
            if measure.visible:
                json = {"formatter": measure.formatter}
                if measure.description is not None:
                    json["description"] = measure.description
                if measure.folder is None:
                    # We store them into another dict to insert them after the folders
                    no_folder[measure.name] = json
                else:
                    folder = f"📁 {measure.folder}"
                    measures_json[folder][measure.name] = json
        for folder, measures_in_folder in measures_json.items():
            measures_json[folder] = dict(sorted(measures_in_folder.items()))
        return (
            {**measures_json, **dict(sorted(no_folder.items()))},
            {"expanded": False, "root": "Measures"},
        )


BaseMeasuresBound = BaseMeasures[BaseMeasure]
