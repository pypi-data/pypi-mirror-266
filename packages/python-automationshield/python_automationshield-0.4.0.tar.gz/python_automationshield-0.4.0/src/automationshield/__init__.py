# read version from installed package
from importlib.metadata import version
__version__ = version("python_aeroshield")

from .shields import AeroShield, FloatShield, MagnetoShield, AutomationShieldException, DummyShield
from .controller import ShieldController
