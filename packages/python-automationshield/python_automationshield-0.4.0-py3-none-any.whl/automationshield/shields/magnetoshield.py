from .baseshield import BaseShield


class MagnetoShield(BaseShield):
    def __init__(self, baudrate: int | None = 115200, port: str | None = None) -> None:
        super().__init__(baudrate, port)

        self.actuator_bits = 12
        self.sensor_bits = 10

    def convert_sensor_reading(self, sensor: int) -> float:
        """Converts the n-bit sensor reading of the Hall effect sensor to Gauss. \
            The constants in this method are for release 4 of the MagnetoShield.

        :param sensor: Raw sensor value.
        :type sensor: int
        :return: Sensor value in Gauss.
        :rtype: int
        """
        return (2.5 - sensor*(3.3/(2**self.potentiometer_bits - 1)))*800
