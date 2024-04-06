from enum import IntEnum, auto
from typing import Final, Literal

SyndbTableNames = Literal[
    "neuron",
    "dendrite",
    "axon",
    "pre_synaptic_terminal",
    "synapse",
    "dendritic_spine",
    "endoplasmic_reticulum",
    "nucleus",
    "vesicle",
    "mitochondria",
]


class SyndbTable(IntEnum):
    # Neuro data hierarchy ==================
    NEURON = auto()

    # Neurites
    DENDRITE = auto()
    AXON = auto()
    PRE_SYNAPTIC_TERMINAL = auto()
    SYNAPSE = auto()
    DENDRITIC_SPINE = auto()

    # Cellular structures
    ENDOPLASMIC_RETICULUM = auto()
    NUCLEUS = auto()

    # Smaller organelles
    VESICLE = auto()
    MITOCHONDRIA = auto()


COMPARTMENT_HIERARCHY: Final[list[tuple[SyndbTable, ...]]] = [
    (SyndbTable.NEURON,),
    (SyndbTable.DENDRITE, SyndbTable.AXON),
    (SyndbTable.PRE_SYNAPTIC_TERMINAL, SyndbTable.SYNAPSE, SyndbTable.DENDRITIC_SPINE),
    (
        SyndbTable.MITOCHONDRIA,
        SyndbTable.ENDOPLASMIC_RETICULUM,
        SyndbTable.NUCLEUS,
        SyndbTable.VESICLE,
    ),
]

_max_line = 0
compartment_to_valid_parents: Final[dict[SyndbTable, tuple[SyndbTable, ...]]] = {}
for level in range(1, len(COMPARTMENT_HIERARCHY)):
    parents = []
    for parent_group in COMPARTMENT_HIERARCHY[:level]:
        parents.extend(parent_group)

    level_tables = COMPARTMENT_HIERARCHY[level]

    # For centering `syndb_table_hierarchy_print`
    _total_line_length = sum(len(table.name) for table in level_tables) + (len(level_tables) - 1) * 2
    _max_line = max(_max_line, _total_line_length)

    ascending_parents = tuple(reversed(parents))
    for l_comp in level_tables:
        compartment_to_valid_parents[l_comp] = ascending_parents

syndb_table_hierarchy_print: Final[str] = "\n".join(
    ", ".join(syndb_table.name.lower() for syndb_table in level).center(_max_line) for level in COMPARTMENT_HIERARCHY
)
syndb_table_hierarchy_descending: Final[list[SyndbTable]] = [SyndbTable.NEURON, *compartment_to_valid_parents]

syndb_table_name_to_enum: Final[dict[str, SyndbTable]] = {e.name.lower(): e for e in SyndbTable}
syndb_table_to_name: Final[dict[SyndbTable, str]] = {v: k for k, v in syndb_table_name_to_enum.items()}

syndb_table_supported_str: Final[str] = ", ".join(syndb_table_name_to_enum)
