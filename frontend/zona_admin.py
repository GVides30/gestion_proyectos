import flet as ft
import requests
from datetime import datetime


BACKEND_URL = "http://127.0.0.1:8000/"  # Cambia según tu configuración

def zona_admin_view(page: ft.Page):
    tabla_actual = None  
    mostrando_logs = False  # Variable para el estado del botón toggle
    fila_seleccionada = None  # Variable para almacenar la fila seleccionada

    # Definir la tabla de datos y sus columnas (por defecto, vacía)
    tabla_datos = ft.DataTable(
        columns=[],  # Inicializamos con una lista vacía, las columnas se agregarán luego
    )

    def cargar_datos_tabla(tabla):
        try:
            response = requests.get(f"{BACKEND_URL}/{tabla}")
            if response.status_code == 200:
                datos = response.json()

                # Verificar si los datos contienen registros con ID = 0
                if datos:
                    # Verificar si alguna fila tiene id=0 en las columnas de identificación
                    datos_validos = [
                        registro for registro in datos
                        if not any(
                            registro.get(col) == 0
                            for col in ["id_bitacora", "id_proyecto", "id_usr", "id_vehiculo", "id_gasolinera"]
                        )
                    ]
                    
                    if datos_validos:
                        # Configurar columnas de la tabla
                        tabla_datos.columns = [
                            ft.DataColumn(ft.Text(col)) for col in datos[0].keys()
                        ]
                        # Configurar filas de la tabla
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
                            for index, registro in enumerate(datos_validos)
                        ]
                    else:
                        tabla_datos.columns = [
                            ft.DataColumn(ft.Text("Sin datos"))
                        ]
                        tabla_datos.rows = [
                            ft.DataRow(cells=[ft.DataCell(ft.Text("No hay registros disponibles"))])
                        ]
                else:
                    tabla_datos.columns = [
                        ft.DataColumn(ft.Text("Sin datos"))
                    ]
                    tabla_datos.rows = [
                        ft.DataRow(cells=[ft.DataCell(ft.Text("No hay registros disponibles"))])
                    ]

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
        actualizar_botones()  # Actualizar botones según la nueva tabla
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
    
        actualizar_botones()  # Actualizar visibilidad de botones
        page.update()

    def agregar_nuevo(e):
        # Validar si se ha seleccionado una tabla válida
        if not tabla_actual or tabla_actual in ["logs", ""]:  # Validar que no sea "logs" o esté vacío
            page.snack_bar = ft.SnackBar(
                ft.Text("Por favor, selecciona una tabla válida antes de agregar."),
                bgcolor=ft.colors.RED,
            )
            page.snack_bar.open = True
            page.update()
            return  # Detener la ejecución si la tabla no es válida

        # Crear una referencia global para los campos de entrada
        campos_input = {}

        # Crear los TextFields para cada columna, excepto las que son auto-generadas (id_*)
        campos_formulario = []
        if tabla_actual == "users":
            columnas = ["username", "email", "role", "password"]
        elif tabla_actual == "vehiculos":
            columnas = ["modelo", "marca", "placa", "rendimiento", "galonaje", "tipo_combustible"]
        elif tabla_actual == "gasolineras":
            columnas = ["nombre", "direccion"]
        elif tabla_actual == "proyectos":
            columnas = ["nombre", "direccion", "activo"]
        elif tabla_actual == "roles":
            columnas = ["descripcion"]
        else:
            columnas = []  # Otras tablas

        # Crear los campos del formulario según las columnas
        for columna in columnas:
            input_field = ft.TextField(
                label=columna,
                value="",  # Por defecto vacío para nuevos registros
                expand=True,
            )
            campos_formulario.append(input_field)
            campos_input[columna] = input_field

        # Función para manejar el guardado
        def guardar_nuevo(e):
            # Crear el diccionario con los campos del formulario
            nuevos_datos = {
                columna: campo.value
                for columna, campo in campos_input.items()
            }
            nuevos_datos["created_at"] = datetime.now().isoformat()  # Fecha y hora actual

            # Verificar si algún campo está vacío
            for columna, valor in nuevos_datos.items():
                if not valor:  # Si el valor está vacío o es nulo
                    page.snack_bar = ft.SnackBar(
                        ft.Text(f"Por favor, llena todos los campos. El campo '{columna}' está vacío."),
                        bgcolor=ft.colors.RED,
                    )
                    page.snack_bar.open = True
                    page.update()
                    return  # Detener la ejecución y no enviar los datos

            # Añadir id con valor 0 (auto-incrementable en la base de datos)
            if "id" not in nuevos_datos:
                if tabla_actual == "gasolineras":
                    nuevos_datos["id_gasolinera"] = 0
                elif tabla_actual == "roles":
                    nuevos_datos["id_rol"] = 0
                elif tabla_actual == "proyectos":
                    nuevos_datos["id_proyecto"] = 0
                elif tabla_actual == "vehiculos":
                    nuevos_datos["id_vehiculo"] = 0
                elif tabla_actual == "users":
                    nuevos_datos["id_usr"] = 0
                elif tabla_actual == "bitacoras":
                    nuevos_datos["id_bitacora"] = 0

            # Ahora puedes enviar los datos si todos los campos están completos
            print(f"Nuevos datos a agregar: {nuevos_datos}")

            # Ajustar la ruta según la tabla actual
            if tabla_actual == "users":
                endpoint = f"{BACKEND_URL}/"  # Ruta especial para users
            elif tabla_actual == "vehiculos":
                endpoint = f"{BACKEND_URL}/{tabla_actual}/"  # Ruta especial para vehiculos
            else:
                endpoint = f"{BACKEND_URL}/{tabla_actual}"  # Ruta genérica para otras tablas

            print(f"Enviando datos a la ruta: {endpoint}")

            try:
                response = requests.post(endpoint, json=nuevos_datos)
                if response.status_code in [200, 201]:  # 201 para creado exitosamente
                    page.snack_bar = ft.SnackBar(
                        ft.Text(f"Datos agregados correctamente en la tabla {tabla_actual}"),
                        bgcolor=ft.colors.GREEN,
                    )
                    cargar_datos_tabla(tabla_actual)  # Recargar la tabla
                else:
                    error_message = response.json().get("detail", "Error desconocido")
                    page.snack_bar = ft.SnackBar(
                        ft.Text(f"Error al agregar: {error_message}"),
                        bgcolor=ft.colors.RED,
                    )
                page.snack_bar.open = True
            except Exception as ex:
                page.snack_bar = ft.SnackBar(
                    ft.Text(f"Error de conexión: {ex}"), bgcolor=ft.colors.RED
                )
                page.snack_bar.open = True

            page.dialog.open = False
            page.update()



        # Crear y abrir el cuadro de diálogo
        page.dialog = ft.AlertDialog(
            title=ft.Text(f"Agregar {tabla_actual.capitalize()}"),
            content=ft.Column(campos_formulario, tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: cerrar_dialogo()),
                ft.TextButton("Guardar", on_click=guardar_nuevo),
            ],
        )
        page.dialog.open = True
        page.update()



    def modificar_fila(e):
        if fila_seleccionada:
            # Obtener los datos de la fila seleccionada
            datos_fila = {col.label.value: cell.content.value for col, cell in zip(tabla_datos.columns, fila_seleccionada.cells)}
    
            # Crear una referencia global para los campos de entrada
            campos_input = {}

            registro_actual = {
                col.label.value if hasattr(col, 'label') else col: fila_seleccionada.cells[i].content.value
                for i, col in enumerate(tabla_datos.columns)
            }
    
            # Crear los TextFields para cada columna
            campos_formulario = []
            for columna, valor in datos_fila.items():
                if columna != "created_at":  # Excluir el campo "created_at"
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
                nuevos_datos["created_at"] = registro_actual.get("created_at")
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

    def eliminar_fila(e):
        if fila_seleccionada:
            # Obtener el ID de la fila seleccionada (suponiendo que la primera columna es el ID)
            id_fila = fila_seleccionada.cells[0].content.value

            # Confirmar eliminación
            def confirmar_eliminacion(e):
                try:
                    # Hacer una solicitud DELETE al backend
                    response = requests.delete(f"{BACKEND_URL}/{tabla_actual}/{id_fila}")
                    if response.status_code == 204:  # Código HTTP 204: No Content (eliminación exitosa)
                        page.snack_bar = ft.SnackBar(
                            ft.Text(f"Fila eliminada correctamente de la tabla {tabla_actual}"),
                            bgcolor=ft.colors.GREEN,
                        )
                        cargar_datos_tabla(tabla_actual)  # Recargar la tabla
                    else:
                        error_message = response.json().get("detail", "Error desconocido")
                        page.snack_bar = ft.SnackBar(
                            ft.Text(f"Error al eliminar: {error_message}"),
                            bgcolor=ft.colors.RED,
                        )
                    page.snack_bar.open = True
                except Exception as ex:
                    page.snack_bar = ft.SnackBar(
                        ft.Text(f"Error de conexión: {ex}"), bgcolor=ft.colors.RED
                    )
                    page.snack_bar.open = True

                # Cerrar el cuadro de confirmación
                page.dialog.open = False
                page.update()

            # Cuadro de confirmación
            page.dialog = ft.AlertDialog(
                title=ft.Text(f"Eliminar fila de {tabla_actual.capitalize()}"),
                content=ft.Text(f"¿Estás seguro de que deseas eliminar el registro con ID {id_fila}?"),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda _: cerrar_dialogo()),
                    ft.TextButton("Eliminar", on_click=confirmar_eliminacion),
                ],
            )
            page.dialog.open = True
            page.update()
        else:
            # Mostrar un mensaje si no hay fila seleccionada
            page.snack_bar = ft.SnackBar(
                ft.Text("Por favor, selecciona una fila para eliminar."),
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
            ft.DataColumn(ft.Text("Temporal"))  # Columna por defecto
        ],
        rows=[
            ft.DataRow(cells=[ft.DataCell(ft.Text("Seleccione una tabla para visualizar"))])
        ],
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

    agregar_button = ft.ElevatedButton(
        text="Agregar",
        icon=ft.icons.ADD,
        on_click=agregar_nuevo,
        visible=True,
    )

    eliminar_button = ft.ElevatedButton(
        text="Eliminar",
        icon=ft.icons.DELETE,
        on_click=eliminar_fila,
        visible=True,
    )

    bitacora_button = ft.ElevatedButton(
        text="Ir a Bitácora",
        icon=ft.icons.BOOK,
        on_click=lambda e: redirigir_a_bitacora(e),  # Redirige a la pantalla de bitácora
    )

    def redirigir_a_bitacora(e):
        """Redirige a la pantalla de Bitácora"""
        page.go("/bitacora")


    botones_accion = ft.Row(
        controls=[
            agregar_button,
            eliminar_button,
            modificar_button,  # Botón Modificar
            toggle_button,  # Botón Ver Logs
            bitacora_button,
        ]
    )

    def actualizar_botones():
        # Ocultar botones cuando estamos en "logs" o no se ha seleccionado una tabla
        if mostrando_logs or tabla_actual == "logs":
            agregar_button.visible = False
            eliminar_button.visible = False
            modificar_button.visible = False
            bitacora_button.visible = False
        else:
            # Mostrar botones solo cuando estamos en una tabla válida
            agregar_button.visible = True
            eliminar_button.visible = True
            modificar_button.visible = True
            bitacora_button.visible = True

        # Mostrar el botón "Ver Logs" solo en la tabla de usuarios
        toggle_button.visible = tabla_actual == "users"
        page.update()


    def cambiar_tabla_y_actualizar(e):
        cambiar_tabla(e)
        actualizar_botones()

    barra_navegacion.on_change = cambiar_tabla_y_actualizar

    tabla_datos_container = ft.ListView(
        controls=[tabla_datos],
        expand=True,  # Asegura que ocupe todo el espacio disponible
    )

    page.add(tabla_datos)
    return ft.Container(
        content=ft.Row(
            [
                barra_navegacion,
                ft.Column(
                    [
                        ft.Text("Zona de Administración", size=30, weight=ft.FontWeight.BOLD),
                        tabla_datos_container,  # Reemplaza con el contenedor con scroll
                        botones_accion,
                    ],
                    expand=True,
                ),
            ],
            expand=True,
        ),
        expand=True,
    )