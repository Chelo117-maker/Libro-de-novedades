# Formulario para registrar una nueva guardia con grupo, operarios y novedades.

from nicegui import ui
from datetime import datetime
from operario import Operario
from guardia import Guardia
from components.sidebar import crear_sidebar, crear_header, ESTADO_CONFIG
from components.ayuda import mostrar_dialogo_ayuda
import novedades


def configurar_tema() -> None:
    """Activa el modo oscuro y el color primario."""
    ui.dark_mode().enable()
    ui.colors(primary="#1976D2")


@ui.page("/nueva-guardia")
def pagina_nueva_guardia() -> None:
    """Pantalla para registrar una nueva guardia."""
    configurar_tema()
    operarios_guardia: list[Operario] = []
    novedades_lst: list[str] = []

    drawer = crear_sidebar("nueva")
    crear_header(
        drawer, "Nueva guardia", mostrar_ayuda=True, fn_ayuda=mostrar_dialogo_ayuda
    )

    with ui.column().classes("q-pa-md full-width"):

        # Datos de la guardia
        ui.label("DATOS DE LA GUARDIA").classes("text-caption text-grey")
        with ui.card().classes("full-width q-mb-md"):

            # Selección de grupo y operarios
            ui.label("GRUPO DE TRABAJO").classes("text-caption text-grey")
        with ui.card().classes("full-width q-mb-md"):
            lista_op = ui.column().classes("q-mt-sm")

        # Recarga los grupos cada vez que se abre la página
        def obtener_grupos() -> list[str]:
            datos = novedades.cargar_grupos()
            return [g["nombre"] for g in datos["grupos"]]

        nombres_grupos = obtener_grupos()

        if nombres_grupos:
            grupo_sel = ui.select(
                nombres_grupos,
                label="Seleccionar grupo base",
            ).classes("full-width q-mb-sm")

            def cargar_grupo() -> None:
                """Carga los operarios del grupo seleccionado en la guardia."""
                if not grupo_sel.value:
                    ui.notify("Seleccioná un grupo", color="warning")
                    return
                datos = novedades.cargar_grupos()
                ops = novedades.cargar_operarios()
                grupo = next(
                    (g for g in datos["grupos"] if g["nombre"] == grupo_sel.value),
                    None,
                )
                if not grupo:
                    ui.notify("Grupo no encontrado", color="negative")
                    return

                operarios_guardia.clear()
                lista_op.clear()

                for legajo in grupo["miembros_base"]:
                    op_data = next((o for o in ops if o["legajo"] == legajo), None)
                    if op_data:
                        op = Operario(
                            op_data["legajo"],
                            op_data["nombre"],
                            op_data["apellido"],
                        )
                    operarios_guardia.append(op)
                    with lista_op:
                        with ui.row().classes("items-center"):
                            ui.icon("check_circle").classes("text-positive")
                            ui.label(str(op)).classes("text-body2")

                if operarios_guardia:
                    ui.notify(
                        f"Grupo '{grupo_sel.value}' cargado con "
                        f"{len(operarios_guardia)} operarios ✓",
                        color="positive",
                    )
                else:
                    ui.notify(
                        "El grupo no tiene operarios registrados",
                        color="warning",
                    )

            ui.button("Cargar grupo", on_click=cargar_grupo).props("flat color=primary")
            ui.separator().classes("q-my-sm")
        else:
            ui.label(
                "No hay grupos registrados. Podés agregar operarios manualmente."
            ).classes("text-caption text-grey q-mb-sm")

        # Agregar operario desde registro
        ops_fijos = novedades.cargar_operarios()
        if ops_fijos:
            ui.label("Agregar operario desde registro:").classes(
                "text-caption text-grey q-mb-xs"
            )
            op_select = ui.select(
                {
                    op["legajo"]: f"[{op['legajo']}] {op['nombre']} {op['apellido']}"
                    for op in ops_fijos
                },
                label="Seleccionar operario",
            ).classes("full-width")

            def cargar_operario_fijo() -> None:
                """Agrega un operario del registro a la guardia evitando duplicados."""
                op_data = next(
                    (o for o in ops_fijos if o["legajo"] == op_select.value), None
                )
                if op_data:
                    if op_data["legajo"] in [o.legajo for o in operarios_guardia]:
                        ui.notify(
                            "Este operario ya está en la guardia", color="warning"
                        )
                        return
                    op = Operario(
                        op_data["legajo"], op_data["nombre"], op_data["apellido"]
                    )
                    operarios_guardia.append(op)
                    with lista_op:
                        with ui.row().classes("items-center"):
                            ui.icon("check_circle").classes("text-positive")
                            ui.label(str(op)).classes("text-body2")
                    ui.notify(f"{op.nombre_completo()} agregado ✓", color="positive")

            ui.button("+ Agregar operario", on_click=cargar_operario_fijo).props(
                "flat color=primary"
            )
            ui.separator().classes("q-my-sm")

        # Carga manual
        ui.label("O ingresá uno que no está en el registro:").classes(
            "text-caption text-grey q-mb-xs"
        )
        with ui.row().classes("full-width q-gutter-sm"):
            legajo = ui.input("Legajo").classes("col")
            nombre = ui.input("Nombre").classes("col")
            apellido = ui.input("Apellido").classes("col")

        def agregar_manual() -> None:
            """Agrega un operario ingresado manualmente a la guardia."""
            if not nombre.value:
                ui.notify("Completá al menos el nombre", color="warning")
                return
            op = Operario(legajo.value, nombre.value, apellido.value)
            operarios_guardia.append(op)
            with lista_op:
                with ui.row().classes("items-center"):
                    ui.icon("check_circle").classes("text-positive")
                    ui.label(str(op)).classes("text-body2")
            legajo.value = nombre.value = apellido.value = ""

        ui.button("+ Agregar a la guardia", on_click=agregar_manual).props(
            "flat color=primary"
        )

        # Novedades
        ui.label("NOVEDADES").classes("text-caption text-grey")
        with ui.card().classes("full-width q-mb-md"):
            texto_novedad = ui.textarea("Escribí la novedad").classes("full-width")
            lista_nov = ui.column().classes("q-mt-sm")

            def agregar_novedad() -> None:
                """Agrega una novedad a la lista del turno."""
                if not texto_novedad.value:
                    ui.notify("Escribí una novedad antes de agregar", color="warning")
                    return
                novedades_lst.append(texto_novedad.value)
                with lista_nov:
                    with ui.row().classes("items-center"):
                        ui.icon("fiber_manual_record").classes(
                            "text-primary text-caption"
                        )
                        ui.label(texto_novedad.value).classes("text-body2")
                texto_novedad.value = ""

            ui.button("+ Agregar novedad", on_click=agregar_novedad).props(
                "flat color=primary"
            )

        def guardar_guardia() -> None:
            """
            Guarda la guardia en el JSON.
            Si hay herramientas con alerta muestra un diálogo de confirmación.
            """
            if not fecha or not franja:
                ui.notify("Completá la fecha y la franja horaria", color="negative")
                return
            if not operarios_guardia:
                ui.notify("Agregá al menos un operario", color="negative")
                return

            herramientas = novedades.cargar_herramientas()
            con_alerta = [h for h in herramientas if h["estado"] != "Operativa"]

            def confirmar_y_guardar() -> None:
                g = Guardia(fecha, franja, hora_actual)
                for op in operarios_guardia:
                    g.agregar_operario(op)
                for nov in novedades_lst:
                    g.agregar_novedad(nov)
                novedades.agregar_guardia(g)
                ui.notify("Guardia guardada correctamente ✓", color="positive")
                ui.navigate.to("/")

            if con_alerta:
                with ui.dialog() as dlg, ui.card().style("width:480px"):
                    with ui.row().classes("items-center q-gutter-sm q-mb-sm"):
                        ui.icon("warning").classes("text-warning text-h5")
                        ui.label("Herramientas con alerta").classes("text-h6")
                    ui.label("Las siguientes herramientas tienen problemas:").classes(
                        "text-body2 text-grey q-mb-sm"
                    )
                    for h in con_alerta:
                        cfg = ESTADO_CONFIG[h["estado"]]
                        with ui.card().classes("full-width q-mb-xs"):
                            with ui.row().classes("items-center q-gutter-sm"):
                                ui.icon(cfg["icon"]).classes(f"text-{cfg['color']}")
                                ui.label(h["nombre"]).classes("text-body2")
                                ui.badge(h["estado"], color=cfg["color"])
                    ui.label(
                        "¿Querés continuar o revisar las herramientas primero?"
                    ).classes("text-body2 q-mt-sm")
                    with ui.row().classes("q-mt-md q-gutter-sm full-width"):
                        ui.button(
                            "Revisar herramientas",
                            on_click=lambda: (
                                dlg.close(),
                                ui.navigate.to("/herramientas"),
                            ),
                        ).props("flat color=warning").classes("col")
                        ui.button(
                            "Continuar igual",
                            on_click=lambda: (dlg.close(), confirmar_y_guardar()),
                        ).props("color=positive").classes("col")
                dlg.open()
            else:
                confirmar_y_guardar()

        ui.button("Guardar guardia", on_click=guardar_guardia).props(
            "color=primary rounded"
        ).classes("full-width")

        def obtener_franja_automatica() -> str:
            """
            Determina la franja horaria según la hora actual.
            Mañana: 06:00 a 13:59
            Tarde:  14:00 a 21:59
            Noche:  22:00 a 05:59
            """
            hora = datetime.now().hour
            if 6 <= hora < 14:
                return "Mañana"
            elif 14 <= hora < 22:
                return "Tarde"
            else:
                return "Noche"

        # Fecha y hora actuales — no editables por el usuario
        ahora = datetime.now()
        fecha_actual = ahora.strftime("%Y-%m-%d")
        hora_actual = ahora.strftime("%H:%M")
        franja_auto = obtener_franja_automatica()

        ui.label("DATOS DE LA GUARDIA").classes("text-caption text-grey")
        with ui.card().classes("full-width q-mb-md"):
            with ui.row().classes("items-center q-gutter-md q-mb-sm"):
                with ui.column():
                    ui.label("Fecha").classes("text-caption text-grey")
                    ui.label(fecha_actual).classes("text-body1 text-primary")
                with ui.column():
                    ui.label("Hora de inicio").classes("text-caption text-grey")
                    ui.label(hora_actual).classes("text-body1 text-primary")
                with ui.column():
                    ui.label("Franja detectada").classes("text-caption text-grey")
                    franja_color = {
                        "Mañana": "primary",
                        "Tarde": "warning",
                        "Noche": "purple",
                    }
                    ui.badge(franja_auto, color=franja_color.get(franja_auto, "grey"))

            ui.label(
                "La fecha, hora y franja se registran automáticamente al abrir este formulario."
            ).classes("text-caption text-grey")

        # Variables que usa guardar_guardia
        fecha = fecha_actual
        franja = franja_auto
