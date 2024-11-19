import flet as ft
from login import login_view
from registrar import registrar_view
from zona_admin import zona_admin_view 

def main(page: ft.Page):
    def route_change(route):
        page.views.clear()

        if page.route == "/":
            page.views.append(
                ft.View(
                    "/",
                    [
                        ft.Container(  # Usamos un contenedor para alinear el contenido
                            content=ft.Column(
                                [
                                    ft.Text(
                                        "Bienvenido a la Aplicación",
                                        size=30,
                                        weight=ft.FontWeight.BOLD,
                                        text_align="center",
                                    ),
                                    ft.Text("Controla, administra y reporta fácilmente", size=18, color=ft.colors.BLUE, text_align="center"),
                                    ft.ElevatedButton(
                                        text="Ir al Login",
                                        on_click=lambda _: page.go("/login"),
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            alignment=ft.alignment.center,  # Centrar el contenedor
                            expand=True,  # Expandir el contenedor para ocupar todo el espacio disponible
                        )
                    ]
                )
            )
        elif page.route == "/login":
            page.views.append(
                ft.View(
                    "/login",
                    [login_view(page)],
                )
            )
        elif page.route == "/registrar":
            page.views.append(
                ft.View(
                    "/registrar",
                    [registrar_view(page)],
                )
            )
        elif page.route == "/zona_admin":  # Agregar esta condición para la nueva ruta
            page.views.append(
                ft.View(
                    "/zona_admin",
                    [zona_admin_view(page)],  # Llama a la vista de zona_admin
                )
            )
        page.update()

    page.on_route_change = route_change
    page.go("/")  # Ruta inicial

ft.app(target=main)
