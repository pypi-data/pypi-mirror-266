from typing import Optional, Callable, Dict
from dataclasses import dataclass, field
from dataclasses_json import config
from ...DataModels.DataModel import DataModel
import numpy as np
from numpy.typing import NDArray
from strenum import StrEnum
from pathlib import Path
import io
from ...Services.Utils import Naming
from ...Services.Storage import Storage


class AppMnemonicCodeEnum(StrEnum):
    NotSet = "NotSet"
    DEPT = "DEPT"  # "Hole depth (MD)"
    GR = "GR"  # "Gamma ray"
    ROP = "ROP"  # "Rate of penetration"
    WOB = "WOB"  # "Weight on bit"
    INCL = "INCL"  # "Inclination"
    AZIM = "AZIM"  # "Azimuth"
    GAS = "GAS"  # "Total Gas"
    BIT = "BIT"  # "Bit depth"
    GRDEPT = "GRDEPT"  # "Gamma ray depth"
    DENS = "DENS"  # "Density"
    RESS = "RESS"  # "Shallow Resistivity"
    RESM = "RESM"  # "Medium Resistivity"
    RESD = "RESD"  # "Deep Resistivity"
    DTC = "DTC"  # "Compressional Sonic Travel Time"
    DTS = "DTS"  # "Shear Sonic Travel Time"
    SP = "SP"  # "Spontaneous Potential"
    PHIN = "PHIN"  # "Neutron Porosity"
    PHID = "PHID"  # "Density Porosity"
    NMR = "NMR"  # "Nuclear Magnetic Resonance"
    PE = "PE"  # "Photoelectric cross section"
    AGR = "AGR"  # "Azimuthal Gamma Ray"
    PHIE = "PHIE"  # "Porosity"
    SW = "SW"  # "Water Saturation"
    VSHL = "VSHL"  # "Shale Content"
    HCP = "HCP"  # "HydocarbonPorosity"
    TIME = "TIME"  # "Time (UTC)"

    @classmethod
    def _missing_(cls, value):
        return AppMnemonicCodeEnum.NotSet


@dataclass(eq=False)
class Curve(DataModel):
    description: Optional[str] = None
    mnemonic: str = ''
    system_mnemonic: AppMnemonicCodeEnum = field(default_factory=lambda: AppMnemonicCodeEnum.NotSet)
    unit: Optional[str] = None
    samples: Optional[np.ndarray] = field(default=None, metadata=config(encoder=lambda x: None, decoder=lambda x: []))
    registered: bool = True

    def __eq__(self, other: object):
        if not isinstance(other, Curve):
            return False

        fields_same = self.description == other.description and self.mnemonic == other.mnemonic and \
                      self.system_mnemonic == other.system_mnemonic and self.unit == other.unit and \
                      self.registered == other.registered
        samples_same = False
        if self.samples is None and other.samples is None:
            samples_same = True
        elif self.samples is not None and other.samples is not None:
            samples_same = np.array_equal(self.samples, other.samples)
        same = fields_same and samples_same
        return same

    def get_v_file_path(self, well_folder: Path, log_name: str) -> Path:
        mne = self.system_mnemonic
        sys_mnemonic = mne if mne is not None and mne != AppMnemonicCodeEnum.NotSet else None
        vendor_mne = self.mnemonic if self.mnemonic is not None and len(self.mnemonic) > 0 else None
        name = sys_mnemonic or vendor_mne or 'Curve'
        safe_name = Naming.make_safe_name(name)
        file_path = well_folder / 'curves' / ('%s-%s-%s.npy' % (log_name, safe_name, self.id))
        return file_path

    def save(self, dir_path: Path, log_name: str, storage: Storage) -> None:
        file_path = self.get_v_file_path(dir_path, log_name)
        storage.save_array(file_path, self.samples)

    def retrieve(self, well_folder: Path, log_name: str, storage: Storage) -> None:
        file_path = self.get_v_file_path(well_folder, log_name)
        self.samples = storage.retrieve_array(file_path)



