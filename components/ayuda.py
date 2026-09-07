# Diálogo de ayuda con guía de uso del sistema.

from nicegui import ui


def mostrar_dialogo_ayuda() -> None:
    """Ventana emergente con guía paso a paso del sistema."""
    with ui.dialog() as dialogo, ui.card().style("width:600px; max-width:90vw"):
        ui.label("📖 Guía de uso").classes("text-h6 q-mb-md")

        with ui.tabs().classes("full-width") as tabs:
            tab1 = ui.tab("Guardias")
            tab2 = ui.tab("Grupos")
            tab3 = ui.tab("Operarios")
            tab4 = ui.tab("Herramientas")
            tab5 = ui.tab("Importar")
            tab6 = ui.tab("Formato")

        with ui.tab_panels(tabs, value=tab1).classes("full-width"):

            with ui.tab_panel(tab1):
                ui.label("¿Cómo registrar una guardia?").classes(
                    "text-subtitle2 text-primary q-mb-sm"
                )
                for p in [
                    "1. Hacé clic en 'Nueva guardia' en el menú lateral.",
                    "2. Completá la fecha en formato AAAA-MM-DD.",
                    "3. Seleccioná la franja horaria: Mañana, Tarde o Noche.",
                    "4. Seleccioná el grupo de trabajo o armá uno manual.",
                    "5. Registrá cada novedad y hacé clic en '+ Agregar novedad'.",
                    "6. Cuando terminés, hacé clic en 'Guardar guardia'.",
                ]:
                    with ui.row().classes("items-start q-mb-xs"):
                        ui.icon("arrow_right").classes("text-primary")
                        ui.label(p).classes("text-body2")

            with ui.tab_panel(tab2):
                ui.label("¿Cómo gestionar grupos?").classes(
                    "text-subtitle2 text-primary q-mb-sm"
                )
                for p in [
                    "1. Ir a la sección 'Grupos' en el menú lateral.",
                    "2. Creá un grupo base con nombre y miembros fijos.",
                    "3. Al crear una guardia podés seleccionar el grupo.",
                    "4. Podés registrar cambios: ausencias, licencias o incorporaciones.",
                    "5. Cada cambio queda registrado con fecha, motivo y reemplazo.",
                ]:
                    with ui.row().classes("items-start q-mb-xs"):
                        ui.icon("arrow_right").classes("text-primary")
                        ui.label(p).classes("text-body2")

            with ui.tab_panel(tab3):
                ui.label("¿Cómo gestionar operarios?").classes(
                    "text-subtitle2 text-primary q-mb-sm"
                )
                for p in [
                    "1. Ir a la sección 'Operarios' en el menú lateral.",
                    "2. En la pestaña 'Registro' podés dar de alta operarios fijos.",
                    "3. Completá legajo, nombre y apellido y hacé clic en 'Registrar'.",
                    "4. Los operarios registrados están disponibles al armar grupos.",
                    "5. Podés ver el historial de guardias por operario.",
                ]:
                    with ui.row().classes("items-start q-mb-xs"):
                        ui.icon("arrow_right").classes("text-primary")
                        ui.label(p).classes("text-body2")

            with ui.tab_panel(tab4):
                ui.label("¿Cómo gestionar herramientas?").classes(
                    "text-subtitle2 text-primary q-mb-sm"
                )
                for p in [
                    "1. Ir a la sección 'Herramientas' en el menú lateral.",
                    "2. Agregá herramientas o maquinaria con su nombre.",
                    "3. El estado inicial es 'Operativa' (verde).",
                    "4. Podés cambiar el estado a 'Defectuosa' o 'Faltante'.",
                    "5. Las herramientas con alerta aparecen en el panel principal.",
                ]:
                    with ui.row().classes("items-start q-mb-xs"):
                        ui.icon("arrow_right").classes("text-primary")
                        ui.label(p).classes("text-body2")

            with ui.tab_panel(tab5):
                ui.label("¿Cómo importar un archivo?").classes(
                    "text-subtitle2 text-primary q-mb-sm"
                )
                for p in [
                    "1. Ir a la sección 'Importar' en el menú lateral.",
                    "2. Hacé clic en 'Seleccionar archivo'.",
                    "3. El sistema acepta .txt, .pdf, .xlsx y .docx.",
                    "4. El programa muestra una vista previa de los datos.",
                    "5. Si los datos son correctos confirmás y se registra la guardia.",
                ]:
                    with ui.row().classes("items-start q-mb-xs"):
                        ui.icon("arrow_right").classes("text-primary")
                        ui.label(p).classes("text-body2")

            with ui.tab_panel(tab6):
                ui.label("Formato para archivo de novedades").classes(
                    "text-subtitle2 text-primary q-mb-sm"
                )
                ui.label(
                    "Descargá la plantilla, completála y subila desde la sección Importar."
                ).classes("text-body2 q-mb-md")

                with ui.card().classes("full-width q-pa-md"):
                    ui.label("La plantilla incluye:").classes(
                        "text-caption text-grey q-mb-sm"
                    )
                    for item in [
                        "✓ Instrucciones de uso",
                        "✓ Campos para completar (fecha, franja, operarios, herramientas, novedades)",
                        "✓ Ejemplo completo para guiarse",
                    ]:
                        ui.label(item).classes("text-body2")

                ui.button(
                    "⬇ Descargar plantilla",
                    on_click=lambda: ui.download(
                        src="formato_novedades.txt", filename="formato_novedades.txt"
                    ),
                ).props("color=primary rounded").classes("full-width q-mt-md")
                ui.timer(0.1, dialogo.open, once=True)
