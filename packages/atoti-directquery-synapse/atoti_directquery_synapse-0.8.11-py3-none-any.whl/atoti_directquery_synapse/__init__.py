"""Plugin to use DirectQuery on `Azure Synapse Analytics <https://azure.microsoft.com/en-us/services/synapse-analytics>`__."""

from .connection import SynapseConnection as SynapseConnection
from .connection_info import SynapseConnectionInfo as SynapseConnectionInfo
from .table import SynapseTable as SynapseTable
from .table_options import SynapseTableOptions as SynapseTableOptions
