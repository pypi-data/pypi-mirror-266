import time

from prettytable import PrettyTable


class StopWatch:
    def __init__(self):
        self._times = []
        self._job_names = []
        self._start_time = None
        self._cur_job_name = None
        self._pt = PrettyTable(["Job", "Time", "Percent"])
        # self.pt.set_style(FRAME)

    def start(self, name=''):
        self._start_time = time.time()
        self._cur_job_name = name

    def stop(self):
        if self._cur_job_name is None:
            raise Exception("Job name is required")
        self._times.append(time.time() - self._start_time)
        self._job_names.append(self._cur_job_name)
        self._cur_job_name = None
        return self._times[-1]

    def avg(self):
        return self.sum() / len(self._times)

    def sum(self):
        return sum(self._times)

    def display(self):
        total = self.sum()
        for i in range(0, len(self._times)):
            self._pt.add_row([self._job_names[i], f'{self._times[i]:.3f}', f'{self._times[i] / total * 100:.2f}%'])
        self._pt.title = f"Sum: {total:.3f}, Avg: {self.avg():.3f}"
        print(self._pt)
