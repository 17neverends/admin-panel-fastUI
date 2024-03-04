from typing import Annotated
from fastui.forms import fastui_form
from fastapi import APIRouter
from fastui import AnyComponent, FastUI
from fastui import components as c
from fastui.components.display import DisplayLookup
from fastui.events import BackEvent, GoToEvent, PageEvent
from pydantic import BaseModel, Field
from config import user, password, db_name, host, port
from psql import PSQL
from shared import demo_page


psql = PSQL(db_name, user, password, host, port)
router = APIRouter()


class User(BaseModel):
    id: str = Field(title="ID")
    name: str = Field(title="Имя")
    age: str = Field(title="Возраст")

class getBackupStep(BaseModel):
    steps: int = Field(title="Иногда для прыжка вперёд требуется отступить на два шага назад. — А иногда надо лишь иметь желание прыгнуть.")

class Actions(BaseModel):
    backup_id: str = Field(title="ID")
    operation_type: str = Field(title="Тип операции")
    column_name: str = Field(title="Поле")
    old_value: str = Field(title="Прошлое значение")
    new_value: str = Field(title="Новое значение")



def fetch_users():
    query = "SELECT id, name, age FROM users;"
    psql.connect()
    data = psql.fetch_all(query=query)
    psql.disconnect()
    users = [User(id=row[0],name=row[1], age=row[2]) for row in data]
    return users

def fetch_actions():
    query = "SELECT backup_id, operation_type, column_name, old_value, new_value FROM actions;"
    psql.connect()
    data = psql.fetch_all(query=query)
    psql.disconnect()
    actions = []
    for row in data:
        old_value = row[3] if row[3] is not None else ""
        new_value = row[4] if row[4] is not None else ""
        action = Actions(backup_id=str(row[0]),  
                         operation_type=row[1], 
                         column_name=row[2],
                         old_value=old_value,
                         new_value=new_value)
        actions.append(action)
    return actions




@router.get('/actions', response_model=FastUI, response_model_exclude_none=True)
def actions_view() -> list[AnyComponent]:
    global actions
    actions = fetch_actions()
    return demo_page(
        *tabs(),
        c.Table(
            data=actions,
            data_model = Actions,
            columns=[
                DisplayLookup(field='backup_id'),
                DisplayLookup(field='operation_type'),
                DisplayLookup(field='column_name'),
                DisplayLookup(field='old_value'),
                DisplayLookup(field='new_value'),
            ],
        ),
        c.Button(text="Сделать бэкап", on_click=GoToEvent(url="/table/users/backup")),
        title='Логи',
    )

def tabs() -> list[AnyComponent]:
    return [
        c.LinkList(
            links=[
                c.Link(
                    components=[c.Text(text='Данные')],
                    on_click=GoToEvent(url='/table/users'),
                    active='startswith:/table/users',
                ),
                c.Link(
                    components=[c.Text(text='Логи')],
                    on_click=GoToEvent(url='/table/actions'),
                    active='startswith:/table/actions',
                ),
            ],
            mode='tabs',
            class_name='+ mb-4',
        ),
    ]


@router.get('/users', response_model=FastUI, response_model_exclude_none=True)
def users_view() -> list[AnyComponent]:
    global users
    users = fetch_users()
    return demo_page(
        *tabs(),
        c.Table(
            data=users,
            data_model = User,
            columns=[
                DisplayLookup(field='id', on_click=GoToEvent(url='/table/users/{id}/')),
                DisplayLookup(field='name'),
                DisplayLookup(field='age'),
            ],
        ),
        c.Button(text="Добавить пользователя", on_click=GoToEvent(url='/table/users/add')),
        c.Paragraph(text="     "),
        c.Button(text='Modal Add', on_click=PageEvent(name='modal-form')),
        c.Modal(
            title='Добавление пользователя',
            body=[
                c.Paragraph(text='Введите данные:'),
                c.Form(
                form_fields=[
                    
                    c.FormFieldInput(name='id', title='ID'),
                    c.FormFieldInput(name='name', title='Имя'),
                    c.FormFieldInput(name='age', title='Возраст'),
                ],                         
                submit_url='/api/table/modalform',
                footer=[],
                submit_trigger=PageEvent(name='modal-form-submit'),
                ),
            ],
            footer=[
                c.Button(
                    text='Отмена', on_click=PageEvent(name='modal-form', clear=True)
                ),
                c.Button(text='Принять', on_click=PageEvent(name='modal-form-submit')),
            ],
            open_trigger=PageEvent(name='modal-form'),
        ),        
        title='Пользователи',
        
    )



