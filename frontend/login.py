import flet as ft
import requests

BACKEND_URL = "http://127.0.0.1:8000"  # URL del backend

def login_view(page: ft.Page):
    # Función para manejar el inicio de sesión
    def iniciar_sesion(e):
        if not usuario.value.strip() or not contrasena.value.strip():
            page.snack_bar = ft.SnackBar(ft.Text("Por favor, completa todos los campos"), bgcolor=ft.colors.RED)
            page.snack_bar.open = True
            page.update()
            return

        # Preparar los datos para la solicitud de autenticación
        payload = {
            "username": usuario.value,
            "password": contrasena.value,
        }

        try:
            # Enviar solicitud POST al backend para verificar las credenciales
            response = requests.post(f"{BACKEND_URL}/login/login", params=payload)

            if response.status_code == 200:
                # Inicio de sesión exitoso
                data = response.json()
                page.snack_bar = ft.SnackBar(ft.Text(f"Bienvenido, {data['name']}!"), bgcolor=ft.colors.GREEN)
                page.snack_bar.open = True

                # Guardar datos del usuario en la sesión
                page.session.set("user_data", data)

                # Redirigir al usuario a otra página, por ejemplo, el dashboard
                page.go("/zona_admin")
            else:
                # Mostrar mensaje de error proporcionado por el backend
                error_message = response.json().get("detail", "Credenciales incorrectas")
                page.snack_bar = ft.SnackBar(ft.Text(f"Error: {error_message}"), bgcolor=ft.colors.RED)
                page.snack_bar.open = True

            page.update()
        except Exception as ex:
            # Manejar errores de conexión o solicitudes
            page.snack_bar = ft.SnackBar(ft.Text(f"Error de conexión: {ex}"), bgcolor=ft.colors.RED)
            page.snack_bar.open = True
            page.update()

    # Contenido del Login
    titulo = ft.Text("Inicia Sesión", size=30, weight=ft.FontWeight.BOLD, text_align="center")
    usuario = ft.TextField(label="Usuario", width=300)
    contrasena = ft.TextField(label="Contraseña", password=True, width=300)
    boton_iniciar = ft.ElevatedButton(text="Iniciar Sesión", on_click=iniciar_sesion)
    boton_registrar = ft.TextButton(text="Registrar Nuevo Usuario", on_click=lambda _: page.go("/registrar"))
    boton_volver = ft.TextButton(text="Volver", on_click=lambda _: page.go("/"))

    return ft.Container(
        content=ft.Column(
            [
                titulo,
                usuario,
                contrasena,
                boton_iniciar,
                boton_registrar,
                boton_volver,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        alignment=ft.alignment.center,
        expand=True,
    )
