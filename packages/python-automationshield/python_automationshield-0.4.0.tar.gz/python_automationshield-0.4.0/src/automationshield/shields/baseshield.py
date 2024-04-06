import serial
import serial.tools.list_ports
import time

from random import randint
from typing import Optional

from ..exception import AutomationShieldException


class BaseShield:
    TEST = 0
    RUN = 1
    STOP = 2

    # Wait time after opening connection
    TIMEOUT = 3

    def __init__(self, baudrate:Optional[int]=115200, port:Optional[str]=None) -> None:
        if port is None:
            port = self.find_arduino()

        self.conn = serial.Serial(port, baudrate=baudrate)
        self.conn.timeout = 1

        self.actuator_bits = 8
        self.potentiometer_bits = 10  # resolution of system ad converter
        self.sensor_bits = 12

        self.zero_reference = 0

    def find_arduino(self) -> str:
        """Get the name of the port that is connected to Arduino. Raises exception if no port was found.

        :raises AutomationShieldException: Raised if no Arduino was found.
        :return: COM port of the Arduino.
        :rtype: str
        """
        ports = serial.tools.list_ports.comports()
        for p in ports:
            if p.manufacturer is not None and "Arduino" in p.manufacturer:
                return p.device

        raise AutomationShieldException("No Arduino Found")

    def firmware_installed(self) -> bool:
        """Check that the correct firmware is installed on the Arduino. This is done by sending flag `BaseShield.TEST` to the Arduino, \
            followed by a random integer. If the Arduino responds with the double and quadruple of the random integer, \
            the firmware is assumed to be correct.

        :return: True if the firmware is assumed correct, False otherwise.
        :rtype: bool.
        """
        with self as shield:
            # set the upper limit of the range to the lower of the potentiometer bits divided by 2 and the sensor bits divided by 4, to guarantee the response fits in the bits.
            v = randint(0, min(2**(self.potentiometer_bits-1), 2**(self.sensor_bits-2)) - 1)
            shield.write(self.TEST, v)
            r1, r2 = shield.read()

        return (r1 == 2*v) and (r2 == 4*v)

    def check_firmware(self):
        if not self.firmware_installed():
            # run install thing here
            raise AutomationShieldException("Wrong firmware installed on the Arduino")


    def convert_potentiometer_reading(self, raw: int) -> float:
        """Convert n-bit potentiometer reading to percentage value.

        :param raw: n-bit potentiometer value.
        :type raw: int
        :return: Potentiometer value as percentage [0, 100].
        :rtype: float
        """
        return raw / (2**self.potentiometer_bits - 1) * 100

    def convert_actuator_input(self, percent: float) -> int:
        """Convert actuator input from percentage to n-bit value.

        :param percent: Actuator percentage.
        :type percent: float
        :return: n-bit number of actuator value.
        :rtype: int
        """
        return percent / 100 * (2**self.actuator_bits - 1)


    def convert_sensor_reading(self, sensor: int) -> int:
        """Convert sensor reading to physical units. Should be implemented on subclasses.

        :param sensor: Raw sensor value
        :type sensor: int
        :return: Sensor value converted to physical units
        :rtype: int
        """
        return sensor

    def calibrate_sensor_reading(self, sensor: int) -> int:
        """Calibrate the sensor reading with the zero reference. Should be implemented on subclass.

        :param sensor: Raw sensor value.
        :type sensor: int
        :return: Calibrated sensor value.
        :rtype: int
        """
        return sensor - self.zero_reference

    def read(self, raw: bool=False) -> tuple[float]:
        """Read data from Arduino. If `raw == False`, the potentiometer value is rescaled to percentages; and the sensor is calibrated with the zero reference and converted to relevant units. This is the default. \
            If `raw == True`, none of that happens and the potentiometer and sensor are returned as n-bit values. No calibration is performed either.

        :param raw: If True, returns raw n-bit readings from potentiometer and sensor. Defaults to False, in which case the potentiometer is converted to percent and the sensor to approppriate units.
        :type raw: bool
        :raises AutomationShieldException: Raised if no data was received. This can happen if there was no `write` command preceding a call to `read`.
        :return: Converted and calibrated potentiometer and sensor readings, in that order.
        :rtype: tuple[float]
        """
        try:
            data = self.conn.read(size=3)

            pot = data[0] // 16 * 256 + data[1]
            sensor = data[0] % 16 * 256 + data[2]

            if raw:
                return pot, sensor

            else:
                return self.convert_potentiometer_reading(pot), self.convert_sensor_reading(self.calibrate_sensor_reading(sensor))

        except IndexError:
            raise AutomationShieldException("No data received from Arduino")

    @staticmethod
    def saturate(value: float, bits: int) -> int:
        """Saturate value between `0` and `2**bits - 1`.

        :param value: Raw value.
        :type value: float
        :param bits: Number of bits.
        :type bits: int
        :return: Saturated value.
        :rtype: int
        """
        return int(min(max((value), 0), 2**bits - 1))

    def write(self, flag: int, actuator: float, raw: bool=False) -> int:
        """Write run/stop flag and actuator value to Arduino. Convert and saturate the actuator value before sending.

        :param flag: `BaseShield.RUN` or `BaseShield.STOP`. The former signals normal running mode, the latter tells the Arduino to stop the motor.
        :type flag: int
        :param actuator: actuator value.
        :type actuator: float
        :param raw: If False, expects actuator as percentage [0, 100]. Value is converted before being sent. If True, expects actuator in range of [0, 2^actuator_bits). Defaults to False.
        :type raw: bool, optional
        :return: Saturated n-bit motor value.
        :rtype: int
        """

        if not raw:
            actuator = self.convert_actuator_input(actuator)

        actuator = self.saturate(actuator, self.actuator_bits)

        if self.actuator_bits > 8:
            bts = [flag, actuator//256, actuator%256]
        else:
            bts = [flag, actuator]

        self.conn.write(bytes(bts))
        return actuator

    def calibrate(self):
        """Read out a zero reference. System should be at rest when calling this method."""
        self.write(self.RUN, 0)
        _, self.zero_reference = self.read(raw=True)

    def stop(self):
        """Send stop signal to Arduino."""
        self.write(self.STOP, 0)

    def open(self):
        """Reset buffers and open connection to Arduino if it is not open already. Wait for `AeroShield.TIMEOUT` seconds to make sure connection is established."""
        if not self.conn.is_open:
            self.conn.open()

        self.conn.reset_input_buffer()
        self.conn.reset_output_buffer()

        time.sleep(self.TIMEOUT)

    def close(self, *args):
        """Close connection to Arduino."""
        self.conn.close()

    def __enter__(self):
        self.open()
        self.calibrate()
        return self

    def __exit__(self, *args):
        self.stop()
        self.close(*args)
