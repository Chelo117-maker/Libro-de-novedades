# Define la clase Guardia que agrupa operarios y novedades de una franja horaria.

from operario import Operario

class Guardia:
    """
    Representa un turno de trabajo.
    Una guardia tiene una fecha, una franja horaria, un grupo de operarios
    y una lista de novedades registradas durante esa guardia.

    Atributos:
        fecha     (str) : Fecha de la guardia en formato AAAA-MM-DD.
        franja    (str) : Franja horaria: 'Mañana', 'Tarde' o 'Noche'.
        grupo     (list): Lista de objetos Operario que trabajan en la guardia.
        novedades (list): Lista de strings con las novedades de la guardia.
    """
    def __init__(self, fecha, franja_horaria, grupo=None):
        """
        Inicializa una guardia.
        Si no se pasa un grupo, arranca con una lista vacía
        para evitar el bug clásico de Python con listas mutables como valor por defecto.
        """
        self.fecha = fecha               # "2026-06-11"
        self.franja = franja_horaria     # "Mañana" / "Tarde" / "Noche"
        self. grupo= grupo or []         # Lista de objetos Operario
        self.novedades = []              # Lista de strings

    def agregar_operario(self,operario):
        """Agrega un objeto Operario a la lista del grupo del turno."""
        self.grupo.append(operario)

    def agregar_novedad(self, texto):
        """Agrega una novedad como string a la lista de novedades de la guardia"""
        self.novedades.append(texto)

    def a_diccionario(self):
        """
        Convierte el objeto Guardia a un diccionario para guardarlo en JSON.
        Llama a a_diccionario() de cada Operario del grupo usando
        una lista por comprensión.
        """
        return {
        "fecha"    : self.fecha,
        "franja"   : self.franja,
        "grupo"    : [op.a_diccionario() for op in self.grupo],
        "novedades": self.novedades
    }

    def __str__(self):
        """
        Define cómo se muestra la guardia si se hace print(turno).
        Ejemplo: 2026-06-11 - Mañana | Grupo: Carlos Pérez, Ana López
        """
        operarios = ", ".join([op.nombre_completo() for op in self.grupo])
        return f"{self.fecha} - {self.franja} | Grupo: {operarios}"
    
