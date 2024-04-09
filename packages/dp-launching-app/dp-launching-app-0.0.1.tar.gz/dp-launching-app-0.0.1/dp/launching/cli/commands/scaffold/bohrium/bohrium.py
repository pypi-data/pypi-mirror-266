from dp.launching.typing import BaseModel, Field

from dp.launching.typing import InputFilePath, OutputDirectory
from dp.launching.typing import List, Union, Optional, Set, Enum
from dp.launching.typing import String, Int, Boolean, Float, DateTime, Date

from dp.launching.typing.dflow import (
    DflowArgoAPIServer,
    DflowK8sAPIServer,
    DflowAccessToken,
    DflowStorageEndpoint,
    DflowStorageRepository,
)

from dp.launching.typing.bohrium import (
    BohriumJobType,
    BohriumMachineType,
    BohriumPlatform,
    BohriumProjectId,
    BohriumUsername,
    BohriumImage,
)

from dp.launching.cli import to_runner, default_minimal_exception_handler


class IOOptions(BaseModel):
    input_protein: InputFilePath = Field(
        ..., ftypes=["pdb"], description="Protein file path"
    )
    input_ligands: List[InputFilePath] = Field(
        ..., ftypes=["pdb", "sdf"], description="Ligands for Job"
    )
    output_dir: OutputDirectory = Field(
        default="./output"
    )  # default will be override after online


class AlgorithmMode(str, Enum):
    """_summary_"""

    quick = "quick"
    default = "default"


class SetOptional(String, Enum):
    option_i_1 = "option_i_1"
    option_i_2 = "option_i_2"


class AlgorithmOptions(BaseModel):
    mode: AlgorithmMode = Field(default=AlgorithmMode.quick, description="balance mode")
    option_a: Int
    option_b: Float
    option_c: String
    option_d: Boolean
    option_e: Optional[String]
    option_f: DateTime
    option_g: Date
    option_h: SetOptional = Field(description="Only select a single item from a set.")
    option_i: Set[SetOptional] = Field(description="Allows multiple items from a set.")


class BohriumOptions(BaseModel):
    """
    For bohrium Jobs, All variable will be injected
    """

    bohrium_job_type: BohriumJobType = Field(default=BohriumJobType.CONTAINER)
    bohrium_machine_type: BohriumMachineType
    bohrium_project_id: BohriumProjectId
    bohrium_platform: BohriumPlatform
    bohrium_username: BohriumUsername
    bohrium_image: BohriumImage


class GlobalOptions(IOOptions, AlgorithmOptions, BohriumOptions, BaseModel):
    ...


def example_runner(opts: GlobalOptions) -> int:
    status = 0
    from pprint import pprint

    print("Opts:")
    pprint(opts.dict())
    return status


__all__ = ["GlobalOptions"]


def to_parser():
    return to_runner(
        GlobalOptions,
        example_runner,
        version="0.1.0",
        exception_handler=default_minimal_exception_handler,
    )


if __name__ == "__main__":
    import sys

    to_parser()(sys.argv[1:])
