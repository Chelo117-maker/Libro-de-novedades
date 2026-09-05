# Panel principal con estadísticas, alertas de herramientas y últimas novedades.

from nicegui import ui
from components.sidebar import crear_sidebar, crear_header, ESTADO_CONFIG, FRANJA_COLOR
from components.ayuda import mostrar_dialogo_ayuda
import novedades


def configurar_tema() -> None:
    """Activa el modo oscuro y el color primario."""
    ui.dark_mode().enable()
    ui.colors(primary="#1976D2")


@ui.page("/")
def pagina_principal() -> None:
    """Panel de inicio con estadísticas, alertas y últimas novedades."""
    configurar_tema()
    guardias = novedades.cargar_datos()
    total_novedades = sum(len(g["novedades"]) for g in guardias)
    total_operarios = len(novedades.cargar_operarios())

    drawer = crear_sidebar("inicio")
    crear_header(
        drawer,
        "Panel principal",
        mostrar_badge=True,
        mostrar_ayuda=True,
        fn_ayuda=mostrar_dialogo_ayuda,
    )

    with ui.column().classes("q-pa-md full-width"):

        # Tarjetas de estadísticas
        with ui.row().classes("full-width q-gutter-md q-mb-md"):
            with ui.card().classes("col"):
                ui.label("Guardias registradas").classes("text-caption text-grey")
                ui.label(str(len(guardias))).classes("text-h4 text-primary")
            with ui.card().classes("col"):
                ui.label("Novedades totales").classes("text-caption text-grey")
                ui.label(str(total_novedades)).classes("text-h4 text-warning")
            with ui.card().classes("col"):
                ui.label("Operarios registrados").classes("text-caption text-grey")
                ui.label(str(total_operarios)).classes("text-h4 text-positive")

        # Alertas de herramientas con problemas
        herramientas = novedades.cargar_herramientas()
        con_alerta = [h for h in herramientas if h["estado"] != "Operativa"]
        if con_alerta:
            ui.label("⚠️ ALERTAS DE HERRAMIENTAS").classes(
                "text-caption text-warning q-mb-sm"
            )
            for h in con_alerta:
                cfg = ESTADO_CONFIG[h["estado"]]
                with ui.card().classes("full-width q-mb-xs"):
                    with ui.row().classes("items-center q-gutter-sm"):
                        ui.icon(cfg["icon"]).classes(f"text-{cfg['color']}")
                        ui.label(h["nombre"]).classes("text-body2")
                        ui.badge(h["estado"], color=cfg["color"])

        # Últimas 5 novedades registradas
        ui.label("ÚLTIMAS NOVEDADES").classes("text-caption text-grey q-mb-sm q-mt-md")
        if not guardias:
            ui.label("No hay novedades registradas todavía.").classes("text-grey")
        else:
            for g in reversed(guardias[-5:]):
                with ui.card().classes("full-width q-mb-sm"):
                    with ui.row().classes("items-center justify-between full-width"):
                        with ui.column().classes("col"):
                            ui.label(g["fecha"]).classes("text-caption text-grey")
                            ui.label(
                                g["novedades"][0] if g["novedades"] else "Sin novedades"
                            ).classes("text-body2")
                            ui.label(
                                ", ".join(
                                    f"{o['nombre']} {o['apellido']}" for o in g["grupo"]
                                )
                            ).classes("text-caption text-grey")
                        ui.badge(
                            g["franja"],
                            color=FRANJA_COLOR.get(g["franja"].lower(), "grey"),
                        )
