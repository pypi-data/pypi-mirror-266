from .baseshield import BaseShield


class FloatShield(BaseShield):
    def __init__(self, baudrate: int | None = 115200, port: str | None = None) -> None:
        super().__init__(baudrate, port)

        self.actuator_bits = 12

    def calibrate_sensor_reading(self, sensor: int) -> int:
        """Calibrate sensor reading. 0 is taken as the ball being at the bottome of the tube.

        :param sensor: Raw sensor value
        :type sensor: int
        :return: Calibrate sensor value
        :rtype: int
        """
        return - super().calibrate_sensor_reading(sensor)
