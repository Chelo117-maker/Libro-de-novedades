# Componentes reutilizables de navegación usados en todas las páginas.

import os
from typing import Callable, Optional

from nicegui import ui

ESTADO_CONFIG = {
    "Operativa": {"color": "positive", "icon": "check_circle"},
    "Defectuosa": {"color": "warning", "icon": "warning"},
    "Faltante": {"color": "negative", "icon": "cancel"},
}

FRANJA_COLOR = {
    "mañana": "primary",
    "tarde": "warning",
    "noche": "purple",
}


def crear_sidebar(activo: str = "") -> ui.left_drawer:
    """Crea el drawer lateral con la navegación principal."""
    with ui.left_drawer(value=True, bordered=True).props(
        "width=200 breakpoint=500"
    ) as drawer:
        ui.label("📋 Novedades").classes("text-h6 q-pa-md")
        ui.separator()
        with ui.list().props("padding"):
            items = [
                ("inicio", "dashboard", "Inicio", "/"),
                ("nueva", "add_circle", "Nueva guardia", "/nueva-guardia"),
                ("ver", "list", "Ver todas", "/ver"),
                ("buscar", "search", "Buscar", "/buscar"),
                ("operarios", "group", "Operarios", "/operarios"),
                ("grupos", "groups", "Grupos", "/grupos"),
                ("herramientas", "build", "Herramientas", "/herramientas"),
                ("importar", "upload_file", "Importar", "/importar"),
            ]
            for clave, icono, etiqueta, ruta in items:
                with ui.item(on_click=lambda r=ruta: ui.navigate.to(r)).classes(
                    "text-primary" if activo == clave else ""
                ):
                    with ui.item_section().props("avatar"):
                        ui.icon(icono)
                    with ui.item_section():
                        ui.item_label(etiqueta)
    return drawer


def crear_header(
    drawer: ui.left_drawer,
    titulo: str = "",
    mostrar_badge: bool = False,
    mostrar_ayuda: bool = False,
    fn_ayuda: Optional[Callable] = None,
) -> None:
    """
    Crea la barra superior con menú, título, badge de estado y ayuda.

    Parámetros:
        drawer        : El drawer lateral para el botón de menú.
        titulo        : Texto del encabezado.
        mostrar_badge : Si muestra el badge de estado de guardia.
        mostrar_ayuda : Si muestra el botón de ayuda.
        fn_ayuda      : Función a llamar al hacer clic en ayuda.
                        Se importa desde cada página para evitar
                        importaciones circulares.
    """
    with ui.header(elevated=True).classes("items-center justify-between"):
        with ui.row().classes("items-center"):
            ui.button(icon="menu", on_click=drawer.toggle).props("flat round")
            ui.label(titulo).classes("text-h6")

        with ui.row().classes("items-center q-gutter-sm"):
            if mostrar_badge:
                estados = [
                    {"texto": "Guardia activa", "color": "positive"},
                    {"texto": "Grupo en pausa", "color": "warning"},
                    {"texto": "Sin guardia activa", "color": "negative"},
                ]
                estado_archivo = "estado_guardia.txt"
                idx_actual = 0
                if os.path.exists(estado_archivo):
                    try:
                        with open(estado_archivo) as f:
                            idx_actual = int(f.read().strip())
                    except Exception:
                        idx_actual = 0

                estado = {"idx": idx_actual}
                e_actual = estados[idx_actual]
                badge = ui.badge(e_actual["texto"], color=e_actual["color"]).classes(
                    "q-pa-sm cursor-pointer text-body2"
                )

                def ciclar() -> None:
                    estado["idx"] = (estado["idx"] + 1) % len(estados)
                    e = estados[estado["idx"]]
                    badge.props(f"color='{e['color']}'")
                    badge.set_text(e["texto"])
                    with open(estado_archivo, "w") as f:
                        f.write(str(estado["idx"]))

                badge.on("click", ciclar)

            if mostrar_ayuda and fn_ayuda:
                ui.button(icon="help_outline", on_click=fn_ayuda).props(
                    "flat round color=white"
                ).tooltip("Ayuda")
