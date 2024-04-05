from ..DataModel import DataModel
from dataclasses import dataclass, field
from typing import Optional, ClassVar, List
from datetime import datetime
from ...DataModels.Completions.DepthFeature import DepthFeature
from ...DataModels.Completions.Plug import Plug
from ...DataModels.Helpers import MakeIsodataOptionalField


@dataclass
class Stage(DataModel):
    # Represents a ZoneVu frac stage data object on a wellbore
    sequence_num: int = 0
    key: str = ''
    gap: bool = False
    note: str = ''
    start_date: Optional[datetime] = MakeIsodataOptionalField()
    duration: Optional[float] = None
    toe_md: float = 0
    heel_md: float = 0

    screened_out: bool = False
    frac_hit: bool = False
    num_clusters: Optional[int] = None
    proppant_weight: Optional[float] = None
    water_volume: Optional[float] = None

    pressure: Optional[float] = None
    bottom_pressure: Optional[float] = None
    slurry_rate: Optional[float] = None
    breakdown_pressure: Optional[float] = None
    closure_pressure: Optional[float] = None
    avg_surface_pressure: Optional[float] = None
    max_surface_pressure: Optional[float] = None
    max_bottom_pressure: Optional[float] = None
    isip_pressure: Optional[float] = None
    closure_gradient: Optional[float] = None
    frac_gradient: Optional[float] = None
    tvd_depth: Optional[float] = None
    slurry_volume: Optional[float] = None
    avg_proppant_conc: Optional[float] = None
    max_proppant_conc: Optional[float] = None
    user_param_values: List[Optional[float]] = field(default_factory=list[Optional[float]])

    toe_plug: Optional[Plug] = None
    depth_features: List[DepthFeature] = field(default_factory=list[DepthFeature])

    def copy_ids_from(self, source: DataModel):
        super().copy_ids_from(source)
        if isinstance(source, Stage):
            if source.toe_plug is not None and self.toe_plug is not None:
                self.toe_plug.copy_ids_from(source.toe_plug)
            DataModel.merge_lists(self.depth_features, source.depth_features)
