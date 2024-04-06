from typing import Optional, Union

from rich.console import Console
from rich.progress import GetTimeCallable, Progress, ProgressColumn


class TitledProgress(Progress):
    def __init__(
        self,
        *columns: Union[str, ProgressColumn],
        title=None,
        console: Optional[Console] = None,
        auto_refresh: bool = True,
        refresh_per_second: float = 10,
        speed_estimate_period: float = 30,
        transient: bool = False,
        redirect_stdout: bool = True,
        redirect_stderr: bool = True,
        get_time: Optional[GetTimeCallable] = None,
        disable: bool = False,
        expand: bool = False,
        scanned_ips: int = 0,
        ok_ips: int = 0,
    ) -> None:
        self.title = title
        self.scanned_ips = scanned_ips
        self.ok_ips = ok_ips
        super().__init__(
            *columns,
            console=console,
            auto_refresh=auto_refresh,
            refresh_per_second=refresh_per_second,
            speed_estimate_period=speed_estimate_period,
            transient=transient,
            redirect_stdout=redirect_stdout,
            redirect_stderr=redirect_stderr,
            get_time=get_time,
            disable=disable,
            expand=expand,
        )
