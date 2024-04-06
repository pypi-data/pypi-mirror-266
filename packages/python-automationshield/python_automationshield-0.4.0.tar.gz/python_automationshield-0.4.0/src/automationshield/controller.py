import numpy as np
import numpy.typing as npt
import time

from typing import Optional, Iterable

from .shields.baseshield import BaseShield
from .plotting import LivePlotter


class ShieldController:
    def __init__(self, shield:BaseShield) -> None:
        self.shield = shield

        self.n_base_vars = 5
        # store additional variables to save when running an experiment
        self.extra_hist_vars: dict[str, int] = dict()

        # initiate controller variables
        self.variables()

    def variables(self) -> None:
        """Define variables to be used by the controller or saved during the experiment."""
        pass

    def add_tracked_variable(self, name:str, size: Optional[int]=1) -> dict[str, int]:
        """Add a variable to the list of variables whose value should be tracked during the experiment and returned afterwards.
        Variables should be instance variables of the class, otherwise they won't be accessible!

        :param name: Name of the variable, without 'self.'
        :type name: str
        :param size: Size of the variable, e.g. 3 for a three-dimensional position vector. Defaults to 1, i.e. single values.
        :type size: int, optional
        :return: A copy of the current map of tracked variables and their respective size.
        :rtype: dict[str, int]
        """
        self.extra_hist_vars[name] = size

        return self.extra_hist_vars.copy()

    def controller(self, t: float, dt: float, ref: float, pot: float, sensor: float) -> float:
        """Implement the controller here. You can subclass ShieldController and overwrite the controller.

        :param t: Time since start of run in seconds.
        :type t: float
        :param dt: Length of current time step in seconds.
        :type dt: float
        :param ref: Reference value for the current step.
        :type ref: float
        :param pot: Potentiometer value in percent.
        :type pot: float
        :param sensor: Sensor value, calibrated if applicable.
        :type sensor: float
        :return: input value for actuator. the motor value will be saturated afterwards.
        :rtype: float
        """

        return 0  # actuator value

    def run(self, freq: int, cycles: int, ref: Optional[float | int | Iterable[float|int]]=None, live_plotter: Optional[LivePlotter]=None) -> npt.NDArray[np.float_]:
        """Run the controller on a shield device.

        :param freq: Desired frequency of the loop.
        :type freq: int
        :param cycles: Number of cycles to run the experiment.
        :type cycles: int
        :param ref: The reference to follow. It should have a lenght equal to freq * time or be a single value for a constant reference. Defaults to None, in which case the reference is set to 0.
        :type ref: Optional[float  |  int  |  Iterable[float | int]], optional
        :param live_plotter: Optional LivePlotter instance to use for displaying a live plot, defaults to None
        :type live_plotter: Optional[LivePlotter], optional
        :return: Experiment data. The columns of the array are time, reference, potentiometer, sensor, actuator, and any additional variables in the order they were added.
        :rtype: npt.NDArray[np.float_]
        """

        cntr = 0
        maxcntr = cycles
        period = 1/freq

        # calculate number of additional columns needed
        extra_hist_size = sum(self.extra_hist_vars.values())
        # t1 - tstart, ref, pot, sensor, actuator, any additional variables
        hist = np.zeros((maxcntr, self.n_base_vars + extra_hist_size))

        # create a zero array if no ref is given
        if ref is None:
            ref = np.zeros(maxcntr)

        # expand ref to array if given as integer/float (i.e. constant reference)
        elif isinstance(ref, (int, float)):
            ref = ref * np.ones(maxcntr)

        if live_plotter:
            live_plotter.set_up(cycles, freq)
            plot_process = live_plotter.get_process()
            plot_process.start()

        with self.shield as shield:
            # need an initial write so there's something to read when we get there.
            shield.write(shield.RUN, 0)

            tstart = time.perf_counter()
            t0 = t1 = tstart

            done = False
            while not done:
                try:
                    print(f"\r{cntr}", end="")

                    while (t1 - t0) < period:
                        t1 = time.perf_counter()

                    dt = t1 - t0
                    t0 = t1

                    pot, sensor = shield.read()
                    raw_actuator = self.controller(t1 - tstart, dt, ref[cntr], pot, sensor)
                    actuator = shield.write(shield.RUN, raw_actuator)

                    self._update_hist(hist, cntr, t1 - tstart, ref[cntr], pot, sensor, actuator)

                    if live_plotter:
                        live_plotter.add_data_to_queue(t1 - tstart, ref[cntr], pot, sensor, actuator/(2**shield.actuator_bits/100))

                    cntr += 1
                    if cntr == maxcntr:
                        done = True

                except KeyboardInterrupt:
                    done = True

            print()

        # signals to terminate live plot
        if live_plotter:
            live_plotter.add_data_to_queue(-1, -1, -1, -1, -1)
            plot_process.join()

        return hist

    def _update_hist(self, hist: npt.NDArray[np.float_], cntr: int, t: float, ref: float, pot:float, sensor: float, actuator: float):
        """Update hist array with variables of the current iteration (cntr). If variables were added to `extra_hist_vars`, add them to the hist as well.

        :param hist: array to update.
        :type hist: npt.NDArray[np.float_]
        :param cntr: Iteration counter. Provides the first index to hist.
        :type cntr: int
        :param t: Time.
        :type t: float
        :param ref: Current reference value.
        :type ref: float
        :param sensor: Current pendulum angle
        :type sensor: float
        :param actuator: Current Motor value.
        :type actuator: float
        """
        hist[cntr, 0:self.n_base_vars] = t, ref, pot, sensor, actuator
        total_vars = self.n_base_vars

        for name, size in self.extra_hist_vars.items():
            hist[cntr, total_vars:total_vars+size] = getattr(self, name)

            total_vars += size
