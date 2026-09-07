# Lista completa de guardias con filtro por franja y exportación a PDF.

from nicegui import ui
from components.sidebar import crear_sidebar, crear_header, FRANJA_COLOR
from components.ayuda import mostrar_dialogo_ayuda
import novedades


def configurar_tema() -> None:
    """Activa el modo oscuro y el color primario."""
    ui.dark_mode().enable()
    ui.colors(primary="#1976D2")


def _render_guardia(g: dict) -> None:
    """
    Renderiza una tarjeta de guardia con fecha, novedades, grupo y botón PDF.

    Parámetros:
        g : Diccionario con los datos de la guardia.
    """
    with ui.card().classes("full-width q-mb-sm"):
        with ui.row().classes("items-center justify-between full-width"):
            with ui.column().classes("col"):
                ui.label(f"{g['fecha']}  {g.get('hora', '')}").classes(
                    "text-caption text-grey"
                )
                ui.label(
                    " / ".join(g["novedades"]) if g["novedades"] else "Sin novedades"
                ).classes("text-body2")
                ui.label(
                    ", ".join(f"{o['nombre']} {o['apellido']}" for o in g["grupo"])
                ).classes("text-caption text-grey")
            with ui.row().classes("items-center q-gutter-xs"):
                ui.badge(
                    g["franja"],
                    color=FRANJA_COLOR.get(g["franja"].lower(), "grey"),
                )

                def exportar(g: dict = g) -> None:
                    """Genera el PDF y lo ofrece para descarga."""
                    try:
                        nombre_pdf = f"guardia_{g['fecha']}_{g['franja']}.pdf"
                        ruta = novedades.exportar_guardia_pdf(g, nombre_pdf)
                        ui.download(src=ruta, filename=nombre_pdf)
                        ui.notify(f"PDF generado: {nombre_pdf}", color="positive")
                    except Exception as e:
                        ui.notify(f"Error al generar PDF: {str(e)}", color="negative")

                ui.button(icon="picture_as_pdf", on_click=exportar).props(
                    "flat round color=negative"
                ).tooltip("Exportar a PDF")


@ui.page("/ver")
def pagina_ver() -> None:
    """Pantalla que lista todas las guardias con filtro por franja."""
    configurar_tema()
    drawer = crear_sidebar("ver")
    crear_header(
        drawer, "Todas las guardias", mostrar_ayuda=True, fn_ayuda=mostrar_dialogo_ayuda
    )

    with ui.column().classes("q-pa-md full-width"):

        # Filtro por franja
        ui.label("FILTRAR POR FRANJA").classes("text-caption text-grey")
        with ui.card().classes("full-width q-mb-md"):
            filtro = ui.select(
                ["Todas", "Mañana", "Tarde", "Noche"], value="Todas", label="Franja"
            ).classes("full-width")
            lista_filtrada = ui.column().classes("full-width q-mt-sm")

            def aplicar_filtro() -> None:
                """Filtra las guardias por franja y las muestra."""
                lista_filtrada.clear()
                guardias = novedades.cargar_datos()
                if filtro.value != "Todas":
                    guardias = [g for g in guardias if g["franja"] == filtro.value]
                with lista_filtrada:
                    if not guardias:
                        ui.label("No hay guardias para este filtro.").classes(
                            "text-grey"
                        )
                    for g in reversed(guardias):
                        _render_guardia(g)

            ui.button("Aplicar filtro", on_click=aplicar_filtro).props(
                "color=primary flat"
            )

        # Lista completa sin filtro
        ui.label("GUARDIAS REGISTRADAS").classes("text-caption text-grey q-mb-sm")
        guardias = novedades.cargar_datos()
        if not guardias:
            ui.label("No hay guardias registradas todavía.").classes("text-grey")
        else:
            for g in reversed(guardias):
                _render_guardia(g)
