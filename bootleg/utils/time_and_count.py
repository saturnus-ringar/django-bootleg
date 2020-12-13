import datetime
import time

import humanize
from django.contrib.humanize.templatetags.humanize import intcomma
from django.utils.translation import ugettext as _


class TimeAndCount:

    tac_start_time = None
    tac_number_run = 0
    tac_total_count = 0
    logger = None

    def init_tac(self, total_count, logger=None, print_every_th=10):
        self.tac_total_count = total_count
        self.tac_start_time = time.time()
        self.print_every_th = print_every_th
        if logger:
            self.logger = logger

    def update_tac(self, number=1):
        self.tac_number_run += number
        percent_done = round((self.tac_number_run / self.tac_total_count) * 100, 1)
        elapsed_time = time.time() - self.tac_start_time
        average_time = elapsed_time / self.tac_number_run
        expected_time_left = int(round((self.tac_total_count - self.tac_number_run) * average_time, 0))
        if self.tac_number_run % self.print_every_th == 0:
            self.print_tac_message(percent_done, expected_time_left, elapsed_time, average_time)

    def print_tac_message(self, percent_done, expected_time_left, elapsed_time, average_time):
        delta_running_time = datetime.timedelta(seconds=elapsed_time)
        msg = _("Done: ")
        msg += intcomma(self.tac_number_run) + "/" + intcomma(self.tac_total_count)
        msg += " (" + str(percent_done) + "%)"
        if expected_time_left > 0:
            msg += " - " + _("Expected to be done in") + ": " + humanize.precisedelta(expected_time_left,
                                                                                   minimum_unit="minutes", format="%0.0f")
        msg += " - " + _("Running time") + ": " + humanize.precisedelta(delta_running_time, minimum_unit="minutes",
                                                                        format="%0.0f")
        # hmmm... weird calculations here
        msg += " - " + _("Average time per entry") + ": " + str(round(average_time, 5)) + "s"
        if self.logger:
            self.logger.info(msg)
        else:
            print(msg)
