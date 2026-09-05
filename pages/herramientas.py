# Gestión de herramientas y maquinaria con control de estado.

from nicegui import ui
from components.sidebar import crear_sidebar, crear_header, ESTADO_CONFIG
from components.ayuda import mostrar_dialogo_ayuda
import novedades


def configurar_tema() -> None:
    """Activa el modo oscuro y el color primario."""
    ui.dark_mode().enable()
    ui.colors(primary="#1976D2")


@ui.page("/herramientas")
def pagina_herramientas() -> None:
    """Pantalla de gestión de herramientas con fuzzy matching y control de estado."""
    configurar_tema()
    drawer = crear_sidebar("herramientas")
    crear_header(
        drawer,
        "Herramientas y maquinaria",
        mostrar_ayuda=True,
        fn_ayuda=mostrar_dialogo_ayuda,
    )

    with ui.column().classes("q-pa-md full-width"):

        ui.label("AGREGAR HERRAMIENTA").classes("text-caption text-grey")
        with ui.card().classes("full-width q-mb-md"):
            with ui.row().classes("full-width q-gutter-sm items-end"):
                nombre_h = ui.input("Nombre de la herramienta").classes("col")
                estado_h = ui.select(
                    ["Operativa", "Defectuosa", "Faltante"],
                    value="Operativa",
                    label="Estado",
                ).classes("col")

            def agregar_herramienta() -> None:
                """
                Agrega una herramienta al registro.
                Usa fuzzy matching para detectar duplicados o nombres similares.
                """
                if not nombre_h.value:
                    ui.notify("Escribí el nombre de la herramienta", color="warning")
                    return

                resultado = novedades.buscar_herramienta_similar(nombre_h.value)

                if resultado["exacta"]:
                    ui.notify(
                        f"'{resultado['exacta']['nombre']}' ya está registrada",
                        color="warning",
                    )
                    return

                if resultado["similares"]:
                    with ui.dialog() as dlg, ui.card().style("width:420px"):
                        with ui.row().classes("items-center q-gutter-sm q-mb-sm"):
                            ui.icon("help_outline").classes("text-warning text-h5")
                            ui.label("¿Herramienta similar encontrada?").classes(
                                "text-h6"
                            )
                        ui.label(
                            f"Escribiste '{nombre_h.value}'. ¿Te referías a alguna de estas?"
                        ).classes("text-body2 text-grey q-mb-sm")

                        for h in resultado["similares"]:
                            cfg = ESTADO_CONFIG.get(
                                h["estado"], ESTADO_CONFIG["Operativa"]
                            )
                            with ui.card().classes("full-width q-mb-xs"):
                                with ui.row().classes(
                                    "items-center justify-between full-width"
                                ):
                                    with ui.row().classes("items-center q-gutter-sm"):
                                        ui.icon(cfg["icon"]).classes(
                                            f"text-{cfg['color']}"
                                        )
                                        ui.label(h["nombre"]).classes("text-body2")
                                    ui.button(
                                        "Usar esta",
                                        on_click=lambda: (
                                            dlg.close(),
                                            ui.notify(
                                                "Usando herramienta existente",
                                                color="positive",
                                            ),
                                        ),
                                    ).props("flat color=primary")

                        ui.separator().classes("q-my-sm")
                        with ui.row().classes("q-gutter-sm full-width"):
                            ui.button("Cancelar", on_click=dlg.close).props(
                                "flat color=grey"
                            ).classes("col")
                            ui.button(
                                f"Agregar '{nombre_h.value}' igual",
                                on_click=lambda: (
                                    dlg.close(),
                                    novedades.agregar_herramienta(
                                        nombre_h.value, estado_h.value
                                    ),
                                    ui.notify(
                                        f"'{nombre_h.value}' agregada ✓",
                                        color="positive",
                                    ),
                                    actualizar_herramientas(),
                                ),
                            ).props("color=positive").classes("col")

                    dlg.open()
                    return

                novedades.agregar_herramienta(nombre_h.value, estado_h.value)
                ui.notify(f"'{nombre_h.value}' agregada ✓", color="positive")
                nombre_h.value = ""
                actualizar_herramientas()

            # Botón justo después de los inputs
            ui.button("Agregar", on_click=agregar_herramienta).props(
                "color=primary rounded"
            ).classes("full-width q-mt-sm")

        ui.label("ESTADO DE HERRAMIENTAS").classes("text-caption text-grey q-mb-sm")
        lista_h = ui.column().classes("q-mt-sm full-width")

        def actualizar_herramientas() -> None:
            """Recarga la lista de herramientas con su estado actual."""
            lista_h.clear()
            herramientas = novedades.cargar_herramientas()
            if not herramientas:
                with lista_h:
                    ui.label("No hay herramientas registradas.").classes("text-grey")
                return
            with lista_h:
                for h in herramientas:
                    cfg = ESTADO_CONFIG.get(h["estado"], ESTADO_CONFIG["Operativa"])
                    with ui.card().classes("full-width q-mb-xs"):
                        with ui.row().classes(
                            "items-center justify-between full-width"
                        ):
                            with ui.row().classes("items-center q-gutter-sm"):
                                ui.icon(cfg["icon"]).classes(f"text-{cfg['color']}")
                                ui.label(h["nombre"]).classes("text-body2")
                                ui.badge(h["estado"], color=cfg["color"])
                            with ui.row().classes("q-gutter-xs"):
                                ui.button(
                                    icon="check_circle",
                                    on_click=lambda n=h["nombre"]: cambiar_estado(
                                        n, "Operativa"
                                    ),
                                ).props("flat round color=positive").tooltip(
                                    "Marcar operativa"
                                )
                                ui.button(
                                    icon="warning",
                                    on_click=lambda n=h["nombre"]: cambiar_estado(
                                        n, "Defectuosa"
                                    ),
                                ).props("flat round color=warning").tooltip(
                                    "Marcar defectuosa"
                                )
                                ui.button(
                                    icon="cancel",
                                    on_click=lambda n=h["nombre"]: cambiar_estado(
                                        n, "Faltante"
                                    ),
                                ).props("flat round color=negative").tooltip(
                                    "Marcar faltante"
                                )
                                ui.button(
                                    icon="delete",
                                    on_click=lambda n=h["nombre"]: eliminar_herramienta(
                                        n
                                    ),
                                ).props("flat round color=grey").tooltip("Eliminar")

        def cambiar_estado(nombre: str, nuevo_estado: str) -> None:
            """Actualiza el estado de una herramienta y recarga la lista."""
            novedades.actualizar_estado_herramienta(nombre, nuevo_estado)
            ui.notify(f'Estado actualizado a "{nuevo_estado}"', color="positive")
            actualizar_herramientas()

        def eliminar_herramienta(nombre: str) -> None:
            """Elimina una herramienta del registro y recarga la lista."""
            novedades.eliminar_herramienta(nombre)
            ui.notify(f'"{nombre}" eliminada', color="warning")
            actualizar_herramientas()

        actualizar_herramientas()
