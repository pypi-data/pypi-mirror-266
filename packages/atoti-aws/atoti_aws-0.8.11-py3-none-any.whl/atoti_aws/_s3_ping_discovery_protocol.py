from dataclasses import dataclass
from textwrap import dedent

from atoti.experimental._distributed import DiscoveryProtocol
from atoti_core import keyword_only_dataclass
from typing_extensions import override


def _bool_to_xml(value: bool, /) -> str:  # noqa: FBT001
    return str(value).lower()


@keyword_only_dataclass
@dataclass(frozen=True)
class S3PingDiscoveryProtocol(DiscoveryProtocol):
    region_name: str
    bucket_name: str
    remove_all_data_on_view_change: bool = True
    remove_old_coords_on_view_change: bool = True
    write_data_on_find: bool = True

    @property
    @override
    def _xml(self) -> str:
        return dedent(
            f"""\
            <org.jgroups.aws.s3.NATIVE_S3_PING
              region_name="{self.region_name}"
              bucket_name="{self.bucket_name}"
              remove_all_data_on_view_change="{_bool_to_xml(self.remove_all_data_on_view_change)}"
              remove_old_coords_on_view_change="{_bool_to_xml(self.remove_old_coords_on_view_change)}"
              write_data_on_find="{_bool_to_xml(self.write_data_on_find)}"
            />
            """
        )
