# Panel principal con estadísticas, alertas y novedades agrupadas por franja.

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
    """Panel de inicio con estadísticas, alertas y novedades agrupadas por franja."""
    configurar_tema()
    guardias = novedades.cargar_datos()
    total_novedades = sum(len(g["novedades"]) for g in guardias)
    total_operarios = len(novedades.cargar_operarios())
    herramientas = novedades.cargar_herramientas()
    con_alerta = [h for h in herramientas if h["estado"] != "Operativa"]

    drawer = crear_sidebar("inicio")
    crear_header(
        drawer,
        "Panel principal",
        mostrar_badge=True,
        mostrar_ayuda=True,
        fn_ayuda=mostrar_dialogo_ayuda,
    )

    with ui.column().classes("q-pa-md full-width"):

        # ── Estadísticas ──────────────────────────────────────────────────────
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
            with ui.card().classes("col"):
                ui.label("Alertas activas").classes("text-caption text-grey")
                ui.label(str(len(con_alerta))).classes(
                    "text-h4 text-negative" if con_alerta else "text-h4 text-positive"
                )

        # ── Contenido principal en dos columnas ───────────────────────────────
        with ui.row().classes("full-width q-gutter-md"):

            # Columna izquierda — novedades agrupadas por franja
            with ui.column().classes("col-8"):
                ui.label("NOVEDADES DEL DÍA").classes("text-caption text-grey q-mb-sm")

                # Agrupar guardias de hoy por franja
                from datetime import datetime

                hoy = datetime.now().strftime("%Y-%m-%d")
                guardias_hoy = [g for g in guardias if g["fecha"] == hoy]

                if not guardias_hoy:
                    with ui.card().classes("full-width"):
                        ui.label("No hay novedades registradas hoy.").classes(
                            "text-grey"
                        )
                else:
                    # Ordenar franjas por horario
                    orden_franjas = ["Mañana", "Tarde", "Noche"]
                    franjas_hoy = {g["franja"] for g in guardias_hoy}
                    franjas_ord = [f for f in orden_franjas if f in franjas_hoy]

                    for franja in franjas_ord:
                        gs_franja = [g for g in guardias_hoy if g["franja"] == franja]
                        color = FRANJA_COLOR.get(franja.lower(), "grey")

                        with ui.card().classes("full-width q-mb-md").style(
                            f"border-left: 4px solid var(--q-{color})"
                        ):
                            with ui.row().classes("items-center q-gutter-sm q-mb-sm"):
                                ui.badge(franja, color=color)
                                ui.label(f"{len(gs_franja)} guardia(s)").classes(
                                    "text-caption text-grey"
                                )

                            for g in gs_franja:
                                hora = g.get("hora", "")
                                ops = ", ".join(
                                    f"{o['nombre']} {o['apellido']}" for o in g["grupo"]
                                )
                                with ui.card().classes("full-width q-mb-xs").style(
                                    "background: rgba(255,255,255,0.03)"
                                ):
                                    with ui.row().classes(
                                        "items-center justify-between full-width"
                                    ):
                                        with ui.column().classes("col"):
                                            ui.label(f"{hora}  —  {ops}").classes(
                                                "text-caption text-grey"
                                            )
                                            if g["novedades"]:
                                                for nov in g["novedades"]:
                                                    with ui.row().classes(
                                                        "items-start q-gutter-xs"
                                                    ):
                                                        ui.icon(
                                                            "fiber_manual_record"
                                                        ).classes(
                                                            "text-caption text-grey"
                                                        ).style(
                                                            "font-size:8px; margin-top:6px"
                                                        )
                                                        ui.label(nov).classes(
                                                            "text-body2"
                                                        )
                                            else:
                                                ui.label(
                                                    "Sin novedades registradas."
                                                ).classes("text-grey text-caption")

                # Últimas guardias de otros días
                ui.label("ÚLTIMAS GUARDIAS").classes(
                    "text-caption text-grey q-mt-md q-mb-sm"
                )
                otras = [g for g in reversed(guardias[-10:]) if g["fecha"] != hoy]
                if not otras:
                    ui.label("No hay guardias anteriores.").classes(
                        "text-grey text-caption"
                    )
                else:
                    for g in otras[:5]:
                        with ui.card().classes("full-width q-mb-xs"):
                            with ui.row().classes(
                                "items-center justify-between full-width"
                            ):
                                with ui.column().classes("col"):
                                    ui.label(
                                        f"{g['fecha']}  {g.get('hora', '')}"
                                    ).classes("text-caption text-grey")
                                    ui.label(
                                        g["novedades"][0]
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

            # Columna derecha — alertas de herramientas
            with ui.column().classes("col"):
                ui.label("ALERTAS DE HERRAMIENTAS").classes(
                    "text-caption text-grey q-mb-sm"
                )
                if not con_alerta:
                    with ui.card().classes("full-width"):
                        with ui.row().classes("items-center q-gutter-sm"):
                            ui.icon("check_circle").classes("text-positive")
                            ui.label("Todas las herramientas operativas").classes(
                                "text-body2 text-positive"
                            )
                else:
                    for h in con_alerta:
                        cfg = ESTADO_CONFIG[h["estado"]]
                        with ui.card().classes("full-width q-mb-xs"):
                            with ui.row().classes("items-center q-gutter-sm"):
                                ui.icon(cfg["icon"]).classes(f"text-{cfg['color']}")
                                with ui.column():
                                    ui.label(h["nombre"]).classes("text-body2")
                                    ui.badge(h["estado"], color=cfg["color"])
