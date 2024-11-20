import flet as ft
import requests

BACKEND_URL = "http://127.0.0.1:8000"  # Cambia según tu configuración

def zona_admin_view(page: ft.Page):
    tabla_actual = "users"  # Inicializar tabla actual como usuarios
    mostrando_logs = False  # Variable para el estado del botón toggle
    fila_seleccionada = None  # Variable para almacenar la fila seleccionada

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
                            ],
                            selected=False,  # Por defecto no está seleccionada
                            on_select_changed=lambda e, idx=index: seleccionar_fila(e, idx)
                        )
                        for index, registro in enumerate(datos)
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

    def seleccionar_fila(e, index):
        nonlocal fila_seleccionada
        for i, row in enumerate(tabla_datos.rows):
            row.selected = i == index  # Solo resaltar la fila seleccionada
        fila_seleccionada = tabla_datos.rows[index]  # Guardar la fila seleccionada
        page.update()

    def cambiar_tabla(e):
        nonlocal tabla_actual, mostrando_logs, fila_seleccionada
        tablas = ["users", "roles", "vehiculos", "proyectos", "gasolineras"]
        tabla_actual = tablas[e.control.selected_index]
        mostrando_logs = False  # Resetear el estado del botón toggle
        fila_seleccionada = None  # Restablecer la fila seleccionada
        cargar_datos_tabla(tabla_actual)  # Cargar los datos de la nueva tabla
        actualizar_botones()
        page.update()

    def toggle_logs(e):
        nonlocal mostrando_logs
        mostrando_logs = not mostrando_logs
        if mostrando_logs:
            cargar_datos_tabla("logs")  # Cargar tabla logs
            toggle_button.text = "Ver Usuarios"
            modificar_button.visible = False  # Ocultar el botón Modificar
        else:
            cargar_datos_tabla("users")  # Cargar tabla usuarios
            toggle_button.text = "Ver Logs"
            modificar_button.visible = True  # Mostrar el botón Modificar
        page.update()

    def modificar_fila(e):
        if fila_seleccionada:
            # Obtener los datos de la fila seleccionada
            datos_fila = {col.label.value: cell.content.value for col, cell in zip(tabla_datos.columns, fila_seleccionada.cells)}
    
            # Crear una referencia global para los campos de entrada
            campos_input = {}
    
            # Crear los TextFields para cada columna
            campos_formulario = []
            for columna, valor in datos_fila.items():
                input_field = ft.TextField(
                    label=columna,
                    value=str(valor),
                    expand=True,
                )
                campos_formulario.append(input_field)
                campos_input[columna] = input_field
    
            # Función para manejar el guardado
            def guardar_modificacion(e):
                nuevos_datos = {columna: campo.value for columna, campo in campos_input.items()}
                print(f"Nuevos datos a guardar: {nuevos_datos}")
    
                # Enviar los datos al backend
                try:
                    response = requests.put(f"{BACKEND_URL}/{tabla_actual}/{nuevos_datos[tabla_datos.columns[0].label.value]}", json=nuevos_datos)
                    if response.status_code == 200:
                        page.snack_bar = ft.SnackBar(
                            ft.Text(f"Datos actualizados correctamente en la tabla {tabla_actual}"),
                            bgcolor=ft.colors.GREEN,
                        )
                        cargar_datos_tabla(tabla_actual)  # Recargar la tabla
                    else:
                        page.snack_bar = ft.SnackBar(
                            ft.Text(f"Error al actualizar: {response.status_code}"),
                            bgcolor=ft.colors.RED,
                        )
                    page.snack_bar.open = True
                except Exception as ex:
                    page.snack_bar = ft.SnackBar(
                        ft.Text(f"Error de conexión: {ex}"), bgcolor=ft.colors.RED
                    )
                    page.snack_bar.open = True
    
                # Cerrar el cuadro de diálogo
                page.dialog.open = False
                page.update()
    
            # Crear y abrir el diálogo
            page.dialog = ft.AlertDialog(
                title=ft.Text(f"Modificar {tabla_actual.capitalize()}"),
                content=ft.Column(campos_formulario, tight=True),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda _: cerrar_dialogo()),
                    ft.TextButton("Guardar", on_click=guardar_modificacion),
                ],
            )
            page.dialog.open = True
            page.update()
        else:
            # Mostrar error si no hay fila seleccionada
            page.snack_bar = ft.SnackBar(
                ft.Text("Por favor, selecciona una fila para modificar."),
                bgcolor=ft.colors.RED,
            )
            page.snack_bar.open = True
            page.update()

    # Función para cerrar el diálogo
    def cerrar_dialogo():
        page.dialog.open = False
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

    modificar_button = ft.ElevatedButton(
        text="Modificar",
        icon=ft.icons.EDIT,
        on_click=modificar_fila,
        visible=True,  # Controlado dinámicamente
    )

    botones_accion = ft.Row(
        controls=[
            ft.ElevatedButton("Agregar", icon=ft.icons.ADD),
            ft.ElevatedButton("Eliminar", icon=ft.icons.DELETE),
            modificar_button,  # Botón Modificar
            toggle_button,  # Botón Ver Logs
        ]
    )

    def actualizar_botones():
        toggle_button.visible = tabla_actual == "users"  # Mostrar solo en Usuarios
        modificar_button.visible = not mostrando_logs  # Ocultar Modificar si está en Logs
        page.update()

    def cambiar_tabla_y_actualizar(e):
        cambiar_tabla(e)
        actualizar_botones()

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
