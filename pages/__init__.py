# Agrega la raíz del proyecto al path para que todos los módulos
# dentro de pages/ puedan encontrar components/ correctamente.

import sys
import os

# Sube dos niveles desde pages/ hasta la raíz del proyecto
raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if raiz not in sys.path:
    sys.path.insert(0, raiz)
