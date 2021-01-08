import datetime
import time

import humanize
from django.contrib.humanize.templatetags.humanize import intcomma
from django.utils.translation import ugettext as _

from bootleg.utils.humanize import get_humanized_memory_usage


class TimeAndCount:

    tac_start_time = None
    tac_number_run = 0
    tac_total_count = 0
    logger = None

    def init_tac(self, total_count, logger=None, print_every_th=10, start_count=None, identifier=None,
                 minimum_print_count=None):
        if not start_count:
            self.tac_start_time = time.time()
        else:
            self.tac_start_time = None
        self.print_every_th = print_every_th
        self.start_count = start_count
        self.identifier = identifier
        self.tac_total_count = total_count
        self.average_time_per_entry = None
        self.minimum_print_count = minimum_print_count
        self.reset_count = None
        self.tac_message = ""
        if logger:
            self.logger = logger

    def update_tac(self, number=1, message=None):
        self.tac_number_run += number
        if not self.tac_start_time and self.tac_number_run == self.start_count:
            self.tac_start_time = time.time()
        if self.should_process_tac():
            percent_done = round((self.tac_number_run / self.tac_total_count) * 100, 1)
            elapsed_time = time.time() - self.tac_start_time
            lines = self.tac_number_run - self.get_count_reduce()
            if lines == 0:
                lines = self.tac_number_run
            average_time = elapsed_time / lines
            expected_time_left = int(round((self.tac_total_count - self.tac_number_run) * average_time, 0))
            self.print_tac_message(percent_done, expected_time_left, elapsed_time, average_time, message=message)

    def reset_tac(self):
        self.tac_start_time = time.time()
        self.reset_count = self.tac_number_run

    def get_count_reduce(self):
        if self.reset_count:
            return self.reset_count
        if self.start_count:
            return self.start_count
        return 0

    def should_process_tac(self):
        if self.minimum_print_count and (self.tac_number_run < self.minimum_print_count):
            return False

        if self.tac_number_run % self.print_every_th == 0:
            return True

        return False

    def print_tac_message(self, percent_done, expected_time_left, elapsed_time, average_time, message=None):
        delta_running_time = datetime.timedelta(seconds=elapsed_time)
        msg = _("Done: ")
        msg += intcomma(self.tac_number_run) + "/" + intcomma(self.tac_total_count)
        msg += " (" + str(percent_done) + "%)"
        if self.start_count:
            msg += " - Started at: [%s]" % intcomma(self.start_count)
        if expected_time_left > 0:
            msg += " - " + _("Expected to be done in") + ": " + humanize.precisedelta(expected_time_left,
                                                                                   minimum_unit="minutes", format="%0.0f")
        msg += " - " + _("Running time") + ": " + humanize.precisedelta(delta_running_time, minimum_unit="minutes",
                                                                        format="%0.0f")
        msg += " - " + _("Avg. time/row") + ": " + str(round(average_time, 5)) + "s"
        msg += " - " + _("Rows/h") + ": " + intcomma(int(100 / average_time * 60))
        msg += " - " + _("Memory usage") + ": " + get_humanized_memory_usage()

        if self.identifier:
            msg += " - Running: %s" % self.identifier
        if message:
            msg += " - " + message

        if self.logger:
            self.logger.info(msg)
        else:
            print(msg)

        self.tac_message = msg
        self.average_time_per_entry = average_time
