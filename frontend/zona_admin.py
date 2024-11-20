import flet as ft
import requests

BACKEND_URL = "http://127.0.0.1:8000"  # Cambia según tu configuración

def zona_admin_view(page: ft.Page):
    tabla_actual = "users"  # Inicializar tabla actual como usuarios
    mostrando_logs = False  # Variable para el estado del botón toggle

    def cargar_datos_tabla(tabla):
        try:
            response = requests.get(f"{BACKEND_URL}/{tabla}")
            if response.status_code == 200:
                datos = response.json()
                if datos:
                    # Configurar columnas
                    tabla_datos.columns = [
                        ft.DataColumn(ft.Text(col)) for col in datos[0].keys()
                    ]
                    # Configurar filas
                    tabla_datos.rows = [
                        ft.DataRow(
                            cells=[
                                ft.DataCell(
                                    ft.Text(
                                        str(campo) if col != "password" else "******"
                                    )
                                )
                                for col, campo in registro.items()
                            ]
                        )
                        for registro in datos
                    ]
                else:
                    tabla_datos.columns = [
                        ft.DataColumn(ft.Text("ID")),
                        ft.DataColumn(ft.Text("Nombre")),
                    ]
                    tabla_datos.rows = []
            else:
                page.snack_bar = ft.SnackBar(
                    ft.Text(f"Error al cargar datos: {response.status_code}"),
                    bgcolor=ft.colors.RED,
                )
                page.snack_bar.open = True
        except Exception as ex:
            page.snack_bar = ft.SnackBar(
                ft.Text(f"Error de conexión: {ex}"), bgcolor=ft.colors.RED
            )
            page.snack_bar.open = True
        page.update()

    def cambiar_tabla(e):
        nonlocal tabla_actual, mostrando_logs
        tablas = ["users", "roles", "vehiculos", "proyectos", "gasolineras"]
        tabla_actual = tablas[e.control.selected_index]
        mostrando_logs = False  # Resetear el estado del botón toggle
        cargar_datos_tabla(tabla_actual)
        page.update()

    def toggle_logs(e):
        nonlocal mostrando_logs
        mostrando_logs = not mostrando_logs
        if mostrando_logs:
            cargar_datos_tabla("logs")  # Cargar tabla logs
            toggle_button.text = "Ver Usuarios"
        else:
            cargar_datos_tabla("users")  # Cargar tabla usuarios
            toggle_button.text = "Ver Logs"
        page.update()

    barra_navegacion = ft.NavigationRail(
        selected_index=0,
        destinations=[
            ft.NavigationRailDestination(icon=ft.icons.PERSON, label="Usuarios"),
            ft.NavigationRailDestination(icon=ft.icons.ADMIN_PANEL_SETTINGS, label="Roles"),
            ft.NavigationRailDestination(icon=ft.icons.CAR_RENTAL, label="Vehículos"),
            ft.NavigationRailDestination(icon=ft.icons.BUILD, label="Proyectos"),
            ft.NavigationRailDestination(icon=ft.icons.LOCAL_GAS_STATION, label="Gasolineras"),
        ],
        on_change=cambiar_tabla,
    )

    tabla_datos = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),  # Inicializar con columnas visibles
            ft.DataColumn(ft.Text("Nombre")),
        ],
        rows=[],
    )

    toggle_button = ft.ElevatedButton(
        text="Ver Logs",
        icon=ft.icons.VIEW_LIST,
        on_click=toggle_logs,
        visible=False,  # Inicialmente oculto
    )

    botones_accion = ft.Row(
        controls=[
            ft.ElevatedButton("Agregar", icon=ft.icons.ADD),
            ft.ElevatedButton("Eliminar", icon=ft.icons.DELETE),
            toggle_button,  # Agregar el botón de toggle a los controles
        ]
    )

    # Mostrar u ocultar el botón de toggle según la tabla actual
    def actualizar_botones():
        toggle_button.visible = tabla_actual == "users"  # Mostrar solo en Usuarios
        page.update()

    # Llamar a esta función cada vez que se cambie la tabla
    def cambiar_tabla_y_actualizar(e):
        cambiar_tabla(e)
        actualizar_botones()

    # Asociar la nueva función al evento de cambio de tabla
    barra_navegacion.on_change = cambiar_tabla_y_actualizar

    return ft.Container(
        content=ft.Row(
            [
                barra_navegacion,
                ft.Column(
                    [
                        ft.Text("Zona de Administración", size=30, weight=ft.FontWeight.BOLD),
                        tabla_datos,
                        botones_accion,
                    ],
                    expand=True,
                ),
            ],
            expand=True,
        ),
        expand=True,
    )
