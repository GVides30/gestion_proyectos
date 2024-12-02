import flet as ft
import requests
from datetime import datetime

BACKEND_URL = "http://127.0.0.1:8000"  # Cambia según tu configuración

def pantalla_bitacora(page: ft.Page):
    tabla_datos = ft.DataTable(
        columns=[],
        rows=[],
    )
    fila_seleccionada = None  # Variable para almacenar la fila seleccionada
    datos_originales = []

    def cargar_bitacora():
        """Cargar los datos de la bitácora desde el backend."""
        nonlocal datos_originales
        try:
            response = requests.get(f"{BACKEND_URL}/bitacoras")
            if response.status_code == 200:
                datos = response.json()
                datos_originales = datos  # Guardar los datos originales
                if datos:
                    mostrar_datos(datos)  # Mostrar datos cargados
                else:
                    tabla_datos.columns = [
                        ft.DataColumn(ft.Text("Información"))
                    ]
                    tabla_datos.rows = [
                        ft.DataRow(cells=[ft.DataCell(ft.Text("No hay registros disponibles"))])
                    ]
            else:
                page.snack_bar = ft.SnackBar(
                    ft.Text(f"Error al cargar bitácoras: {response.status_code}"),
                    bgcolor=ft.colors.RED,
                )
                page.snack_bar.open = True
        except Exception as ex:
            page.snack_bar = ft.SnackBar(
                ft.Text(f"Error de conexión: {ex}"), bgcolor=ft.colors.RED
            )
            page.snack_bar.open = True
        page.update()

    def mostrar_datos(datos):
        """Actualizar la tabla con los datos proporcionados."""
        columnas_visibles = ["id_bitacora", "created_at", "comentario", "km_inicial", "km_final",
                             "num_galones", "costo", "tipo_gasolina", "id_usr", "id_vehiculo", "id_gasolinera", "id_proyecto"]
        tabla_datos.columns = [
            ft.DataColumn(ft.Text(col)) for col in columnas_visibles
        ]
        tabla_datos.rows = [
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(registro[col])))
                    for col in columnas_visibles
                ],
                selected=False,
                on_select_changed=lambda e, idx=index: seleccionar_fila(idx)
            )
            for index, registro in enumerate(datos)
        ]
        page.update()

    def filtrar_datos(e):
        """Filtrar datos por fecha y comentario."""
        filtro_fecha = campo_fecha.value.strip()
        filtro_comentario = campo_busqueda.value.strip().lower()

        datos_filtrados = datos_originales
        if filtro_fecha:
            datos_filtrados = [
                registro for registro in datos_filtrados if registro["created_at"].startswith(filtro_fecha)
            ]
        if filtro_comentario:
            datos_filtrados = [
                registro for registro in datos_filtrados if filtro_comentario in registro["comentario"].lower()
            ]

        mostrar_datos(datos_filtrados)

    def seleccionar_fila(idx):
        """Manejar la selección de filas."""
        nonlocal fila_seleccionada
        for i, row in enumerate(tabla_datos.rows):
            row.selected = (i == idx)  # Marcar la fila seleccionada
        fila_seleccionada = tabla_datos.rows[idx]  # Guardar la fila seleccionada
        page.update()

    def agregar_registro(e):
        """Agregar un nuevo registro a la bitácora."""
        campos_input = {}
        campos_formulario = []

        # Definir las cabeceras para los campos a agregar, excluyendo id_bitacora y created_at
        columnas_visibles = ["comentario", "km_inicial", "km_final", "num_galones", "costo", "tipo_gasolina", "id_usr", "id_vehiculo", "id_gasolinera", "id_proyecto"]

        # Crear los campos de entrada para cada columna
        for columna_label in columnas_visibles:
            input_field = ft.TextField(
                label=columna_label, 
                value="", 
                expand=True,  
                width=500,   
            )
            campos_formulario.append(input_field)
            campos_input[columna_label] = input_field

        def guardar_nuevo(e):
            """Guardar el nuevo registro en el backend."""
            nuevos_datos = {col: campo.value for col, campo in campos_input.items()}
            nuevos_datos["created_at"] = datetime.now().isoformat()  # Agregar la fecha automáticamente
            nuevos_datos["id_bitacora"] = 0  # Asegurarse de que el ID sea 0 para la auto-generación
            print(nuevos_datos)
            try:
                response = requests.post(f"{BACKEND_URL}/bitacoras/", json=nuevos_datos)
                if response.status_code in [200, 201]:
                    page.snack_bar = ft.SnackBar(
                        ft.Text("Registro agregado exitosamente."),
                        bgcolor=ft.colors.GREEN,
                    )
                    cargar_bitacora()  # Recargar datos
                else:
                    page.snack_bar = ft.SnackBar(
                        ft.Text(f"Error al agregar registro: {response.status_code}"),
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

        page.dialog = ft.AlertDialog(
            title=ft.Text("Agregar Registro a Bitácora"),
            content=ft.Column(
                campos_formulario, 
                tight=False,  # Puedes ajustar esto para mejorar el espaciado
                spacing=15,  # Espaciado entre los campos
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _:cerrar_dialogo()),
                ft.TextButton("Guardar", on_click=guardar_nuevo),
            ],
        )
        page.dialog.open = True
        page.update()



    def modificar_registro(e):
        """Modificar un registro seleccionado."""
        if fila_seleccionada:
            registro_id = fila_seleccionada.cells[0].content.value  # ID del registro seleccionado
            campos_input = {}
            campos_formulario = []

            # Obtener datos del registro seleccionado
            registro_actual = {
                col.label.value if hasattr(col, 'label') else col: fila_seleccionada.cells[i].content.value
                for i, col in enumerate(tabla_datos.columns)
            }

            # Excluir el campo "created_at" y agregar campos editables
            for col, valor in registro_actual.items():
                if col != "created_at":  # Excluir el campo "created_at"
                    input_field = ft.TextField(label=col, value=str(valor), expand=True)
                    campos_formulario.append(input_field)
                    campos_input[col.lower().replace(" ", "_")] = input_field

            def guardar_modificacion(e):
                """Guardar los cambios en el backend."""
                try:
                    # Construir los datos nuevos a partir de los campos editables
                    nuevos_datos = {
                        key: campo.value for key, campo in campos_input.items()
                    }

                    # Asegurarse de que los campos requeridos estén en el cuerpo
                    nuevos_datos["id_bitacora"] = int(registro_id)  # Agregar el ID del registro
                    nuevos_datos["created_at"] = registro_actual.get("created_at")  # Mantener created_at sin cambios

                    # Convertir campos a enteros si es necesario
                    for campo in ["id_usr", "id_vehiculo", "id_gasolinera", "id_proyecto", "km_inicial", "km_final", "num_galones", "costo"]:
                        if campo in nuevos_datos and nuevos_datos[campo].isdigit():
                            nuevos_datos[campo] = int(nuevos_datos[campo])

                    print(f"Datos enviados para modificar: {nuevos_datos}")  # Depuración

                    # Enviar solicitud PUT al backend
                    response = requests.put(f"{BACKEND_URL}/bitacoras/{registro_id}", json=nuevos_datos)
                    if response.status_code == 200:
                        page.snack_bar = ft.SnackBar(
                            ft.Text("Registro modificado exitosamente."),
                            bgcolor=ft.colors.GREEN,
                        )
                        cargar_bitacora()  # Recargar datos
                    else:
                        error_message = response.json().get("detail", "Error desconocido")
                        page.snack_bar = ft.SnackBar(
                            ft.Text(f"Error al modificar registro: {error_message}"),
                            bgcolor=ft.colors.RED,
                        )
                    page.snack_bar.open = True
                except ValueError as ve:
                    page.snack_bar = ft.SnackBar(
                        ft.Text(f"Error en los datos: {ve}"), bgcolor=ft.colors.RED
                    )
                    page.snack_bar.open = True
                except Exception as ex:
                    page.snack_bar = ft.SnackBar(
                        ft.Text(f"Error de conexión: {ex}"), bgcolor=ft.colors.RED
                    )
                    page.snack_bar.open = True

                page.dialog.open = False
                page.update()

            # Crear diálogo para modificar registro
            page.dialog = ft.AlertDialog(
                title=ft.Text("Modificar Registro de Bitácora"),
                content=ft.Column(campos_formulario),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda _: cerrar_dialogo()),
                    ft.TextButton("Guardar", on_click=guardar_modificacion),
                ],
            )
            page.dialog.open = True
            page.update()
        else:
            page.snack_bar = ft.SnackBar(
                ft.Text("Por favor, selecciona una fila para modificar."),
                bgcolor=ft.colors.RED,
            )
            page.snack_bar.open = True



    def eliminar_registro(e):
        """Eliminar un registro seleccionado con confirmación."""
        if fila_seleccionada:
            # Obtener el ID del registro seleccionado
            registro_id = fila_seleccionada.cells[0].content.value

            # Función para confirmar la eliminación
            def confirmar_eliminacion(e):
                try:
                    # Enviar solicitud DELETE al backend
                    response = requests.delete(f"{BACKEND_URL}/bitacoras/{registro_id}")
                    if response.status_code == 204:
                        page.snack_bar = ft.SnackBar(
                            ft.Text("Registro eliminado exitosamente."),
                            bgcolor=ft.colors.GREEN,
                        )
                        cargar_bitacora()  # Recargar datos
                    else:
                        page.snack_bar = ft.SnackBar(
                            ft.Text(f"Error al eliminar registro: {response.status_code}"),
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

            # Crear cuadro de confirmación
            page.dialog = ft.AlertDialog(
                title=ft.Text("Confirmar Eliminación"),
                content=ft.Text(f"¿Estás seguro de que deseas eliminar el registro con ID {registro_id}?"),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda _: cerrar_dialogo()),
                    ft.TextButton("Eliminar", on_click=confirmar_eliminacion),
                ],
            )
            page.dialog.open = True
            page.update()
        else:
            # Mostrar mensaje si no hay fila seleccionada
            page.snack_bar = ft.SnackBar(
                ft.Text("Por favor, selecciona una fila para eliminar."),
                bgcolor=ft.colors.RED,
            )
            page.snack_bar.open = True
            page.update()

    def cerrar_dialogo():
        page.dialog.open = False
        page.update()

    def regresar(e):
        """Redirigir al usuario a la zona de administración."""
        page.go("/zona_admin")

    # Botón regresar
    boton_regresar = ft.ElevatedButton(
        text="Regresar",
        icon=ft.icons.ARROW_BACK,
        on_click=regresar,
    )

    # Cargar datos automáticamente al ingresar a la pantalla
    cargar_bitacora()

    # Componentes de filtros
    campo_fecha = ft.TextField(
        label="Filtrar por fecha (YYYY-MM-DD)", width=200, on_change=filtrar_datos
    )
    campo_busqueda = ft.TextField(
        label="Buscar por comentario",
        width=200,
        prefix_icon=ft.icons.SEARCH,
        on_change=filtrar_datos    
    )

    # Filtrar y título
    filtro_y_titulo = ft.Row(
        controls=[
            ft.Text("Bitácora de Combustible", size=30, weight=ft.FontWeight.BOLD),
            campo_fecha,
            campo_busqueda,
            boton_regresar,
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    botones_accion = ft.Row(
        controls=[
            ft.ElevatedButton("Agregar", icon=ft.icons.ADD, on_click=agregar_registro),
            ft.ElevatedButton("Modificar", icon=ft.icons.EDIT, on_click=modificar_registro),
            ft.ElevatedButton("Eliminar", icon=ft.icons.DELETE, on_click=eliminar_registro),
        ]
    )

    tabla_datos_container = ft.ListView(
        controls=[tabla_datos],
        expand=True,  # Asegura que ocupe todo el espacio disponible
    )

    return ft.Container(
        content=ft.Column(
            [
                filtro_y_titulo,
                tabla_datos_container,
                botones_accion,
            ],
            expand=True,
        ),
        expand=True,
    )
