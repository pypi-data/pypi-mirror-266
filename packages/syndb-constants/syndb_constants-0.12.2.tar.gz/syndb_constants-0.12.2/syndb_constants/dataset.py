from enum import IntEnum, auto
from typing import Final

# Relational column names
DATASET_ID_COLUMN_NAME: Final[str] = "dataset_id"
CID_COLUMN_NAME: Final[str] = "cid"

NEURON_ID_COLUMN_NAME: Final[str] = "neuron_id"
PARENT_ID_COLUMN_NAME: Final[str] = "parent_id"
PARENT_ENUM_COLUMN_NAME: Final[str] = "parent_enum"

FORMS_SYNAPSE_WITH_COLUMN_NAME: Final[str] = "forms_synapse_with"

CAVE_ID_COLUMN_NAME: Final[str] = "cave_id"
PRE_SYNAPTIC_TERMINAL_ID_COLUMN_NAME: Final[str] = "pre_id"
POST_SYNAPTIC_TERMINAL_ID_COLUMN_NAME: Final[str] = "post_id"

# Categorical column names
POLARITY_COLUMN_NAME: Final[str] = "polarity"
NEURON_TYPE_COLUMN_NAME: Final[str] = "neuron_type"
CABLE_LENGTH_COLUMN_NAME: Final[str] = "cable_length"
BBOX_COLUMN_NAME: Final[str] = "bounding_box"
IS_TREE_COLUMN_NAME: Final[str] = "is_tree"
N_BRANCHES_COLUMN_NAME: Final[str] = "n_branches"
N_SKELETONS_COLUMN_NAME: Final[str] = "n_skeletons"
N_TREES_COLUMN_NAME: Final[str] = "n_trees"

TERMINAL_COUNT_COLUMN_NAME: Final[str] = "terminal_count"
MITOCHONDRIA_COUNT_COLUMN_NAME: Final[str] = "mitochondria_count"
TOTAL_MITOCHONDRIA_VOLUME_COLUMN_NAME: Final[str] = "total_mitochondria_volume"

NEUROTRANSMITTER_COLUMN_NAME: Final[str] = "neurotransmitter"
MINIMUM_NORMAL_LENGTH_COLUMN_NAME: Final[str] = "minimum_normal_length"
RIBOSOME_COUNT_COLUMN_NAME: Final[str] = "ribosome_count"

# Double Column Names
VOXEL_VOLUME_COLUMN_NAME: Final[str] = "voxel_volume"
VOXEL_RADIUS_COLUMN_NAME: Final[str] = "voxel_radius"
MESH_VOLUME_COLUMN_NAME: Final[str] = "mesh_volume"
MESH_SURFACE_AREA_COLUMN_NAME: Final[str] = "mesh_surface_area"
MESH_AREA_VOLUME_RATIO_COLUMN_NAME: Final[str] = "mesh_area_volume_ratio"
MESH_SPHERICITY_COLUMN_NAME: Final[str] = "mesh_sphericity"
CENTROID_Z_COLUMN_NAME: Final[str] = "centroid_z"
CENTROID_X_COLUMN_NAME: Final[str] = "centroid_x"
CENTROID_Y_COLUMN_NAME: Final[str] = "centroid_y"
CONNECTION_SCORE_COLUMN_NAME: Final[str] = "connection_score"
CLEFT_SCORE_COLUMN_NAME: Final[str] = "cleft_score"
GABA_COLUMN_NAME: Final[str] = "gaba"
ACETYLCHOLINE_COLUMN_NAME: Final[str] = "acetylcholine"
GLUTAMATE_COLUMN_NAME: Final[str] = "glutamate"
OCTOPAMINE_COLUMN_NAME: Final[str] = "octopamine"
SERINE_COLUMN_NAME: Final[str] = "serine"
DOPAMINE_COLUMN_NAME: Final[str] = "da"

# S3 ===========

# Server-side location columns
S3_MESH_LOCATION_COLUMN_NAME: Final[str] = "s3_mesh_location"
S3_SWB_LOCATION_COLUMN_NAME: Final[str] = "s3_swb_location"

# Client-side file-path columns
MESH_PATH_COLUMN_NAME: Final[str] = "mesh_path"
SWB_DF_COLUMN_NAME: Final[str] = "swb_path"


class S3Datacenter(IntEnum):
    NULL = auto()
    WEST = auto()


class S3Instance(IntEnum):
    MESH = auto()
    SWB = auto()


# https://ucsd-prp.gitlab.io/userdocs/storage/ceph-s3/
s3_to_out_url: Final[dict[S3Datacenter, str]] = {
    S3Datacenter.WEST: "https://s3-west.nrp-nautilus.io",
}
s3_to_internal_url: Final[dict[S3Datacenter, str]] = {
    S3Datacenter.WEST: "http://rook-ceph-rgw-nautiluss3.rook",
}
