from ark_sdk_python.args import ArkArgsFormatter
from ark_sdk_python.models import ArkPollCallback
from ark_sdk_python.models.common import ArkAsyncStatus, ArkAsyncTask


class ArkPollers:
    @staticmethod
    def default_poller() -> ArkPollCallback:
        def poll_callback(async_task: ArkAsyncTask, time_left_seconds: int, async_status: ArkAsyncStatus) -> None:
            from colorama import Fore

            if async_status == ArkAsyncStatus.StartedPolling:
                ArkArgsFormatter.print_colored(async_task.model_dump_json(indent=4), fore=Fore.GREEN)
                ArkArgsFormatter.print_colored(
                    f'[ID: {async_task.task_id}] Started Polling...[Time Remaining: {time_left_seconds}s, '
                    f'Status: {async_task.task_status()}]',
                    fore=Fore.CYAN,
                )
            elif async_status == ArkAsyncStatus.Successful:
                ArkArgsFormatter.print_colored(f'[ID: {async_task.task_id}] Polling Operation Ended Successfully', fore=Fore.GREEN)
            elif async_status == ArkAsyncStatus.Failed:
                ArkArgsFormatter.print_colored(f'[ID: {async_task.task_id}] Polling Operation Failed', fore=Fore.RED)
            elif async_status == ArkAsyncStatus.Timeout:
                ArkArgsFormatter.print_colored(f'[ID: {async_task.task_id}] Polling Operation Timed Out', fore=Fore.YELLOW)
            elif async_status == ArkAsyncStatus.StillPolling and time_left_seconds < 60:
                ArkArgsFormatter.print_colored(
                    f'[ID: {async_task.task_id}] Still Polling...[Time Remaining: {time_left_seconds}s, '
                    f'Status: {async_task.task_status()}]',
                    fore=Fore.YELLOW,
                )
            elif async_status == ArkAsyncStatus.StillPolling:
                ArkArgsFormatter.print_colored(
                    f'[ID: {async_task.task_id}] Still Polling...[Time Remaining: {time_left_seconds}s, '
                    f'Status: {async_task.task_status()}]',
                    fore=Fore.CYAN,
                )
            elif async_status == ArkAsyncStatus.AsyncTaskUpdated:
                ArkArgsFormatter.print_colored(async_task.model_dump_json(indent=4), fore=Fore.GREEN)
                ArkArgsFormatter.print_colored(
                    f'[ID: {async_task.task_id}] Still Polling...[Time Remaining: {time_left_seconds}s, '
                    f'Status: {async_task.task_status()}]',
                    fore=Fore.CYAN,
                )

        return poll_callback

    @staticmethod
    def __spinner_poller(spinner_clazz):
        from progress.spinner import LineSpinner

        def spinner_callback(spinner: LineSpinner, async_status: ArkAsyncStatus, *_) -> None:
            if async_status in [ArkAsyncStatus.Successful, ArkAsyncStatus.Failed]:
                spinner.finish()
            else:
                spinner.next()

        spinner_callback_lambda = lambda a, b, c: spinner_callback(spinner_callback_lambda.spinner, c, a, b)  # pylint: disable=no-member
        spinner_callback_lambda.spinner = spinner_clazz()
        return spinner_callback_lambda

    @staticmethod
    def line_spinner_poller() -> ArkPollCallback:
        from progress.spinner import LineSpinner

        return ArkPollers.__spinner_poller(LineSpinner)

    @staticmethod
    def pixel_spinner_poller() -> ArkPollCallback:
        from progress.spinner import PixelSpinner

        return ArkPollers.__spinner_poller(PixelSpinner)

    @staticmethod
    def moon_spinner_poller() -> ArkPollCallback:
        from progress.spinner import MoonSpinner

        return ArkPollers.__spinner_poller(MoonSpinner)

    @staticmethod
    def spinner_poller() -> ArkPollCallback:
        from progress.spinner import Spinner

        return ArkPollers.__spinner_poller(Spinner)

    @staticmethod
    def pie_spinner_poller() -> ArkPollCallback:
        from progress.spinner import PieSpinner

        return ArkPollers.__spinner_poller(PieSpinner)
