import datetime
import time

import humanize
from django.utils.translation import ugettext as _


class CountAndTime:

    cat_start_time = None
    cat_number_run = 0
    cat_total_count = 0
    logger = None

    def init_tac(self, total_count, logger=None):
        self.cat_total_count = total_count
        self.cat_start_time = time.time()
        if logger:
            self.logger = logger

    def update_tac(self, number=1):
        self.cat_number_run += number
        percent_done = round((self.cat_number_run / self.cat_total_count) * 100, 1)
        elapsed_time = time.time() - self.cat_start_time
        average_time = elapsed_time / self.cat_number_run
        expected_time_left = int(round((self.cat_total_count - self.cat_number_run) * average_time, 0))
        self.print_tac_message(percent_done, expected_time_left, elapsed_time)

    def print_tac_message(self, percent_done, expected_time_left, elapsed_time):
        delta_running_time = datetime.timedelta(seconds=elapsed_time)
        msg = _("Done: ")
        msg += str(self.cat_number_run) + "/" + str(self.cat_total_count)
        msg += " (" + str(percent_done) + "%)"
        if expected_time_left > 0:
            msg += " - " + _("Expected to be done in") + ": " + humanize.precisedelta(expected_time_left,
                                                                                   minimum_unit="minutes", format="%0.0f")
        msg += " - " + _("Running time") + ": " + humanize.precisedelta(delta_running_time, minimum_unit="minutes",
                                                                        format="%0.0f")

        if self.logger:
            self.logger.info(msg)
        else:
            print(msg)
