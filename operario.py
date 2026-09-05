# Define la clase Operario que representa a una persona que trabaja en un turno.

class Operario:
    """
    Representa a un operario del sistema.
    
    Atributos:
        legajo   (int): Identificador único del operario.
        nombre   (str): Nombre del operario.
        apellido (str): Apellido del operario.
    """

    def __init__(self, legajo, nombre, apellido):
        self.legajo = legajo
        self.nombre = nombre
        self.apellido = apellido

    def nombre_completo(self):
        return (f"{self.nombre} {self.apellido}")

    def a_diccionario(self):
        """
        Convierte el objeto Operario a un diccionario.
        Necesario para poder guardarlo en el archivo JSON.
        """
        return {
            "legajo"   : self.legajo,
            "nombre"   : self.nombre,
            "apellido" : self.apellido
        }

    def __str__(self):
        """
        Define cómo se muestra el operario si se hace print(operario).
        Ejemplo: [101] Carlos Pérez
        """
        return (f"[{self.legajo}]{self.nombre_completo()}")