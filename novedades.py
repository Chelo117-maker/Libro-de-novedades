# Contiene las funciones que manejan la persistencia de datos en el archivo JSON.
# Es la capa entre las clases (operario, guardia) y el almacenamiento (datos.json).

import json
import os

ARCHIVO_GUARDIAS = "datos.json"
ARCHIVO_OPERARIOS = "operarios.json"

# ── Guardias ──────────────────────────────────────────────────────────────────


def cargar_datos():
    """Lee el archivo JSON y devuelve la lista de guardias. Si no existe, devuelve lista vacía."""
    if not os.path.exists(ARCHIVO_GUARDIAS):
        return []
    with open(ARCHIVO_GUARDIAS, "r", encoding="utf-8") as f:
        return json.load(f)


def guardar_datos(guardias):
    """Sobreescribe el archivo JSON con la lista de guardias actualizada."""
    with open(ARCHIVO_GUARDIAS, "w", encoding="utf-8") as f:
        json.dump(guardias, f, indent=4, ensure_ascii=False)


def agregar_guardia(guardia):
    """Convierte un objeto Guardia a diccionario y lo guarda en el JSON."""
    guardias = cargar_datos()
    guardias.append(guardia.a_diccionario())
    guardar_datos(guardias)


def buscar_por_fecha(fecha):
    """Devuelve guardias que coincidan exactamente con la fecha dada."""
    guardias = cargar_datos()
    return [g for g in guardias if g["fecha"] == fecha]


def buscar_por_operario(texto):
    """
    Busca guardias donde el nombre, apellido O legajo del operario
    contenga el texto buscado. No distingue mayúsculas.
    """
    guardias = cargar_datos()
    resultado = []
    busqueda = str(texto).lower().strip()
    for g in guardias:
        for op in g["grupo"]:
            nombre_completo = f"{op['nombre']} {op['apellido']}".lower()
            legajo = str(op["legajo"]).lower()
            if busqueda in nombre_completo or busqueda in legajo:
                resultado.append(g)
                break
    return resultado


def buscar_por_palabra(palabra):
    """
    Busca guardias donde cualquier novedad contenga la palabra clave.
    No distingue mayúsculas ni minúsculas.
    Antes fallaba si las novedades estaban vacías.
    """
    guardias = cargar_datos()
    texto = palabra.lower().strip()
    return [
        g
        for g in guardias
        if any(texto in nov.lower() for nov in g.get("novedades", []))
    ]


def eliminar_guardia(fecha, franja):
    """Elimina la guardia que coincida con fecha y franja."""
    guardias = cargar_datos()
    nuevas = [
        g for g in guardias if not (g["fecha"] == fecha and g["franja"] == franja)
    ]
    guardar_datos(nuevas)


# ── Operarios fijos ───────────────────────────────────────────────────────────


def cargar_operarios():
    """Lee el archivo de operarios fijos. Si no existe, devuelve lista vacía."""
    if not os.path.exists(ARCHIVO_OPERARIOS):
        return []
    with open(ARCHIVO_OPERARIOS, "r", encoding="utf-8") as f:
        return json.load(f)


def guardar_operarios(operarios):
    """Sobreescribe el archivo de operarios con la lista actualizada."""
    with open(ARCHIVO_OPERARIOS, "w", encoding="utf-8") as f:
        json.dump(operarios, f, indent=4, ensure_ascii=False)


def agregar_operario_fijo(operario):
    """
    Agrega un operario al registro fijo.
    Verifica que el legajo no esté duplicado antes de guardar.
    """
    operarios = cargar_operarios()
    legajos = [op["legajo"] for op in operarios]
    if operario.a_diccionario()["legajo"] in legajos:
        return False  # Ya existe
    operarios.append(operario.a_diccionario())
    guardar_operarios(operarios)
    return True


def eliminar_operario_fijo(legajo):
    """Elimina el operario con el legajo indicado del registro fijo."""
    operarios = cargar_operarios()
    nuevos = [op for op in operarios if op["legajo"] != legajo]
    guardar_operarios(nuevos)


# ── Herramientas ──────────────────────────────────────────────────────────────

ARCHIVO_HERRAMIENTAS = "herramientas.json"


def cargar_herramientas():
    """Lee el archivo de herramientas. Si no existe, devuelve lista vacía."""
    if not os.path.exists(ARCHIVO_HERRAMIENTAS):
        return []
    with open(ARCHIVO_HERRAMIENTAS, "r", encoding="utf-8") as f:
        return json.load(f)


def guardar_herramientas(herramientas):
    """Sobreescribe el archivo de herramientas con la lista actualizada."""
    with open(ARCHIVO_HERRAMIENTAS, "w", encoding="utf-8") as f:
        json.dump(herramientas, f, indent=4, ensure_ascii=False)


