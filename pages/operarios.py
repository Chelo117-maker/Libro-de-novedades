# Gestión de operarios: registro, activos en guardia e historial.

from nicegui import ui
from operario import Operario
from components.sidebar import crear_sidebar, crear_header, FRANJA_COLOR
from components.ayuda import mostrar_dialogo_ayuda
import novedades


def configurar_tema() -> None:
    """Activa el modo oscuro y el color primario."""
    ui.dark_mode().enable()
    ui.colors(primary="#1976D2")


@ui.page("/operarios")
def pagina_operarios() -> None:
    """Pantalla de gestión de operarios con tres pestañas."""
    configurar_tema()
    drawer = crear_sidebar("operarios")
    crear_header(
        drawer, "Operarios", mostrar_ayuda=True, fn_ayuda=mostrar_dialogo_ayuda
    )

    with ui.column().classes("q-pa-md full-width"):
        with ui.tabs().classes("full-width") as tabs:
            tab_registro = ui.tab("Registro")
            tab_activos = ui.tab("Activos en guardia")
            tab_historial = ui.tab("Historial")

        with ui.tab_panels(tabs, value=tab_registro).classes("full-width"):

            # ── Registro ──────────────────────────────────────────────────────
            with ui.tab_panel(tab_registro):
                ui.label("REGISTRAR OPERARIO").classes("text-caption text-grey q-mb-sm")
                with ui.card().classes("full-width q-mb-md"):
                    with ui.row().classes("full-width q-gutter-sm"):
                        legajo = ui.input("Legajo").classes("col")
                        nombre = ui.input("Nombre").classes("col")
                        apellido = ui.input("Apellido").classes("col")

                    def registrar_operario() -> None:
                        """Valida y registra un operario nuevo en el sistema."""
                        if not nombre.value or not legajo.value:
                            ui.notify(
                                "Legajo y nombre son obligatorios", color="warning"
                            )
                            return

                        ops_actuales = novedades.cargar_operarios()
                        if any(op["legajo"] == legajo.value for op in ops_actuales):
                            ui.notify(
                                f"Ya existe un operario con el legajo {legajo.value}",
                                color="negative",
                            )
                            return

                        nombre_completo = f"{nombre.value} {apellido.value}".strip()
                        resultado = novedades.buscar_operario_similar(nombre_completo)

                        if resultado["exacto"]:
                            ui.notify(
                                f"Ya existe '{resultado['exacto']['nombre']} "
                                f"{resultado['exacto']['apellido']}' con legajo "
                                f"{resultado['exacto']['legajo']}",
                                color="warning",
                            )
                            return

                        if resultado["similares"]:
                            with ui.dialog() as dlg, ui.card().style("width:440px"):
                                with ui.row().classes(
                                    "items-center q-gutter-sm q-mb-sm"
                                ):
                                    ui.icon("person_search").classes(
                                        "text-warning text-h5"
                                    )
                                    ui.label("¿Operario similar encontrado?").classes(
                                        "text-h6"
                                    )
                                ui.label(
                                    f"Estás por registrar '{nombre_completo}'. "
                                    "¿Es la misma persona que alguna de estas?"
                                ).classes("text-body2 text-grey q-mb-sm")

                                for op in resultado["similares"]:
                                    with ui.card().classes("full-width q-mb-xs"):
                                        with ui.row().classes(
                                            "items-center justify-between full-width"
                                        ):
                                            with ui.row().classes(
                                                "items-center q-gutter-sm"
                                            ):
                                                ui.icon("person").classes(
                                                    "text-primary"
                                                )
                                                ui.label(
                                                    f"[{op['legajo']}] {op['nombre']} {op['apellido']}"
                                                ).classes("text-body2")
                                            ui.button(
                                                "Es este",
                                                on_click=lambda: (
                                                    dlg.close(),
                                                    ui.notify(
                                                        "Registro cancelado, ya existe",
                                                        color="info",
                                                    ),
                                                ),
                                            ).props("flat color=warning")

                                ui.separator().classes("q-my-sm")
                                with ui.row().classes("q-gutter-sm full-width q-mt-sm"):
                                    ui.button("Cancelar", on_click=dlg.close).props(
                                        "flat color=grey"
                                    ).classes("col")

                                    def registrar_igual() -> None:
                                        op = Operario(
                                            legajo.value, nombre.value, apellido.value
                                        )
                                        ok = novedades.agregar_operario_fijo(op)
                                        dlg.close()
                                        if ok:
                                            ui.notify(
                                                f"{op.nombre_completo()} registrado ✓",
                                                color="positive",
                                            )
                                            legajo.value = nombre.value = (
                                                apellido.value
                                            ) = ""
                                            actualizar_lista()
                                        else:
                                            ui.notify(
                                                "Error al registrar", color="negative"
                                            )

                                    ui.button(
                                        "Registrar igual", on_click=registrar_igual
                                    ).props("color=positive").classes("col")

                            dlg.open()
                            return

                        op = Operario(legajo.value, nombre.value, apellido.value)
                        ok = novedades.agregar_operario_fijo(op)
                        if ok:
                            ui.notify(
                                f"{op.nombre_completo()} registrado ✓", color="positive"
                            )
                            legajo.value = nombre.value = apellido.value = ""
                            actualizar_lista()
                        else:
                            ui.notify(
                                "Ya existe un operario con ese legajo", color="negative"
                            )

                    # Botón justo después de los inputs
                    ui.button("Registrar operario", on_click=registrar_operario).props(
                        "color=primary rounded"
                    ).classes("full-width q-mt-sm")

                lista_reg = ui.column().classes("q-mt-sm full-width")

                def actualizar_lista() -> None:
                    """Recarga la lista de operarios registrados."""
                    lista_reg.clear()
                    ops = novedades.cargar_operarios()
                    if not ops:
                        with lista_reg:
                            ui.label("No hay operarios registrados todavía.").classes(
                                "text-grey"
                            )
                        return
                    with lista_reg:
                        for op in ops:
                            with ui.card().classes("full-width q-mb-xs"):
                                with ui.row().classes(
                                    "items-center justify-between full-width"
                                ):
                                    with ui.row().classes("items-center q-gutter-sm"):
                                        ui.icon("person").classes("text-primary")
                                        ui.label(
                                            f"[{op['legajo']}] {op['nombre']} {op['apellido']}"
                                        ).classes("text-body2")
                                    ui.button(
                                        icon="delete",
                                        on_click=lambda l=op[
                                            "legajo"
                                        ]: eliminar_y_actualizar(l),
                                    ).props("flat round color=negative")

                def eliminar_y_actualizar(legajo_op: str) -> None:
                    """Elimina un operario del registro y recarga la lista."""
                    novedades.eliminar_operario_fijo(legajo_op)
                    ui.notify("Operario eliminado", color="warning")
                    actualizar_lista()

                actualizar_lista()

            # ── Activos en guardia ────────────────────────────────────────────
            with ui.tab_panel(tab_activos):
                ui.label("OPERARIOS EN GUARDIA ACTUAL").classes(
                    "text-caption text-grey q-mb-sm"
                )
                guardias = novedades.cargar_datos()
                if not guardias:
                    ui.label("No hay guardias registradas.").classes("text-grey")
                else:
                    ultima = guardias[-1]
                    ui.label(
                        f"Última guardia: {ultima['fecha']} — {ultima['franja']}"
                    ).classes("text-caption text-grey q-mb-sm")
                    if not ultima["grupo"]:
                        ui.label("Sin operarios registrados en esta guardia.").classes(
                            "text-grey"
                        )
                    for op in ultima["grupo"]:
                        with ui.card().classes("full-width q-mb-xs"):
                            with ui.row().classes("items-center q-gutter-sm"):
                                ui.icon("person").classes("text-positive")
                                ui.label(
                                    f"[{op['legajo']}] {op['nombre']} {op['apellido']}"
                                ).classes("text-body2")

            # ── Historial por operario ────────────────────────────────────────
            with ui.tab_panel(tab_historial):
                ui.label("GUARDIAS POR OPERARIO").classes(
                    "text-caption text-grey q-mb-sm"
                )
                guardias = novedades.cargar_datos()
                if not guardias:
                    ui.label("No hay guardias registradas.").classes("text-grey")
                else:
                    conteo: dict[str, dict] = {}
                    for g in guardias:
                        for op in g["grupo"]:
                            key = f"{op['nombre']} {op['apellido']}"
                            if key not in conteo:
                                conteo[key] = {"total": 0, "franjas": []}
                            conteo[key]["total"] += 1
                            conteo[key]["franjas"].append(g["franja"])

                    for nombre_op, datos in sorted(
                        conteo.items(), key=lambda x: x[1]["total"], reverse=True
                    ):
                        franja_frecuente = max(
                            set(datos["franjas"]), key=datos["franjas"].count
                        )
                        with ui.card().classes("full-width q-mb-xs"):
                            with ui.row().classes(
                                "items-center justify-between full-width"
                            ):
                                with ui.row().classes("items-center q-gutter-sm"):
                                    ui.icon("person").classes("text-primary")
                                    ui.label(nombre_op).classes("text-body2")
                                with ui.row().classes("items-center q-gutter-xs"):
                                    ui.badge(
                                        f"{datos['total']} guardias", color="primary"
                                    )
                                    ui.badge(
                                        franja_frecuente,
                                        color=FRANJA_COLOR.get(
                                            franja_frecuente.lower(), "grey"
                                        ),
                                    )
