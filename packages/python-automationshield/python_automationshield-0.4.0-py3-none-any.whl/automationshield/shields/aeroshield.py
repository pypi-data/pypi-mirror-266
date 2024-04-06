import numpy as np

from .baseshield import BaseShield


class AeroShield(BaseShield):
    @staticmethod
    def convert_sensor_reading(raw: int) -> float:
        """Convert raw angle to degrees.

        :param raw: 12-bit value of angle sensor.
        :type raw: int
        :return: Angle value scaled to degrees.
        :rtype: float
        """
        return raw * 360 / 4096

    @staticmethod
    def raw_angle_to_rad(raw: int) -> float:
        """Convert raw angle to radians.

        :param raw: 12-bit value of angle sensor.
        :type raw: int
        :return: Angle value scaled to radians.
        :rtype: float
        """
        return raw * np.pi / 2048

    def calibrate_sensor_reading(self, raw_angle: int) -> int:
        """Calibrate angle with zero angle. Subtracts zero offset from current angle reading.

        :param raw_angle: Raw 12-bit angle value.
        :type raw_angle: int
        :return: Calibrated angle (12-bit value).
        :rtype: int
        """

        angle = raw_angle - self.zero_reference
        if angle < -1024:
            angle += 4096

        return angle
