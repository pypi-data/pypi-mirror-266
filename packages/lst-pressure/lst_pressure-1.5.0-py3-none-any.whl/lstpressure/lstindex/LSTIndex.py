"""
lstpressure.lstindex.LSTIndex
------

Contains the LSTIndex class, which acts as a wrapper around the IntervalTree class for simplified interval operations.
"""

from intervaltree import IntervalTree, Interval
from perf import track_total_runtime, decorate_all


@decorate_all(track_total_runtime)
class LSTIndex:
    """
    A wrapper around the IntervalTree class for simplified interval operations.

    This class provides convenience methods to insert and query intervals.
    It internally uses the IntervalTree for interval management and query operations.

    Attributes
    ----------
    idx : IntervalTree
        The internal interval tree used for managing intervals.
    tree : IntervalTree
        Alias for the idx attribute.

    Methods
    -------
    get_entries() -> set
        Retrieve all intervals stored in the interval tree.

        Returns
        -------
        set
            A set of (Interval, data) pairs.
    insert(*args)
        Insert an interval into the interval tree.

        This method supports multiple calling patterns:
        - With a single Interval argument.
        - With two arguments specifying the start and end of the interval.
        - With three arguments specifying the start, end, and data associated with the interval.

        Parameters
        ----------
        *args
            Variable length argument list.

        Raises
        ------
        ValueError
            If the arguments don't match any of the accepted input patterns.
    envelop(*args) -> set
        Retrieve intervals that are enveloped by the given interval.

        Parameters
        ----------
        *args
            Variable length argument list.

        Returns
        -------
        set
            A set of (Interval, data) pairs.
    overlap(*args) -> set
        Retrieve intervals that overlap with the given interval.

        Parameters
        ----------
        *args
            Variable length argument list.

        Returns
        -------
        set
            A set of (Interval, data) pairs.
    """

    def __init__(self):
        """
        Initializes an empty interval tree.
        """
        self.idx = IntervalTree()
        self.tree = self.idx

    def get_entries(self) -> set:
        """
        Retrieve all intervals stored in the interval tree.

        Returns
        -------
        set
            A set of (Interval, data) pairs.
        """
        return self.idx.items()

    def insert(self, *args):
        """
        Insert an interval into the interval tree.

        This method supports multiple calling patterns:
        - With a single Interval argument.
        - With two arguments specifying the start and end of the interval.
        - With three arguments specifying the start, end, and data associated with the interval.

        Parameters
        ----------
        *args
            Variable length argument list.

        Raises
        ------
        ValueError
            If the arguments don't match any of the accepted input patterns.
        """
        if len(args) == 1 and isinstance(args[0], Interval):
            interval = args[0]
            self.idx.add(interval)
        elif len(args) == 2:
            begin, end = args
            self.idx.addi(begin, end, {})
        elif len(args) == 3:
            begin, end, data = args
            self.idx.addi(begin, end, data)
        else:
            raise ValueError("Invalid arguments")

    def envelop(self, *args) -> set:
        """
        Retrieve intervals that are enveloped by the given interval.

        Parameters
        ----------
        *args
            Variable length argument list.

        Returns
        -------
        set
            A set of (Interval, data) pairs.
        """
        return self.idx.envelop(*args)

    def overlap(self, *args) -> set:
        """
        Retrieve intervals that overlap with the given interval.

        Parameters
        ----------
        *args
            Variable length argument list.

        Returns
        -------
        set
            A set of (Interval, data) pairs.
        """
        return self.idx.overlap(*args)
