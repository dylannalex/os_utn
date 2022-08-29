from robin.operating_system.processes import process


class ExecutionsTable:
    def __init__(self):
        self.processes = []
        self.executions = []

    def add_execution(
        self, time: int, process_: process.Process, queue: list[process.Process]
    ) -> None:
        self.executions.append(
            {
                "time": time,
                "process_running": process_.name,
                "remaining_executions": process_.remaining_executions,
                "queue": process.ProcessList.get_processes_names(queue),
            }
        )
        self._update_process(time, process_)
        self._sort_table()

    def _update_process(self, time: int, process_: process.Process) -> None:
        if process_.has_finished():
            process_.finish_time = time

        for i, p in enumerate(self.processes):
            if process_.name == p.name:
                self.processes[i] = process_
                break
        else:
            self.processes.append(process_)

    def _sort_table(self) -> None:
        self.executions = sorted(self.executions, key=lambda d: d["time"])

    @property
    def executions_intervals(self):
        executions_intervals = []
        last_process_running = self.executions[0]["process_running"]
        current_execution = {
            "process": self.executions[0]["process_running"],
            "initial_time": self.executions[0]["time"],
        }
        for execution in self.executions:
            if last_process_running != execution["process_running"]:
                # Add final time to current execution
                current_execution["final_time"] = execution["time"] - 1
                executions_intervals.append(current_execution)

                # Update variables
                current_execution = {
                    "process": execution["process_running"],
                    "initial_time": execution["time"],
                }
                last_process_running = execution["process_running"]

        current_execution["final_time"] = execution["time"]
        executions_intervals.append(current_execution)

        return executions_intervals

    def show_table(self, show_remaining_executions=False) -> None:
        for execution in self.executions:
            time = execution["time"]
            process_running = execution["process_running"]
            remaining_executions = execution["remaining_executions"]
            queue = execution["queue"]

            if show_remaining_executions:
                execution_stats = [
                    f"time: {time} ",
                    f"running: {process_running}  ({remaining_executions} remaining executions)",
                    f"queue: {queue}",
                ]
            else:
                execution_stats = [
                    f"time: {time} ",
                    f"running: {process_running}",
                    f"queue: {queue}",
                ]

            print("\t".join(execution_stats))

    def get_execution_string(self) -> None:
        return "".join([e["process_running"] for e in self.executions])

    def get_first_execution_time(self, process_name: str) -> int:
        for execution in self.executions:
            if process_name in execution["process_running"]:
                return execution["time"]

    def get_last_execution_time(self, process_name: str) -> int:
        for execution in self.executions:
            if (
                process_name in execution["process_running"]
                and execution["remaining_executions"] == 0
            ):
                return execution["time"]

    def __len__(self) -> int:
        return len(self.executions)


class InteractiveSystem:
    def get_return_time(table: ExecutionsTable) -> list[tuple[str, int]]:
        processes_return_time = [
            (p.name, table.get_last_execution_time(p.name) - p.arrival_time + 1)
            for p in table.processes
        ]
        average = sum([wait_time[1] for wait_time in processes_return_time]) / len(
            processes_return_time
        )

        return [processes_return_time, f"Average: {average}"]

    def get_wait_time(table: ExecutionsTable) -> list[tuple[str, int]]:
        processes_wait_time = [
            (p.name, table.get_first_execution_time(p.name) - p.arrival_time)
            for p in table.processes
        ]
        average = sum([wait_time[1] for wait_time in processes_wait_time]) / len(
            processes_wait_time
        )

        return [processes_wait_time, f"Average: {average}"]

    def get_wait_time2(table: ExecutionsTable) -> list[tuple[str, int]]:
        wait_time = [
            (
                p.name,
                table.get_last_execution_time(p.name)
                - p.arrival_time
                + 1
                - p.total_executions,
            )
            for p in table.processes
        ]
        average = sum([wait_time[1] for wait_time in wait_time]) / len(wait_time)

        return [wait_time, f"Average: {average}"]

    def round_robin(
        processes: list[process.Process],
        time_slice,
        with_modification: bool = False,
        with_modification_change_times: list[int] = None,
    ) -> tuple[ExecutionsTable]:
        """
        with_modification state can change over time. with_modification_changes is a
        list the value time instants where the with_modification value changes.
        """
        queue = process.ProcessList.find_first_processes(processes)
        running_process = queue[0]
        slept_processes = [p for p in processes if p not in queue]
        table = ExecutionsTable()
        time = queue[0].arrival_time

        while slept_processes or queue:
            # Execute process
            running_process = queue[0]
            running_process.execute()
            table.add_execution(time, running_process, queue[1::])

            # Update time and "with_modification" state
            time += 1
            if with_modification_change_times:
                for change_time in with_modification_change_times:
                    if time == change_time:
                        if with_modification == True:
                            with_modification = False
                        else:
                            with_modification = True
                        with_modification_change_times.remove(time)
                        break

            # Check if a process activates
            new_processes, slept_processes = process.ProcessList.get_new_processes(
                time, slept_processes
            )

            # Update Queue
            if running_process.has_finished():
                queue.pop(0)
                queue = [*queue, *new_processes]

            elif running_process.consecutive_executions == time_slice:
                running_process.consecutive_executions = 0

                if with_modification:
                    queue = [*queue[1::], *new_processes, running_process]

                if not with_modification:
                    queue = [*queue[1::], running_process, *new_processes]

            else:
                queue = [*queue, *new_processes]

        return table


