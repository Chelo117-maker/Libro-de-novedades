# Búsqueda de guardias por fecha, operario o palabra clave.

from nicegui import ui
from components.sidebar import crear_sidebar, crear_header, FRANJA_COLOR
from components.ayuda import mostrar_dialogo_ayuda
import novedades


def configurar_tema() -> None:
    """Activa el modo oscuro y el color primario."""
    ui.dark_mode().enable()
    ui.colors(primary="#1976D2")


@ui.page("/buscar")
def pagina_buscar() -> None:
    """Pantalla de búsqueda de guardias por distintos criterios."""
    configurar_tema()
    drawer = crear_sidebar("buscar")
    crear_header(
        drawer, "Buscar novedades", mostrar_ayuda=True, fn_ayuda=mostrar_dialogo_ayuda
    )

    with ui.column().classes("q-pa-md full-width"):
        ui.label("CRITERIO DE BÚSQUEDA").classes("text-caption text-grey")
        with ui.card().classes("full-width q-mb-md"):
            criterio = ui.select(
                ["Por fecha", "Por operario", "Por palabra clave"],
                label="Buscar por",
                value="Por fecha",
            ).classes("full-width")
            valor = ui.input("Valor a buscar").classes("full-width")
            ui.label(
                "Por fecha: AAAA-MM-DD  |  "
                "Por operario: nombre, apellido o legajo  |  "
                "Por palabra clave: cualquier palabra de una novedad"
            ).classes("text-caption text-grey q-mt-xs")

        results = ui.column().classes("full-width")

        def buscar() -> None:
            """Ejecuta la búsqueda según el criterio seleccionado."""
            results.clear()
            if criterio.value == "Por fecha":
                guardias = novedades.buscar_por_fecha(valor.value)
            elif criterio.value == "Por operario":
                guardias = novedades.buscar_por_operario(valor.value)
            else:
                guardias = novedades.buscar_por_palabra(valor.value)

            with results:
                if not guardias:
                    ui.label("No se encontraron resultados.").classes("text-grey")
                    return
                ui.label(f"{len(guardias)} resultado(s) encontrado(s)").classes(
                    "text-caption text-grey q-mb-sm"
                )
                for g in guardias:
                    with ui.card().classes("full-width q-mb-sm"):
                        with ui.row().classes(
                            "items-center justify-between full-width"
                        ):
                            with ui.column().classes("col"):
                                ui.label(g["fecha"]).classes("text-caption text-grey")
                                ui.label(
                                    " / ".join(g["novedades"])
                                    if g["novedades"]
                                    else "Sin novedades"
                                ).classes("text-body2")
                                ui.label(
                                    ", ".join(
                                        f"{o['nombre']} {o['apellido']}"
                                        for o in g["grupo"]
                                    )
                                ).classes("text-caption text-grey")
                            ui.badge(
                                g["franja"],
                                color=FRANJA_COLOR.get(g["franja"].lower(), "grey"),
                            )

        ui.button("Buscar", on_click=buscar).props("color=primary rounded").classes(
            "full-width"
        )
