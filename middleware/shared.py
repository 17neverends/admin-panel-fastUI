from fastui import AnyComponent
from fastui import components as c
from fastui.events import GoToEvent


def demo_page(*components: AnyComponent, title: str | None = None) -> list[AnyComponent]:
    return [
        c.PageTitle(text=f'Admin — {title}' if title else 'Admin'),
        c.Navbar(
            title='Admin',
            title_event=GoToEvent(url='/'),
            start_links=[
                c.Link(
                    components=[c.Text(text='Пользователи')],
                    on_click=GoToEvent(url='/table/users'),
                    active='startswith:/table',
                )
            ]
        ),
        c.Page(
            components=[
                *((c.Heading(text=title),) if title else ()),
                *components,
            ],
        ),
        c.Footer(
            extra_text='Admin panel',
            links=[
                c.Link(
                    components=[c.Text(text='Github')], on_click=GoToEvent(url='https://github.com/17neverends')
                ),
            ],
        ),
    ]