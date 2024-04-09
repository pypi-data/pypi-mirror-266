#
# _progress_indicator.py - DeGirum Python SDK: stdout progress indicator
# Copyright DeGirum Corp. 2022
#
# Contains implementation of progress indicator class printing to stdout
#

import sys
import math


class _ProgressIndicator:
    """Progress indicator helper class.
    Print progress indicator string into stdout.
    """

    def __init__(self, total, width):
        """Contructor.

        total - indicator value corresponding to full length
        width - total number of symbols to use for progress bar string
        """
        self._total = total
        self._width = width
        self._current = 0
        self._sym = int(math.log10(self._total))

    def __enter__(self):
        """Context manager enter handler"""
        self._current = 0
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit handler"""
        sys.stdout.write("\n")

    def advance(self, increment):
        """Advance progress indicator.

        increment - value to advance indicator
        """
        self._current += increment
        progress = float(self._current) / self._total
        ready = int(progress * self._width)
        status = "[{}{}] {:6.2f}% ({:{}d}/{})".format(
            "=" * ready,
            " " * (self._width - ready),
            100 * progress,
            self._current,
            self._sym,
            self._total,
        )
        sys.stdout.write("\r" + status)
        sys.stdout.flush()