def agregar_herramienta(nombre, estado="Operativa"):
    """
    Agrega una herramienta al registro.
    Estado puede ser: 'Operativa', 'Defectuosa', 'Faltante'
    """
    herramientas = cargar_herramientas()
    herramientas.append({"nombre": nombre, "estado": estado})
    guardar_herramientas(herramientas)


def actualizar_estado_herramienta(nombre, nuevo_estado):
    """Actualiza el estado de una herramienta existente por nombre."""
    herramientas = cargar_herramientas()
    for h in herramientas:
        if h["nombre"].lower() == nombre.lower():
            h["estado"] = nuevo_estado
            break
    guardar_herramientas(herramientas)


def eliminar_herramienta(nombre):
    """Elimina una herramienta del registro por nombre."""
    herramientas = cargar_herramientas()
    nuevas = [h for h in herramientas if h["nombre"].lower() != nombre.lower()]
    guardar_herramientas(nuevas)


def buscar_herramienta_similar(nombre_buscado, umbral=80):
    """
    Busca una herramienta por nombre tolerando errores tipográficos
    y diferencias de mayúsculas/minúsculas.

    Parámetros:
        nombre_buscado (str): El nombre que escribió el usuario.
        umbral (int): Porcentaje mínimo de similitud (0-100).
                      80 es un buen balance entre flexible y preciso.

    Retorna:
        dict con tres claves:
            'exacta'    : la herramienta si hubo coincidencia exacta
            'similares' : lista de herramientas parecidas si no fue exacta
            'ninguna'   : True si no se encontró nada similar
    """
    from rapidfuzz import fuzz, process

    herramientas = cargar_herramientas()
    if not herramientas:
        return {"exacta": None, "similares": [], "ninguna": True}

    nombres = [h["nombre"] for h in herramientas]
    busqueda = nombre_buscado.strip().lower()

    # Primero buscar coincidencia exacta ignorando mayúsculas
    for h in herramientas:
        if h["nombre"].lower() == busqueda:
            return {"exacta": h, "similares": [], "ninguna": False}

    # Si no hay exacta, buscar similares con fuzzy matching
    resultados = process.extract(
        nombre_buscado,
        nombres,
        scorer=fuzz.WRatio,  # WRatio es el más flexible, combina varios métodos
        limit=3,  # Devuelve las 3 más parecidas
    )

    similares = [
        next(h for h in herramientas if h["nombre"] == nombre)
        for nombre, score, _ in resultados
        if score >= umbral
    ]

    if similares:
        return {"exacta": None, "similares": similares, "ninguna": False}

    return {"exacta": None, "similares": [], "ninguna": True}


def buscar_operario_similar(nombre_buscado, umbral=80):
    """
    Busca un operario por nombre o apellido tolerando errores tipográficos
    y diferencias de mayúsculas/minúsculas.

    Parámetros:
        nombre_buscado (str): Nombre o apellido que escribió el usuario.
        umbral (int): Porcentaje mínimo de similitud (0-100).

    Retorna:
        dict con tres claves:
            'exacto'    : el operario si hubo coincidencia exacta
            'similares' : lista de operarios parecidos si no fue exacto
            'ninguno'   : True si no se encontró nada similar
    """
    from rapidfuzz import fuzz, process

    operarios = cargar_operarios()
    if not operarios:
        return {"exacto": None, "similares": [], "ninguno": True}

    # Construir lista de nombres completos para comparar
    nombres_completos = [f"{op['nombre']} {op['apellido']}" for op in operarios]
    busqueda = nombre_buscado.strip().lower()

    # Primero buscar coincidencia exacta ignorando mayúsculas
    for op in operarios:
        nombre_completo = f"{op['nombre']} {op['apellido']}".lower()
        if nombre_completo == busqueda or op["legajo"] == nombre_buscado.strip():
            return {"exacto": op, "similares": [], "ninguno": False}

    # Si no hay exacta, buscar similares con fuzzy matching
    resultados = process.extract(
        nombre_buscado, nombres_completos, scorer=fuzz.WRatio, limit=3
    )

    similares = [operarios[idx] for _, score, idx in resultados if score >= umbral]

    if similares:
        return {"exacto": None, "similares": similares, "ninguno": False}

    return {"exacto": None, "similares": [], "ninguno": True}


# ── Grupos de trabajo ─────────────────────────────────────────────────────────

ARCHIVO_GRUPOS = "grupos.json"


def cargar_grupos():
    """Lee el archivo de grupos. Si no existe devuelve estructura vacía."""
    if not os.path.exists(ARCHIVO_GRUPOS):
        return {"grupos": [], "cambios": []}
    with open(ARCHIVO_GRUPOS, "r", encoding="utf-8") as f:
        return json.load(f)


def guardar_grupos(datos):
    """Sobreescribe el archivo de grupos con los datos actualizados."""
    with open(ARCHIVO_GRUPOS, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)


