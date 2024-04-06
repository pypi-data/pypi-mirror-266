from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..models.audit_log_export_format import AuditLogExportFormat
from ..types import UNSET, Unset

T = TypeVar("T", bound="AuditLogExport")


@attr.s(auto_attribs=True, repr=False)
class AuditLogExport:
    """  """

    _api_ids: List[str]
    _format: AuditLogExportFormat

    def __repr__(self):
        fields = []
        fields.append("api_ids={}".format(repr(self._api_ids)))
        fields.append("format={}".format(repr(self._format)))
        return "AuditLogExport({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        api_ids = self._api_ids

        format = self._format.value

        field_dict: Dict[str, Any] = {}
        # Allow the model to serialize even if it was created outside of the constructor, circumventing validation
        if api_ids is not UNSET:
            field_dict["apiIds"] = api_ids
        if format is not UNSET:
            field_dict["format"] = format

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any], strict: bool = False) -> T:
        d = src_dict.copy()

        def get_api_ids() -> List[str]:
            api_ids = cast(List[str], d.pop("apiIds"))

            return api_ids

        try:
            api_ids = get_api_ids()
        except KeyError:
            if strict:
                raise
            api_ids = cast(List[str], UNSET)

        def get_format() -> AuditLogExportFormat:
            _format = d.pop("format")
            try:
                format = AuditLogExportFormat(_format)
            except ValueError:
                format = AuditLogExportFormat.of_unknown(_format)

            return format

        try:
            format = get_format()
        except KeyError:
            if strict:
                raise
            format = cast(AuditLogExportFormat, UNSET)

        audit_log_export = cls(
            api_ids=api_ids,
            format=format,
        )

        return audit_log_export

    @property
    def api_ids(self) -> List[str]:
        """ API IDs of the Benchling objects to export a single audit log file for. """
        if isinstance(self._api_ids, Unset):
            raise NotPresentError(self, "api_ids")
        return self._api_ids

    @api_ids.setter
    def api_ids(self, value: List[str]) -> None:
        self._api_ids = value

    @property
    def format(self) -> AuditLogExportFormat:
        """ The format of the exported file. """
        if isinstance(self._format, Unset):
            raise NotPresentError(self, "format")
        return self._format

    @format.setter
    def format(self, value: AuditLogExportFormat) -> None:
        self._format = value
