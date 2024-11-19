import flet as ft
import requests
from datetime import datetime  # Importar para obtener la fecha y hora actual

BACKEND_URL = "http://127.0.0.1:8000"  # URL del backend

def registrar_view(page: ft.Page):
    # Contenido del formulario
    titulo = ft.Text("Registrar Nuevo Usuario", size=30, weight=ft.FontWeight.BOLD, text_align="center")
    nombre = ft.TextField(label="Nombre", width=300)
    apellido = ft.TextField(label="Apellido", width=300)
    username = ft.TextField(label="Nombre de Usuario", width=300)
    contrasena = ft.TextField(label="Contraseña", password=True, width=300)

    # Crear el Dropdown vacío inicialmente
    dropdown_rol = ft.Dropdown(
        label="Seleccionar Rol",
        options=[],  # Se cargarán dinámicamente
        width=300,
    )

    # Función para cargar los roles desde el backend
    def cargar_roles():
        try:
            response = requests.get(f"{BACKEND_URL}/roles")
            if response.status_code == 200:
                roles = response.json()
                # Rellenar el Dropdown con las opciones obtenidas
                dropdown_rol.options = [
                    ft.dropdown.Option(key=str(rol["id_rol"]), text=rol["descripcion"]) for rol in roles
                ]
                page.update()  # Asegurarse de que la página se actualice con los nuevos datos
            else:
                page.snack_bar = ft.SnackBar(ft.Text("No se pudieron cargar los roles"), bgcolor=ft.colors.RED)
                page.snack_bar.open = True
                page.update()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error al cargar los roles: {ex}"), bgcolor=ft.colors.RED)
            page.snack_bar.open = True
            page.update()

    # Función para manejar el registro de usuario
    def registrar_usuario(e):
        if not nombre.value or not apellido.value or not username.value or not contrasena.value or not dropdown_rol.value:
            page.snack_bar = ft.SnackBar(ft.Text("Por favor, completa todos los campos"), bgcolor=ft.colors.RED)
            page.snack_bar.open = True
            page.update()
            return

        # Preparar los datos para enviar al backend
        payload = {
            "id_usr": None,  # Incluir id_usr como None
            "username": username.value,
            "password": contrasena.value,
            "nombre": nombre.value,
            "apellido": apellido.value,
            "id_rol": int(dropdown_rol.value),  # Usamos el valor seleccionado del Dropdown
            "created_at": datetime.now().isoformat(),  # Añadimos la fecha y hora actual
        }

        try:
            # Enviar solicitud POST al backend usando la ruta ajustada
            response = requests.post(f"{BACKEND_URL}/", json=payload)

            if response.status_code == 200:
                page.snack_bar = ft.SnackBar(ft.Text("Usuario registrado con éxito!"), bgcolor=ft.colors.GREEN)
                page.snack_bar.open = True
                # Limpia los campos del formulario
                nombre.value = ""
                apellido.value = ""
                username.value = ""
                contrasena.value = ""
                dropdown_rol.value = None  # Restablece el Dropdown
            else:
                # Mostrar el mensaje de error del backend
                error_message = response.json().get("detail", "Error desconocido")
                page.snack_bar = ft.SnackBar(ft.Text(f"Error al registrar usuario: {error_message}"), bgcolor=ft.colors.RED)
                page.snack_bar.open = True

            page.update()

        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error de conexión: {ex}"), bgcolor=ft.colors.RED)
            page.snack_bar.open = True
            page.update()

    # Botones
    boton_registrar = ft.ElevatedButton(text="Registrar Usuario", on_click=registrar_usuario)
    boton_volver = ft.TextButton(text="Volver", on_click=lambda _: page.go("/login"))

    # Contenedor con el formulario
    container = ft.Container(
        content=ft.Column(
            [
                titulo,
                nombre,
                apellido,
                username,
                contrasena,
                dropdown_rol,
                boton_registrar,
                boton_volver,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        alignment=ft.alignment.center,
        expand=True,
    )

    # Añadir el contenedor a la página antes de cargar los roles
    page.add(container)

    # Cargar roles después de que el Dropdown haya sido agregado
    page.update()
    cargar_roles()

    return container
