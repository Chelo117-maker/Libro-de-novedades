# Gestión de grupos de trabajo: creación, edición permanente,
# ajuste por guardia e historial de cambios.

from nicegui import ui
from components.sidebar import crear_sidebar, crear_header
from components.ayuda import mostrar_dialogo_ayuda
import novedades

MOTIVOS: list[str] = [
    "Licencia médica",
    "Licencia vacacional",
    "Cambio de turno",
    "Franco / día libre",
    "Baja administrativa",
]


def configurar_tema() -> None:
    """Activa el modo oscuro y el color primario."""
    ui.dark_mode().enable()
    ui.colors(primary="#1976D2")


@ui.page("/grupos")
def pagina_grupos() -> None:
    """Pantalla de gestión de grupos con tres pestañas."""
    configurar_tema()
    drawer = crear_sidebar("grupos")
    crear_header(
        drawer, "Grupos de trabajo", mostrar_ayuda=True, fn_ayuda=mostrar_dialogo_ayuda
    )

    with ui.column().classes("q-pa-md full-width"):
        with ui.tabs().classes("full-width") as tabs:
            tab_grupos = ui.tab("Grupos base")
            tab_cambios = ui.tab("Ajuste por guardia")
            tab_historial = ui.tab("Historial de cambios")

        with ui.tab_panels(tabs, value=tab_grupos).classes("full-width"):

            # ── Grupos base ───────────────────────────────────────────────────
            with ui.tab_panel(tab_grupos):
                ui.label("CREAR GRUPO BASE").classes("text-caption text-grey q-mb-sm")
                with ui.card().classes("full-width q-mb-md"):
                    nombre_grupo = ui.input("Nombre del grupo (ej: Grupo A)").classes(
                        "full-width q-mb-sm"
                    )
                    ui.label("Seleccioná los miembros base:").classes(
                        "text-caption text-grey q-mb-xs"
                    )
                    ops = novedades.cargar_operarios()
                    checks: list[tuple] = []

                    if not ops:
                        ui.label(
                            "No hay operarios registrados. Registrá operarios primero."
                        ).classes("text-grey text-caption")
                    else:
                        for op in ops:
                            with ui.row().classes("items-center"):
                                check = ui.checkbox(
                                    f"[{op['legajo']}] {op['nombre']} {op['apellido']}"
                                )
                                checks.append((check, op["legajo"]))

                    # Botón justo después de los inputs
                    def crear_grupo() -> None:
                        """Crea un grupo base con los operarios seleccionados."""
                        if not nombre_grupo.value:
                            ui.notify("Escribí el nombre del grupo", color="warning")
                            return
                        legajos = [leg for check, leg in checks if check.value]
                        if not legajos:
                            ui.notify("Seleccioná al menos un miembro", color="warning")
                            return
                        ok = novedades.agregar_grupo(nombre_grupo.value, legajos)
                        if ok:
                            ui.notify(
                                f"Grupo '{nombre_grupo.value}' creado ✓",
                                color="positive",
                            )
                            nombre_grupo.value = ""
                            for check, _ in checks:
                                check.value = False
                            actualizar_grupos()
                        else:
                            ui.notify(
                                "Ya existe un grupo con ese nombre", color="negative"
                            )

                    ui.button("Crear grupo", on_click=crear_grupo).props(
                        "color=primary rounded"
                    ).classes("full-width q-mt-sm")

                ui.label("GRUPOS REGISTRADOS").classes("text-caption text-grey q-mb-sm")
                lista_grupos = ui.column().classes("full-width")

                def actualizar_grupos() -> None:
                    """Recarga la lista de grupos registrados."""
                    lista_grupos.clear()
                    datos = novedades.cargar_grupos()
                    ops_reg = novedades.cargar_operarios()

                    if not datos["grupos"]:
                        with lista_grupos:
                            ui.label("No hay grupos registrados todavía.").classes(
                                "text-grey"
                            )
                        return

                    with lista_grupos:
                        for g in datos["grupos"]:
                            with ui.card().classes("full-width q-mb-sm"):
                                with ui.row().classes(
                                    "items-center justify-between full-width"
                                ):
                                    ui.label(g["nombre"]).classes(
                                        "text-body1 text-primary"
                                    )
                                    with ui.row().classes("q-gutter-xs"):
                                        # Botón editar abre diálogo de edición permanente
                                        ui.button(
                                            icon="edit",
                                            on_click=lambda n=g[
                                                "nombre"
                                            ]: abrir_editor_grupo(n),
                                        ).props("flat round color=primary").tooltip(
                                            "Editar miembros"
                                        )
                                        ui.button(
                                            icon="delete",
                                            on_click=lambda n=g[
                                                "nombre"
                                            ]: eliminar_grupo(n),
                                        ).props("flat round color=negative").tooltip(
                                            "Eliminar grupo"
                                        )

                                ui.label("Miembros base:").classes(
                                    "text-caption text-grey q-mt-xs"
                                )
                                for legajo in g["miembros_base"]:
                                    op = next(
                                        (o for o in ops_reg if o["legajo"] == legajo),
                                        None,
                                    )
                                    nombre_op = (
                                        f"[{op['legajo']}] {op['nombre']} {op['apellido']}"
                                        if op
                                        else f"[{legajo}] — no encontrado"
                                    )
                                    with ui.row().classes("items-center q-gutter-sm"):
                                        ui.icon("person").classes(
                                            "text-positive text-caption"
                                        )
                                        ui.label(nombre_op).classes("text-body2")

                def abrir_editor_grupo(nombre: str) -> None:
                    """
                    Abre un diálogo para editar los miembros permanentes del grupo.
                    Los cambios modifican el grupo base, no una guardia específica.
                    """
                    datos = novedades.cargar_grupos()
                    ops_reg = novedades.cargar_operarios()
                    grupo = next(
                        (g for g in datos["grupos"] if g["nombre"] == nombre), None
                    )
                    if not grupo:
                        return

                    with ui.dialog() as dlg, ui.card().style("width:500px"):
                        ui.label(f"Editar grupo: {nombre}").classes("text-h6 q-mb-sm")
                        ui.label(
                            "Marcá los operarios que pertenecen al grupo base:"
                        ).classes("text-caption text-grey q-mb-sm")

                        checks_edit: list[tuple] = []
                        for op in ops_reg:
                            activo = op["legajo"] in grupo["miembros_base"]
                            with ui.row().classes("items-center"):
                                check = ui.checkbox(
                                    f"[{op['legajo']}] {op['nombre']} {op['apellido']}",
                                    value=activo,
                                )
                                checks_edit.append((check, op["legajo"]))

                        def guardar_edicion() -> None:
                            """Guarda los nuevos miembros del grupo base."""
                            nuevos_legajos = [leg for c, leg in checks_edit if c.value]
                            if not nuevos_legajos:
                                ui.notify(
                                    "El grupo debe tener al menos un miembro",
                                    color="warning",
                                )
                                return
                            datos_act = novedades.cargar_grupos()
                            for g in datos_act["grupos"]:
                                if g["nombre"] == nombre:
                                    g["miembros_base"] = nuevos_legajos
                                    break
                            novedades.guardar_grupos(datos_act)
                            ui.notify(
                                f"Grupo '{nombre}' actualizado ✓", color="positive"
                            )
                            dlg.close()
                            actualizar_grupos()

                        with ui.row().classes("q-gutter-sm full-width q-mt-md"):
                            ui.button("Cancelar", on_click=dlg.close).props(
                                "flat color=grey"
                            ).classes("col")
                            ui.button(
                                "Guardar cambios", on_click=guardar_edicion
                            ).props("color=primary rounded").classes("col")

                    dlg.open()

                def eliminar_grupo(nombre: str) -> None:
                    """Elimina un grupo y recarga la lista."""
                    novedades.eliminar_grupo(nombre)
                    ui.notify(f"Grupo '{nombre}' eliminado", color="warning")
                    actualizar_grupos()

                actualizar_grupos()

            # ── Ajuste por guardia ────────────────────────────────────────────
            with ui.tab_panel(tab_cambios):
                ui.label("AJUSTE PARA UNA GUARDIA ESPECÍFICA").classes(
                    "text-caption text-grey q-mb-sm"
                )
                ui.label(
                    "Registrá ausencias o incorporaciones para una guardia puntual "
                    "sin modificar la composición permanente del grupo."
                ).classes("text-body2 text-grey q-mb-md")

                with ui.card().classes("full-width q-mb-md"):
                    datos_grupos = novedades.cargar_grupos()
                    nombres_grupos = [g["nombre"] for g in datos_grupos["grupos"]]

                    if not nombres_grupos:
                        ui.label(
                            "No hay grupos registrados. Creá un grupo primero."
                        ).classes("text-grey")
                    else:
                        grupo_sel = ui.select(
                            nombres_grupos, label="Grupo afectado"
                        ).classes("full-width q-mb-sm")
                        fecha_c = ui.input("Fecha de la guardia (AAAA-MM-DD)").classes(
                            "full-width q-mb-sm"
                        )
                        franja_c = ui.select(
                            ["Mañana", "Tarde", "Noche"], label="Franja"
                        ).classes("full-width q-mb-sm")
                        tipo_c = ui.select(
                            ["ausencia", "incorporacion"], label="Tipo de cambio"
                        ).classes("full-width q-mb-sm")
                        motivo_c = ui.select(MOTIVOS, label="Motivo").classes(
                            "full-width q-mb-sm"
                        )

                        ops = novedades.cargar_operarios()
                        op_opts = {
                            op[
                                "legajo"
                            ]: f"[{op['legajo']}] {op['nombre']} {op['apellido']}"
                            for op in ops
                        }
                        legajo_c = ui.select(
                            op_opts, label="Operario afectado"
                        ).classes("full-width q-mb-sm")
                        reemplazo_c = ui.select(
                            {**op_opts, "": "Sin reemplazo"},
                            value="",
                            label="Reemplazado por (opcional)",
                        ).classes("full-width q-mb-sm")

                        def registrar_cambio() -> None:
                            """Registra un cambio puntual en la composición del grupo."""
                            if not all(
                                [
                                    grupo_sel.value,
                                    fecha_c.value,
                                    franja_c.value,
                                    tipo_c.value,
                                    motivo_c.value,
                                    legajo_c.value,
                                ]
                            ):
                                ui.notify(
                                    "Completá todos los campos obligatorios",
                                    color="warning",
                                )
                                return
                            novedades.registrar_cambio_grupo(
                                fecha=fecha_c.value,
                                franja=franja_c.value,
                                nombre_grupo=grupo_sel.value,
                                legajo=legajo_c.value,
                                tipo=tipo_c.value,
                                motivo=motivo_c.value,
                                reemplazado_por=reemplazo_c.value or None,
                            )
                            ui.notify("Cambio registrado ✓", color="positive")
                            fecha_c.value = ""

                        # Botón justo después de los inputs
                        ui.button("Registrar cambio", on_click=registrar_cambio).props(
                            "color=primary rounded"
                        ).classes("full-width")

            # ── Historial de cambios ──────────────────────────────────────────
            with ui.tab_panel(tab_historial):
                ui.label("HISTORIAL DE CAMBIOS").classes(
                    "text-caption text-grey q-mb-sm"
                )
                datos = novedades.cargar_grupos()
                cambios = datos.get("cambios", [])
                ops = novedades.cargar_operarios()

                if not cambios:
                    ui.label("No hay cambios registrados todavía.").classes("text-grey")
                else:
                    for c in reversed(cambios):
                        op = next((o for o in ops if o["legajo"] == c["legajo"]), None)
                        nombre_op = (
                            f"{op['nombre']} {op['apellido']}" if op else c["legajo"]
                        )
                        reemplazo = ""
                        if c.get("reemplazado_por"):
                            op_r = next(
                                (o for o in ops if o["legajo"] == c["reemplazado_por"]),
                                None,
                            )
                            reemplazo = (
                                f" → Reemplazado por {op_r['nombre']} {op_r['apellido']}"
                                if op_r
                                else f" → Reemplazado por [{c['reemplazado_por']}]"
                            )

                        tipo_color = (
                            "negative" if c["tipo"] == "ausencia" else "positive"
                        )
                        tipo_icono = (
                            "person_remove" if c["tipo"] == "ausencia" else "person_add"
                        )

                        with ui.card().classes("full-width q-mb-xs"):
                            with ui.row().classes(
                                "items-center justify-between full-width"
                            ):
                                with ui.row().classes("items-center q-gutter-sm"):
                                    ui.icon(tipo_icono).classes(f"text-{tipo_color}")
                                    with ui.column():
                                        ui.label(
                                            f"{c['fecha']} — {c['franja']} | {c['grupo']}"
                                        ).classes("text-caption text-grey")
                                        ui.label(f"{nombre_op}{reemplazo}").classes(
                                            "text-body2"
                                        )
                                        ui.label(c["motivo"]).classes(
                                            "text-caption text-grey"
                                        )
                                ui.badge(c["tipo"], color=tipo_color)