def agregar_grupo(nombre, legajos_base):
    """
    Crea un grupo base con nombre y lista de legajos.
    Verifica que no exista un grupo con el mismo nombre.
    """
    datos = cargar_grupos()
    if any(g["nombre"].lower() == nombre.lower() for g in datos["grupos"]):
        return False
    datos["grupos"].append(
        {"nombre": nombre, "miembros_base": legajos_base, "activo": True}
    )
    guardar_grupos(datos)
    return True


def eliminar_grupo(nombre):
    """Elimina un grupo por nombre."""
    datos = cargar_grupos()
    datos["grupos"] = [
        g for g in datos["grupos"] if g["nombre"].lower() != nombre.lower()
    ]
    guardar_grupos(datos)


def registrar_cambio_grupo(
    fecha, franja, nombre_grupo, legajo, tipo, motivo, reemplazado_por=None
):
    """
    Registra un cambio en la composición del grupo para una guardia.

    Parámetros:
        fecha          : Fecha de la guardia afectada
        franja         : Franja de la guardia
        nombre_grupo   : Nombre del grupo
        legajo         : Legajo del operario que cambia
        tipo           : 'ausencia' o 'incorporacion'
        motivo         : Razón del cambio
        reemplazado_por: Legajo del reemplazo (opcional)
    """
    datos = cargar_grupos()
    datos["cambios"].append(
        {
            "fecha": fecha,
            "franja": franja,
            "grupo": nombre_grupo,
            "legajo": legajo,
            "tipo": tipo,
            "motivo": motivo,
            "reemplazado_por": reemplazado_por,
        }
    )
    guardar_grupos(datos)


def obtener_miembros_guardia(nombre_grupo, fecha, franja):
    """
    Devuelve la lista de legajos activos para un grupo en una guardia específica,
    aplicando los cambios registrados (ausencias e incorporaciones).
    """
    datos = cargar_grupos()
    grupo = next((g for g in datos["grupos"] if g["nombre"] == nombre_grupo), None)
    if not grupo:
        return []

    miembros = set(grupo["miembros_base"])

    # Aplicar cambios para esa fecha y franja
    for cambio in datos["cambios"]:
        if (
            cambio["fecha"] == fecha
            and cambio["franja"] == franja
            and cambio["grupo"] == nombre_grupo
        ):
            if cambio["tipo"] == "ausencia":
                miembros.discard(cambio["legajo"])
                if cambio.get("reemplazado_por"):
                    miembros.add(cambio["reemplazado_por"])
            elif cambio["tipo"] == "incorporacion":
                miembros.add(cambio["legajo"])

    return list(miembros)


def exportar_guardia_pdf(
    guardia_dict: dict, ruta_salida: str = "guardia_exportada.pdf"
) -> str:
    """
    Genera un PDF con los datos completos de una guardia.

    Parámetros:
        guardia_dict : Diccionario con fecha, franja, grupo y novedades.
        ruta_salida  : Nombre del archivo PDF a generar.

    Retorna:
        Ruta del archivo generado.
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm

    doc = SimpleDocTemplate(ruta_salida, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    titulo_style = ParagraphStyle(
        "titulo", parent=styles["Heading1"], fontSize=16, spaceAfter=6
    )
    subtitulo_style = ParagraphStyle(
        "subtitulo",
        parent=styles["Heading2"],
        fontSize=12,
        spaceAfter=4,
        textColor=colors.HexColor("#1976D2"),
    )
    normal_style = styles["Normal"]
    pie_style = ParagraphStyle(
        "pie", parent=styles["Normal"], fontSize=8, textColor=colors.grey
    )

    # Encabezado
    story.append(Paragraph("Libro de Novedades", titulo_style))
    hora = guardia_dict.get("hora", "")
    story.append(
        Paragraph(
            f"Guardia del {guardia_dict['fecha']} — {guardia_dict['franja']}",
            subtitulo_style,
        )
    )
    story.append(Spacer(1, 0.5 * cm))

    # Operarios
    story.append(Paragraph("Operarios de la guardia:", subtitulo_style))
    if guardia_dict["grupo"]:
        for op in guardia_dict["grupo"]:
            story.append(
                Paragraph(
                    f"• [{op['legajo']}] {op['nombre']} {op['apellido']}", normal_style
                )
            )
    else:
        story.append(Paragraph("Sin operarios registrados.", normal_style))
    story.append(Spacer(1, 0.5 * cm))

    # Novedades
    story.append(Paragraph("Novedades registradas:", subtitulo_style))
    if guardia_dict["novedades"]:
        for nov in guardia_dict["novedades"]:
            story.append(Paragraph(f"• {nov}", normal_style))
    else:
        story.append(Paragraph("Sin novedades registradas.", normal_style))
    story.append(Spacer(1, 0.5 * cm))

    # Pie
    story.append(
        Paragraph(
            f"Generado por Libro de Novedades — {guardia_dict['fecha']}", pie_style
        )
    )

    doc.build(story)
    return ruta_salida
