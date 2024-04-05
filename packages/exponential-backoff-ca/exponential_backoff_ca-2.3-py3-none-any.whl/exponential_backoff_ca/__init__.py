"""An Exponential Backoff with Collision Avoidance iterator

This code uses the algorithm described at
https://en.wikipedia.org/wiki/Exponential_backoff#Collision_avoidance
"""

import datetime
import random

## TYPING
from typing import Optional, Iterator
## END OF TYPING

class ExponentialBackoff:
    """The iterator exponential class.

    In each iteration returns the total time (in seconds) to delay. It
    does this by increasing the maximum number of slots each iteration and
    then choosing a random number of slots between 0 and the maximum
    number of slots.

    (See https://en.wikipedia.org/wiki/Exponential_backoff#Collision_avoidance)

    Example:

        import exponentional_backoff_ca

        time_slot_secs = 2.0 # The number of seconds in each time slot.
        num_iterations = 10  # The number of iterations.

        exp_boff = ExponentialBackoff(time_slot_secs, num_iterations)

        for interval in exp_boff:
            print(f"number of seconds in this slot is {interval}")

    """
    def __init__(
            self,
            slot_time:            float,
            number_of_iterations: int,
            max_slots:            Optional[int]   = None,
            limit_value:          Optional[float] = None,
            multiplier:           float = 2.0,
            debug:                bool  = False,
    ):
        """
            slot_time: how long each slot should be (in seconds)

            number_of_iterations: how many iterations before stopping.

            max_slots: set this if you want to put a ceiling on the number of
            slots
        """

        if (slot_time is None):
            msg = "the slot_time parameter must be a positive float"
            raise ValueError(msg)

        if (slot_time < 0.0):
            msg = "the slot_time parameter must be a positive float"
            raise ValueError(msg)

        if (number_of_iterations is None):
            msg = "the number_of_iterations parameter cannot be None"
            raise ValueError(msg)

        self.slot_time         = slot_time
        self.number_of_iterations = number_of_iterations
        self.max_slots         = max_slots
        self.limit_value       = limit_value
        self.multiplier        = multiplier
        self.debug             = debug

        if (self.multiplier < 1.0):
            raise ValueError("multiplier must be a number larger than 1.0")

        # self.counter keeps track of how many iterations we have gone through.
        self.counter = 0

    def progress(self, msg: str) -> None:
        """Send a progress message to standard output."""
        if (self.debug):
            print(f"[progress]: {msg}")

    def __iter__(self) -> Iterator[float]:
        """The iterator initiator"""
        return self

    def __next__(self) -> float:
        """What to do on the next iteration
        """
        if self.counter < self.number_of_iterations:
            self.counter += 1

            self.progress(f"counter is: {self.counter}")

            # Calculate how many available slots. This will be
            # a random integer in [0, (self.multiplier)**(self.counter) - 1].
            available_slots = int(self.multiplier**(self.counter) - 1)
            if ((self.max_slots is not None) and (available_slots > self.max_slots)):
                self.progress(f"max slots limit of {self.max_slots} reached")
                available_slots = self.max_slots

            msg = f"will choose number of slots randomly from [0, {available_slots}]"
            self.progress(msg)

            number_slots = random.randint(0, available_slots)
            self.progress(f"number of slots chosen: {number_slots}")

            wait_time = number_slots * self.slot_time

            if ((self.limit_value is not None) and (wait_time > self.limit_value)):
                msg =f"limit value exceeded; returning limit of {self.limit_value}"
                self.progress(msg)
                wait_time = self.limit_value

            return wait_time

        raise StopIteration
