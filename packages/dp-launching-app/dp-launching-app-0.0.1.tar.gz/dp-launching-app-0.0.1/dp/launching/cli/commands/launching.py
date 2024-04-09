import argparse
import os.path
import os
import shutil
from pathlib import Path


def main():
    parser = argparse.ArgumentParser("Launching")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="log in verbose mode"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    examples = {
        "basic-starter": "basic",
        "bohrium-starter": "bohrium",
        "dflow-starter": "dflow",
    }
    for k, v in examples.items():
        cmd = subparsers.add_parser(k, help=f"generate a {v} example")
        cmd.add_argument("--output", help="output file path", default="./")

    args = parser.parse_args()

    if args.command in examples:
        try:
            output_path = (
                Path(os.path.abspath(os.path.join(os.getcwd(), args.output)))
                / f"{examples[args.command]}.py"
            )

            dir_path = os.path.dirname(os.path.realpath(__file__))
            source_path = os.path.join(
                dir_path,
                f"scaffold/{examples[args.command]}/{examples[args.command]}.py",
            )
            shutil.copy(source_path, output_path)
            print("generate success")
        except Exception as err:
            print("generate failed: ", err)


if __name__ == "__main__":
    main()
