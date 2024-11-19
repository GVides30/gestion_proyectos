import flet as ft

def login_view(page: ft.Page):
    # Función para manejar el inicio de sesión
    def iniciar_sesion(e):
        if usuario.value and contrasena.value:
            page.snack_bar = ft.SnackBar(ft.Text(f"Bienvenido, {usuario.value}!"))
            page.snack_bar.open = True
            page.update()
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Por favor, completa todos los campos"), bgcolor=ft.colors.RED)
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
