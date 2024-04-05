from pathlib import Path
from typing import Optional

from atoti_core import Plugin
from typing_extensions import override


class AwsPlugin(Plugin):
    @property
    @override
    def jar_path(self) -> Optional[Path]:
        return Path(__file__).parent / "data" / "atoti-aws.jar"

    @property
    @override
    def java_package_name(self) -> Optional[str]:
        return "io.atoti.loading.s3"
