# widgets/data_model.py

from dataclasses import dataclass, asdict
from typing import List, Dict, Any

@dataclass
class MaterialSelectionModel:
    ambient: str
    substrate: str

@dataclass
class SystemParametersModel:
    fov: Dict[str, float]
    eyebox: Dict[str, float]
    eye_relief: float
    wavelength: Dict[str, float]
    show_rgb: Dict[str, bool]

@dataclass
class GratingElementModel:
    grating_name: str
    pitch: float
    vector_angle: float
    order: str
    advanced: Dict[str, Any]

@dataclass
class DataModel:
    material_selection: MaterialSelectionModel
    system_parameters: SystemParametersModel
    grating_elements: List[GratingElementModel]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "material_selection": asdict(self.material_selection),
            "system_parameters": asdict(self.system_parameters),
            "grating_elements": [asdict(e) for e in self.grating_elements]
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "DataModel":
        ms = MaterialSelectionModel(**data["material_selection"])
        sp = SystemParametersModel(**data["system_parameters"])
        ge = [GratingElementModel(**e) for e in data.get("grating_elements", [])]
        return DataModel(ms, sp, ge)
