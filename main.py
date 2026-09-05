# Punto de entrada de la aplicación.
# Importa todas las páginas y arranca el servidor NiceGUI.

import sys
import os

# Agrega la raíz del proyecto al path para que todos los módulos
# puedan encontrar las carpetas components/ y pages/ correctamente.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nicegui import ui

from pages import inicio  # noqa: F401
from pages import nueva_guardia  # noqa: F401
from pages import ver  # noqa: F401
from pages import buscar  # noqa: F401
from pages import operarios  # noqa: F401
from pages import herramientas  # noqa: F401
from pages import importar  # noqa: F401
from pages import grupos  # noqa: F401

ui.run(title="Libro de Novedades", dark=True)