@router.get('/users/{id}/', response_model=FastUI, response_model_exclude_none=True)
def user_profile(id: int) -> list[AnyComponent]:
    global old_id
    old_id = id
    user = next(u for u in users if int(u.id) == id)
    return demo_page(
        c.Link(components=[c.Text(text='Назад')], on_click=BackEvent()),
        c.Details(
            data=user,
            fields=[
                DisplayLookup(field='id'),
                DisplayLookup(field='name'),
                DisplayLookup(field='age'),
            ],
        ),
        c.Button(text="Удалить пользователя", on_click=PageEvent(name="delete-user")),
        c.Paragraph(text="     "),
        c.Button(text="Изменить данные", on_click=GoToEvent(url='/table/users/update')),
        c.Form(
                    submit_url="/api/table/userdelete",
                    form_fields=[
                        c.FormFieldInput(name='id', title='', initial=id, html_type='hidden'),
                        c.FormFieldInput(name='name', title='', initial=id, html_type='hidden'),
                        c.FormFieldInput(name='age', title='', initial=id, html_type='hidden'),
                    ],
                    footer=[],
                    submit_trigger=PageEvent(name="delete-user"),
                ),

        title=f"Пользователь ID: {id}",
    )


@router.get('/users/add', response_model=FastUI, response_model_exclude_none=True)
def user_add() -> list[AnyComponent]:
    return demo_page(
        c.Heading(text='Добавить пользователя', level=2),
        c.Link(components=[c.Text(text='Назад')], on_click=BackEvent()),
        c.ModelForm(
            model=User,
            submit_url="/api/table/useradd"
        )
    )

@router.get("/users/update", response_model=FastUI, response_model_exclude_none=True)
def add_user_page():
    return [
        c.Page(
            components=[
                c.Link(components=[c.Text(text='Назад')], on_click=BackEvent()),
                c.Heading(text='Обновить данные', level=2),
                c.ModelForm(
                    model=User,
                    submit_url="/api/table/userupdate"
                )
            ]
        )
    ]


@router.post("/useradd")
def add_user(form: Annotated[User, fastui_form(User)]):
    psql.connect()
    psql.execute_query("INSERT INTO users (id, name, age) VALUES (%s, %s, %s)", (form.id, form.name, form.age))
    psql.disconnect()
    return [c.FireEvent(event=GoToEvent(url='/table/users'))]


@router.post("/userupdate")
def add_user(form: Annotated[User, fastui_form(User)]):
    print(old_id)
    psql.connect()
    try:
        psql.execute_query("UPDATE users SET id = %s, name = %s, age = %s WHERE id = %s", (form.id, form.name, form.age, str(old_id)))
    except Exception as e:
        print("Error executing query:", e)
    psql.disconnect()
    return [c.FireEvent(event=GoToEvent(url='/table/users'))]


@router.post("/userdelete")
def delete_user(form: Annotated[User, fastui_form(User)]):
    psql.connect()
    psql.execute_query("DELETE FROM users WHERE id = %s", (form.id,))
    psql.disconnect()
    return [c.FireEvent(event=GoToEvent(url='/table/users'))]


@router.get("/users/backup", response_model=FastUI, response_model_exclude_none=True)
def add_user_page():
    return [
        c.Page(
            components=[
                c.Link(components=[c.Text(text='Назад')], on_click=BackEvent()),
                c.Heading(text='Сделать бэкап', level=2),
                c.ModelForm(
                    model=getBackupStep,
                    submit_url="/api/table/backup"
                )
            ]
        )
    ]


@router.post("/backup")
def add_steps(form: Annotated[getBackupStep, fastui_form(getBackupStep)]):
    psql.connect()
    psql.execute_query(f"SELECT manual_backup({form.steps})")
    psql.disconnect()
    return [c.FireEvent(event=GoToEvent(url='/table/users'))]



@router.post('/modalform', response_model=FastUI, response_model_exclude_none=True)
def modal_form_submit(form: Annotated[User, fastui_form(User)])  -> list[AnyComponent]:
    psql.connect()
    psql.execute_query("INSERT INTO users (id, name, age) VALUES (%s, %s, %s)", (form.id, form.name, form.age))
    psql.disconnect()
    global users
    users = fetch_users()
    return [c.FireEvent(event=PageEvent(name='modal-form', clear=True)),
            c.FireEvent(event=GoToEvent(url='/table/users'))]
