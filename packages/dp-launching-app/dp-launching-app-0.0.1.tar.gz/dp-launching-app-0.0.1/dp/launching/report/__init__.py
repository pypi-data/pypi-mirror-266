from pathlib import Path
from typing import List, Optional, Union, Dict
from pydantic import BaseModel
import json
from wcmatch import glob


class MetricsChartReportElement(BaseModel):
    metrics_path: Union[str, Path]
    options: Dict
    title: Optional[str] = ""
    type: str = "metrics_chart"
    description: str = ""
    height: str = "240px"


class DockingReportElement(BaseModel):
    protein_path: Union[str, Path]
    ligand_path: Union[str, Path]
    gt_ligand_path: Optional[Union[str, Path]]
    title: str = ""
    description: str = ""
    traj_path: Optional[Union[str, Path]] = None
    type: str = "docking"
    height: str = "240px"


class AutoReportElement(BaseModel):
    path: Union[str, Path, List[Union[str, Path]]]
    title: str = ""
    type: str = "auto"
    description: str = ""
    height: str = "240px"
    render_hints: Optional[List[str]] = None
    kwargs: Optional[Dict] = None

    @classmethod
    def from_patterns(cls, output_dir, patterns, **kwargs):
        return [
            cls(path=i, **kwargs)
            for i in glob.glob(root_dir=output_dir, patterns=patterns)
        ]


class ChartsReportElement(BaseModel):
    step: str
    ncols: int
    charts: List[Dict]


class StreamReportElement(BaseModel):
    type: str = "stream"
    title: Optional[str] = ""
    key: str
    width: str = "100%"
    height: str = "720px"
    description: str = ""


class ChartReportElement(BaseModel):
    options: Dict
    title: Optional[str] = ""
    type: str = "chart"
    description: str = ""


class StepChartsReportElement(BaseModel):
    steps: List[ChartsReportElement]
    title: Optional[str] = ""
    type: str = "step_charts"
    description: str = ""


class ReportSection(BaseModel):
    title: Optional[str] = ""
    elements: List[
        Union[
            StreamReportElement,
            DockingReportElement,
            AutoReportElement,
            StepChartsReportElement,
            MetricsChartReportElement,
            ChartReportElement,
        ]
    ]
    ncols: int = 1
    description: str = ""
    chemical_formula: Optional[List[str]] = []
    smiles: Optional[List[str]] = []
    tags: Optional[List[str]] = []
    metrics_group: str = "default"
    metrics: Optional[Dict[str, Union[str, int, float]]] = {}
    hyperparameters: Optional[Dict[str, Union[str, int, float]]] = {}
    show_overview: bool = False


class Report(BaseModel):
    title: Optional[str] = ""
    sections: List[ReportSection]
    name: str = "index"
    description: Optional[str] = ""

    def save(self, output_dir: Optional[Union[str, Path]] = ""):
        with (Path(output_dir) / f"{self.name}.launching_report").open("w") as f:
            f.write(self.json(indent=2))

    @classmethod
    def load(cls, path: Union[str, Path]):
        with Path(path).open() as f:
            report = json.load(f)
        return cls.parse_obj(report)


if __name__ == "__main__":
    ...
