import flet as ft

def zona_admin_view(page: ft.Page):
    titulo = ft.Text("Bienvenido a la Zona de Administración", size=30, weight=ft.FontWeight.BOLD)
    boton_volver = ft.TextButton(text="Cerrar Sesión", on_click=lambda _: page.go("/"))

    return ft.Container(
        content=ft.Column(
            [
                titulo,
                boton_volver,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        alignment=ft.alignment.center,
        expand=True,
    )
