import flet as ft

def registrar_view(page: ft.Page):
    # Función para manejar el registro de un nuevo usuario
    def registrar_usuario(e):
        if nuevo_usuario.value and nueva_contrasena.value:  # Solo verifica usuario y contraseña
            page.snack_bar = ft.SnackBar(ft.Text(f"Usuario {nuevo_usuario.value} registrado con éxito!"))
            page.snack_bar.open = True
            nuevo_usuario.value = ""
            nueva_contrasena.value = ""
            page.update()
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Por favor, completa todos los campos"), bgcolor=ft.colors.RED)
            page.snack_bar.open = True
            page.update()

    # Contenido del Registro
    titulo = ft.Text("Registrar Nuevo Usuario", size=30, weight=ft.FontWeight.BOLD, text_align="center")
    nuevo_usuario = ft.TextField(label="Usuario", width=300)
    nueva_contrasena = ft.TextField(label="Contraseña", password=True, width=300)
    boton_registrar = ft.ElevatedButton(text="Registrar Usuario", on_click=registrar_usuario)
    boton_volver = ft.TextButton(text="Volver", on_click=lambda _: page.go("/login"))

    return ft.Container(
        content=ft.Column(
            [
                titulo,
                nuevo_usuario,
                nueva_contrasena,
                boton_registrar,
                boton_volver,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        alignment=ft.alignment.center,
        expand=True,
    )
