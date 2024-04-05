from pathlib import Path
from typing import Optional

from atoti_core import Plugin
from typing_extensions import override


class SynapsePlugin(Plugin):
    @property
    @override
    def jar_path(self) -> Optional[Path]:
        return Path(__file__).parent / "data" / "atoti-directquery-synapse.jar"

    @property
    @override
    def java_package_name(self) -> Optional[str]:
        return "io.atoti.directquery.synapse"
