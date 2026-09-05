# Importación de guardias desde archivos externos (.txt, .pdf, .xlsx, .docx).

from nicegui import ui
from operario import Operario
from guardia import Guardia
from components.sidebar import crear_sidebar, crear_header, ESTADO_CONFIG
from components.ayuda import mostrar_dialogo_ayuda
import novedades


def configurar_tema() -> None:
    """Activa el modo oscuro y el color primario."""
    ui.dark_mode().enable()
    ui.colors(primary="#1976D2")


@ui.page("/importar")
def pagina_importar() -> None:
    """Pantalla para importar guardias desde archivos externos."""
    configurar_tema()
    drawer = crear_sidebar("importar")
    crear_header(
        drawer, "Importar novedades", mostrar_ayuda=True, fn_ayuda=mostrar_dialogo_ayuda
    )

    preview = ui.column().classes("full-width")
    datos_parseados: dict = {}

    def parsear_txt(contenido: str) -> dict:
        """
        Lee el contenido de un archivo de texto y extrae los datos de la guardia.
        Soporta las secciones: FECHA, FRANJA, OPERARIOS, HERRAMIENTAS, NOVEDADES.

        Parámetros:
            contenido : Texto completo del archivo leído.

        Retorna:
            Diccionario con fecha, franja, operarios, herramientas y novedades.
        """
        datos: dict = {
            "fecha": "",
            "franja": "",
            "operarios": [],
            "herramientas": [],
            "novedades": [],
        }
        seccion = None
        for linea in contenido.splitlines():
            linea = linea.strip()
            if not linea:
                continue
            if linea.startswith("FECHA:"):
                datos["fecha"] = linea.replace("FECHA:", "").strip()
            elif linea.startswith("FRANJA:"):
                datos["franja"] = linea.replace("FRANJA:", "").strip()
            elif linea == "OPERARIOS:":
                seccion = "operarios"
            elif linea == "HERRAMIENTAS:":
                seccion = "herramientas"
            elif linea == "NOVEDADES:":
                seccion = "novedades"
            elif seccion == "operarios" and " - " in linea:
                partes = linea.split(" - ", 1)
                nc = partes[1].strip().split(" ", 1)
                datos["operarios"].append(
                    {
                        "legajo": partes[0].strip(),
                        "nombre": nc[0],
                        "apellido": nc[1] if len(nc) > 1 else "",
                    }
                )
            elif seccion == "herramientas" and " - " in linea:
                partes = linea.split(" - ", 1)
                datos["herramientas"].append(
                    {
                        "nombre": partes[0].strip(),
                        "estado": partes[1].strip(),
                    }
                )
            elif seccion == "novedades":
                datos["novedades"].append(linea)
        return datos

    def mostrar_preview(datos: dict) -> None:
        """Muestra una vista previa de los datos parseados antes de confirmar."""
        preview.clear()
        datos_parseados.update(datos)
        with preview:
            ui.label("VISTA PREVIA").classes("text-caption text-grey q-mb-sm")
            with ui.card().classes("full-width q-mb-sm"):
                ui.label(f"📅 Fecha: {datos['fecha']}").classes("text-body2")
                ui.label(f"🕐 Franja: {datos['franja']}").classes("text-body2")
            with ui.card().classes("full-width q-mb-sm"):
                ui.label("Operarios:").classes("text-caption text-grey")
                for op in datos["operarios"]:
                    ui.label(
                        f"  [{op['legajo']}] {op['nombre']} {op['apellido']}"
                    ).classes("text-body2")
            with ui.card().classes("full-width q-mb-sm"):
                ui.label("Novedades:").classes("text-caption text-grey")
                for nov in datos["novedades"]:
                    ui.label(f"  • {nov}").classes("text-body2")
            if datos["herramientas"]:
                with ui.card().classes("full-width q-mb-sm"):
                    ui.label("Herramientas:").classes("text-caption text-grey")
                    for h in datos["herramientas"]:
                        cfg = ESTADO_CONFIG.get(h["estado"], ESTADO_CONFIG["Operativa"])
                        with ui.row().classes("items-center q-gutter-sm"):
                            ui.icon(cfg["icon"]).classes(f"text-{cfg['color']}")
                            ui.label(f"{h['nombre']} — {h['estado']}").classes(
                                "text-body2"
                            )
            ui.button("✓ Confirmar e importar", on_click=confirmar_importacion).props(
                "color=positive rounded"
            ).classes("full-width q-mt-sm")

    def confirmar_importacion() -> None:
        """Registra la guardia importada y sus herramientas en el sistema."""
        datos = datos_parseados
        if not datos.get("fecha") or not datos.get("franja"):
            ui.notify("El archivo no tiene fecha o franja válida", color="negative")
            return
        g = Guardia(datos["fecha"], datos["franja"])
        for op in datos["operarios"]:
            g.agregar_operario(Operario(op["legajo"], op["nombre"], op["apellido"]))
        for nov in datos["novedades"]:
            g.agregar_novedad(nov)
        novedades.agregar_guardia(g)
        for h in datos.get("herramientas", []):
            novedades.agregar_herramienta(h["nombre"], h["estado"])
        ui.notify("Guardia importada correctamente ✓", color="positive")
        preview.clear()
        ui.navigate.to("/")

    with ui.column().classes("q-pa-md full-width"):
        ui.label("SUBIR ARCHIVO DE NOVEDADES").classes("text-caption text-grey")
        with ui.card().classes("full-width q-mb-md"):
            ui.label(
                "Formatos soportados: .txt (recomendado), .pdf, .xlsx y .docx"
            ).classes("text-caption text-grey q-mb-sm")

            async def procesar_archivo(e) -> None:
                """
                Lee el archivo subido según su extensión y lo parsea.
                Soporta .txt, .pdf, .xlsx y .docx.
                """
                archivo = e.files[0] if e.files else None
                if not archivo:
                    return
                nombre = archivo.name.lower()
                contenido = ""

                if nombre.endswith(".txt"):
                    contenido = archivo.content.read().decode("utf-8", errors="ignore")

                elif nombre.endswith(".pdf"):
                    try:
                        import io
                        import pdfplumber

                        with pdfplumber.open(io.BytesIO(archivo.content.read())) as pdf:
                            contenido = "\n".join(
                                p.extract_text() or "" for p in pdf.pages
                            )
                    except ImportError:
                        ui.notify(
                            "Instalá pdfplumber: pip install pdfplumber",
                            color="warning",
                        )
                        return

                elif nombre.endswith(".xlsx"):
                    try:
                        import io
                        import openpyxl

                        wb = openpyxl.load_workbook(io.BytesIO(archivo.content.read()))
                        ws = wb.active
                        contenido = "\n".join(
                            " - ".join(str(c.value or "") for c in row)
                            for row in ws.iter_rows()
                        )
                    except ImportError:
                        ui.notify(
                            "Instalá openpyxl: pip install openpyxl", color="warning"
                        )
                        return

                elif nombre.endswith(".docx"):
                    try:
                        import io
                        import docx

                        doc = docx.Document(io.BytesIO(archivo.content.read()))
                        contenido = "\n".join(p.text for p in doc.paragraphs)
                    except ImportError:
                        ui.notify(
                            "Instalá python-docx: pip install python-docx",
                            color="warning",
                        )
                        return

                else:
                    ui.notify(
                        "Formato no soportado. Usá .txt, .pdf, .xlsx o .docx",
                        color="negative",
                    )
                    return

                if contenido.strip():
                    mostrar_preview(parsear_txt(contenido))
                else:
                    ui.notify("No se pudo leer contenido del archivo", color="negative")

            ui.upload(
                label="Seleccionar archivo",
                on_upload=procesar_archivo,
                auto_upload=True,
            ).props('accept=".txt,.pdf,.xlsx,.docx"').classes("full-width")

        preview
