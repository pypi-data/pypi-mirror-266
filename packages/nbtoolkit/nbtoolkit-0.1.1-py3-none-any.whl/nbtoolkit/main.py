# Copyright (c) 2024 Jake Walker
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import base64
import json
import os
import zipfile
from datetime import datetime, timedelta
from typing import Optional

import requests
import typer
from rich.console import Console
from rich.progress import Progress, track
from typing_extensions import Annotated

app = typer.Typer()
console = Console()


def upload_file(filename: str):
    expiry = datetime.now() + timedelta(hours=8)
    with Progress() as progress:
        task = progress.add_task("Uploading...", total=None)
        with open(filename, "rb") as f:
            res = requests.post(
                "https://vh7.uk/api/upload",
                data={"expires": int(expiry.timestamp() * 1000)},
                files={"file": (os.path.basename(filename), f)},
            )

        res.raise_for_status()
        progress.update(task, completed=1, total=1)

    console.print(f"Uploaded to VH7: https://vh7.uk/{res.json()['id']}", style="green")


@app.command()
def extract_images(
    filename: Annotated[
        str, typer.Argument(help="The filename of the notebook to extract images from.")
    ],
    output_dir: Annotated[
        str, typer.Option("--output", "-o", help="The name of the directory to output images to.")
    ] = "out",
    zip_output: Annotated[
        bool, typer.Option("--zip", "-z", help="Output extracted images into a zip.")
    ] = False,
    upload: Annotated[
        bool,
        typer.Option("--upload", help="Upload the output to VH7. This will also zip the output."),
    ] = False,
    delete: Annotated[
        bool,
        typer.Option(
            "--rm",
            help="Delete the output after completion. This is useful when used in conjunction with "
            "upload.",
        ),
    ] = False,
):
    """Extract images from a Jupyter Notebook."""

    if upload:
        zip_output = True

    full_output_dir = os.path.abspath(output_dir)
    os.makedirs(full_output_dir, exist_ok=True)

    with open(filename, "r") as f:
        data = json.load(f)

    assert data["nbformat"] == 4

    out_zip: Optional[zipfile.ZipFile] = None

    if zip_output:
        out_zip = zipfile.ZipFile(f"{full_output_dir}.zip", "w")

    for cell_index, cell in track(enumerate(data["cells"]), description="Processing cells..."):
        cell_id = cell.get("id", str(cell_index))
        i = 0

        for output in cell.get("outputs", []):
            output_data = output.get("data", {})

            if "image/png" in output_data:
                image_filename = f"{cell_id.split('-')[0]}_{i}.png"
                image_data = base64.b64decode(output_data["image/png"])
                if out_zip is None:
                    with open(os.path.join(output_dir, image_filename), "wb") as f:
                        f.write(image_data)
                else:
                    out_zip.writestr(image_filename, image_data)
                i += 1

    if out_zip is not None:
        out_zip.close()
        console.print(f"Extracted and zipped images to {full_output_dir}.zip", style="green")
    else:
        console.print(f"Extracted images to {full_output_dir}", style="green")

    if upload:
        upload_file(f"{full_output_dir}.zip")

    if delete:
        if zip_output:
            os.remove(f"{full_output_dir}.zip")
        else:
            os.removedirs(full_output_dir)

        console.print("Removed output", style="green")
