import os
from datetime import datetime
from pathlib import Path

import pkg_resources
import PyPDF3
from rich.console import Console

from .args.parser import parse_args
from .utils.progress import TitledProgress

START_DT_STR = datetime.now().strftime(r"%Y%m%d_%H%M%S")
SCRIPTDIR = os.getcwd()


def main():
    console = Console()
    logo = (
        Path(__file__)
        .parent.joinpath("assets")
        .joinpath("ascii_logo.txt")
        .read_text()
    )
    console.print(f"[bold green1]{logo}[/bold green1]")
    try:
        console.print(
            "[bold green1]"
            f"v{pkg_resources.get_distribution('sheetfusion').version}"
            "[bold green1]\n\n"
        )
    except pkg_resources.DistributionNotFound:
        console.print("[bold green1]v0.0.0[bold green1]\n\n")

    args = parse_args()

    cover_sheets_file = Path(args.cover_sheets_file)
    if not cover_sheets_file.exists():
        console.print(
            "[bold red]Error:"
            f" The file '{cover_sheets_file}' does not exist.[/bold red]"
        )
        return

    exam_file = Path(args.exam_file)
    if not exam_file.exists():
        console.print(
            "[bold red]Error:"
            f" The file '{exam_file}' does not exist.[/bold red]"
        )
        return

    output_dir = Path(args.output_dir)
    if not output_dir.exists():
        info_message = (
            "[bold cyan]Info:[/bold cyan]"
            f" [bold white]The directory '{output_dir}' does not exist."
            " Creating it now.[/bold white]"
        )
        console.print(info_message)
        try:
            os.makedirs(output_dir)
        except Exception as e:
            console.print(
                "[bold red]Error:"
                f"Failed to create the directory '{output_dir}'[/bold red]"
            )
            console.print(e)
            return

    with (
        TitledProgress(
            title=f"start: [green]{START_DT_STR}[/green]"
        ) as progress,
        open(cover_sheets_file, "rb") as covers,
        open(exam_file, "rb") as exam,
    ):
        console = progress.console
        cover_reader = PyPDF3.PdfFileReader(covers)
        exam_reader = PyPDF3.PdfFileReader(exam)

        n_exams = cover_reader.numPages
        n_exam_pages = exam_reader.numPages

        bar = "-" * 50

        progress.print(f"[bold cyan]{bar}[/bold cyan]")
        progress.print(
            f"[bold blue]cover_sheets_file:[/bold blue]"
            f" [white]{cover_sheets_file}[/white]"
        )
        progress.print(
            "[bold blue]exam_file:[/bold blue]" f" [white]{exam_file}[/white]"
        )
        progress.print(
            f"[bold blue]output_dir:[/bold blue] [white]{output_dir}[/white]"
        )
        progress.print(
            f"[bold blue]number of exams:[/bold blue] [white]{n_exams}[/white]"
        )
        progress.print(
            "[bold blue]number of exam pages:[/bold blue]"
            f" [white]{n_exam_pages}[/white]"
        )
        progress.print(f"[bold cyan]{bar}[/bold cyan]")
        print("\n")

        all_exams_task = progress.add_task(
            f"All Exam - total = {n_exams} exams", total=n_exams
        )

        n_leading_zeros = len(str(n_exams))
        for i in range(cover_reader.numPages):
            this_exam_task = progress.add_task(
                f"Exam ({i+1:^5}/{n_exams:^5})", total=n_exam_pages
            )
            writer = PyPDF3.PdfFileWriter()

            writer.addPage(cover_reader.getPage(i))

            for j in range(exam_reader.numPages):
                writer.addPage(exam_reader.getPage(j))
                progress.update(this_exam_task, advance=1)

            write_path = output_dir / f"{i+1:0{n_leading_zeros}d}.pdf"
            if write_path.exists() and not args.overwrite:
                console.print(
                    "[bold red]Warning:[/bold red]"
                    f" [white]The file '{write_path}' already exists."
                    " Skipping.[white]"
                )
                progress.update(all_exams_task, advance=1)
                progress.remove_task(this_exam_task)
                continue
            with open(write_path, "wb") as output_pdf:
                writer.write(output_pdf)

            progress.update(all_exams_task, advance=1)
            progress.remove_task(this_exam_task)