class BatchSystem:
    def get_wait_time(table: ExecutionsTable) -> list[tuple[str, int]]:
        processes_return_time = [
            (p.name, table.get_last_execution_time(p.name) - p.arrival_time + 1)
            for p in table.processes
        ]
        average = sum([wait_time[1] for wait_time in processes_return_time]) / len(
            processes_return_time
        )

        return [processes_return_time, f"Average: {average}"]

    def shortest_job_first(processes: list[process.Process]):
        first_processes = process.ProcessList.find_first_processes(processes)
        first_processes_sorted = process.ProcessList.sort_processes_by_total_executions(
            first_processes
        )
        running_process = first_processes_sorted[0]
        queue = first_processes_sorted[1::]
        slept_processes = [p for p in processes if p not in first_processes]
        table = ExecutionsTable()
        time = running_process.arrival_time

        while slept_processes or running_process:
            # Execute process
            running_process.execute()
            table.add_execution(time, running_process, queue)
            time += 1

            # Find new processes
            new_processes, slept_processes = process.ProcessList.get_new_processes(
                time, slept_processes
            )
            queue = process.ProcessList.sort_processes_by_total_executions(
                [*queue, *new_processes]
            )
            if running_process.has_finished():
                if queue:
                    running_process = queue[0]
                    queue.pop(0)
                else:
                    running_process = None

        return table

    def first_come_first_served(processes: list[process.Process]):
        first_processes = process.ProcessList.find_first_processes(processes)
        running_process = first_processes[0]
        queue = first_processes[1::]
        slept_processes = [p for p in processes if p not in first_processes]
        table = ExecutionsTable()
        time = running_process.arrival_time

        while queue or running_process:
            running_process.execute()
            table.add_execution(time, running_process, queue)
            time += 1

            queue += process.ProcessList.get_new_processes(time, slept_processes)[0]

            if running_process.has_finished():
                if queue:
                    running_process = queue[0]
                    queue.pop(0)
                else:
                    running_process = None

        return table

    def shortest_remaining_time_next(processes: list[process.Process]):
        first_processes = process.ProcessList.find_first_processes(processes)
        first_processes_sorted = process.ProcessList.sort_processes_by_total_executions(
            first_processes
        )
        running_process = first_processes_sorted[0]
        queue = first_processes_sorted[1::]
        slept_processes = [p for p in processes if p not in first_processes]
        table = ExecutionsTable()
        time = running_process.arrival_time

        while slept_processes or running_process:
            # Execute process
            running_process.execute()
            table.add_execution(time, running_process, queue)
            time += 1

            # Find new processes
            new_processes, slept_processes = process.ProcessList.get_new_processes(
                time, slept_processes
            )
            new_processes_sorted = (
                process.ProcessList.sort_processes_by_total_executions(new_processes)
            )

            # If a new process have less remaining current_executions than the running
            # process, start executing the new process:
            if new_processes:
                if (
                    new_processes_sorted[0].remaining_executions
                    < running_process.remaining_executions
                ):
                    queue.insert(0, running_process)
                    running_process = new_processes_sorted[0]
                    new_processes_sorted.pop(0)

            # Update activated proccesses
            queue = process.ProcessList.sort_processes_by_remaining_executions(
                [*queue, *new_processes_sorted]
            )
            # Check if running process has finished
            if running_process.has_finished():
                if queue:
                    running_process = queue[0]
                    queue.pop(0)
                else:
                    running_process = None

        return table
