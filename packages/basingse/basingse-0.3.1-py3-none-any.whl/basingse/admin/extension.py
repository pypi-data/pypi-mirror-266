import dataclasses as dc
import os.path
from collections.abc import Callable
from collections.abc import Iterable
from collections.abc import Iterator
from typing import Any
from typing import ClassVar
from typing import Generic
from typing import IO
from typing import overload
from typing import TypeVar

import attrs
import click
import structlog
from blinker import signal
from bootlace.icon import Icon
from bootlace.links import View as ViewLink
from bootlace.nav import NavStyle
from bootlace.nav.elements import Link
from bootlace.nav.elements import Nav
from bootlace.table import Table
from bootlace.util import as_tag
from bootlace.util import render
from flask import abort
from flask import Blueprint
from flask import current_app
from flask import Flask
from flask import has_app_context
from flask import render_template
from flask import request
from flask import url_for
from flask.cli import with_appcontext
from flask.typing import ResponseReturnValue as IntoResponse
from flask.views import View
from flask_attachments import Attachment
from flask_login import current_user
from flask_wtf import FlaskForm as FormBase
from jinja2 import FileSystemLoader
from jinja2 import Template
from markupsafe import Markup
from marshmallow import Schema
from sqlalchemy import delete
from sqlalchemy import select
from sqlalchemy.orm import Session
from wtforms import FileField
from wtforms import Form

from basingse.auth.permissions import require_permission
from basingse.auth.utils import redirect_next
from basingse.htmx import HtmxProperties
from basingse.models import Model as ModelBase
from basingse.svcs import get

log: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)

M = TypeVar("M", bound=ModelBase)
F = TypeVar("F", bound=FormBase)
Fn = TypeVar("Fn", bound=Callable)

on_new = signal("new")
on_update = signal("update")
on_delete = signal("delete")
on_submit = signal("submit")


@attrs.define(init=False)
class PortalMenuItem(Link):
    """
    A menu item for the admin portal
    """

    permissions: str | None = None

    # This ordering is frozen for backwards compatibility
    def __init__(self, label: str, view: str, icon: str | Icon, permissions: str) -> None:
        if isinstance(icon, str):
            icon = Icon(icon)

        link = ViewLink(endpoint=view, text=[icon, " ", label])

        super().__init__(link=link)
        self.permissions = permissions

    @property
    def enabled(self) -> bool:
        if self.permissions is None:
            return True
        return current_user.can(self.permissions)


@dc.dataclass
class Portal:

    blueprint: Blueprint
    items: list[PortalMenuItem] = dc.field(default_factory=list)

    def __post_init__(self) -> None:
        self.blueprint.context_processor(self.context)

    def add(self, item: PortalMenuItem) -> None:
        self.items.append(item)

    def _render_nav(self) -> Markup:
        ul = as_tag(Nav([item for item in self.items if item.enabled], style=NavStyle.PILLS))
        ul.classes.add("flex-column", "mb-auto")
        return render(ul)

    def context(self) -> dict[str, Any]:
        return {
            "nav": self._render_nav(),
            "hx": HtmxProperties,
            "base_template": base_template(),
            "form_encoding": get_form_encoding,
        }


def get_form_encoding(form: Form) -> str:
    """Get the form encoding type"""
    for field in form:
        if isinstance(field, FileField):
            return "multipart/form-data"
        if (widget := getattr(field, "widget", None)) is not None:
            if getattr(widget, "input_type", None) == "file":
                return "multipart/form-data"
    return "application/x-www-form-urlencoded"


def base_template() -> Template:
    name = current_app.config.get("BASINGSE_ADMIN_BASE_TEMPLATE", ["admin/customize.html", "admin/base.html"])
    return current_app.jinja_env.get_or_select_template(name)


@dc.dataclass
class Action:
    """
    Record for admin action decorators
    """

    name: str
    permission: str
    url: str
    methods: list[str] = dc.field(default_factory=list)
    defaults: dict[str, Any] = dc.field(default_factory=dict)
    attachments: bool = False


@overload
def action(fn: Fn) -> Fn: ...


@overload
def action(**options: Any) -> Callable[[Any], Callable[[Fn], Fn]]: ...


def action(*args: Any, **options: Any) -> Callable[[Any], Callable[[Fn], Fn]]:
    """Mark a function as an action"""

    def decorate(func: Fn) -> Fn:
        name = options.setdefault("name", func.__name__)

        if name in {"list", "preview"}:
            options.setdefault("permission", "view")
        elif name == "new":
            options.setdefault("permission", "edit")
        else:
            options.setdefault("permission", name)

        if name in {"preview", "edit"}:
            options.setdefault("url", f"/<key>/{name}/")
        else:
            options.setdefault("url", f"/{name}/")

        if options.get("permission") == "view":
            options.setdefault("methods", ["GET"])
        elif options.get("permission") == "edit":
            options.setdefault("methods", ["GET", "POST", "PATCH", "PUT"])
        elif options.get("permission") == "delete":
            options.setdefault("methods", ["GET", "DELETE"])

        func.action = Action(**options)  # type: ignore
        return func

    if args:
        if len(args) > 1:  # pragma: nocover
            raise TypeError(f"action() takes at most 1 positional argument ({len(args)} given)")
        return decorate(args[0])

    return decorate


class AdminView(View, Generic[M, F]):
    #: base url for this view
    url: ClassVar[str]

    #: Url template for identifying an individual instance
    key: ClassVar[str]

    #: The form to use for this view
    form: type[F]

    #: The model to use for this view
    model: type[M]

    #: The schema to use for API responses
    schema: type[Schema] | None = None

    #: The table to use for rendering list views
    table: type[Table] | None = None

    #: The name of this view
    name: ClassVar[str]

    #: The permission namespace to use for this view
    permission: ClassVar[str]

    #: A class-specific blueprint, where this view's routes are registered.
    bp: ClassVar[Blueprint]

    #: The template to use for attachments
    attachments: ClassVar[str | None] = None

    #: The CLI group to use for importers
    importer_group: ClassVar[click.Group] = click.Group("import", help="Import data from YAML files")

    #: The CLI group to use for exporters
    exporter_group: ClassVar[click.Group] = click.Group("export", help="Export data to YAML files")

    # The navigation item for this view
    nav: ClassVar[PortalMenuItem | None] = None

    #: The logger to use for this view
    logger: ClassVar[structlog.stdlib.BoundLogger]

    @classmethod
    def sidebar(cls) -> Nav:
        return Nav([scls.nav for scls in iter_subclasses(cls) if scls.nav is not None])

    def __init_subclass__(
        cls, /, blueprint: Blueprint | None = None, namespace: str | None = None, portal: Portal | None = None
    ) -> None:
        super().__init_subclass__()

        cls.logger = log.bind(model=cls.name)

        if not hasattr(cls, "permission"):
            cls.permission = cls.name

        if portal is not None:
            cls.register_portal(portal)
            cls.register_blueprint(portal.blueprint, namespace, cls.url, cls.key)

        if blueprint is not None:
            cls.register_blueprint(blueprint, namespace, cls.url, cls.key)

    def dispatch_action(self, action: str, **kwargs: Any) -> IntoResponse:
        method = getattr(self, action, None)
        if method is None or not hasattr(method, "action"):
            self.logger.error(f"Unimplemented method {action!r}", path=request.path)
            abort(400)

        return method(**kwargs)

    @classmethod
    def importer(cls, data: dict[str, Any]) -> list[M]:
        if cls.schema is None:
            raise NotImplementedError("No schema defined")
        items = data[cls.name]
        if isinstance(items, list):
            schema = cls.schema(many=True)
            return schema.load(items)
        schema = cls.schema()
        return [schema.load(items)]

    @classmethod
    def importer_command(cls) -> click.Command:

        logger = cls.logger.bind(command="import")

        @click.command(name=cls.name)
        @click.option("--clear/--no-clear")
        @click.option("--data-key", type=str, help="Key for data in the YAML file")
        @click.argument("filename", type=click.File("r"))
        @with_appcontext
        def import_command(filename: IO[str], clear: bool, data_key: str | None) -> None:
            import yaml

            data = yaml.safe_load(filename)
            if data_key is not None:
                data = data[data_key]

            session = get(Session)

            if clear:
                logger.info(f"Clearing {cls.name}")
                session.execute(delete(cls.model))

            session.add_all(cls.importer(data))
            session.commit()

        import_command.help = f"Import {cls.name} data from a YAML file"
        return import_command

    @classmethod
    def exporter_command(cls) -> click.Command:
        @click.command(name=cls.name)
        @click.argument("filename", type=click.File("w"))
        @with_appcontext
        def export_command(filename: IO[str]) -> None:
            import yaml

            if not cls.schema:
                click.echo(f"No schema defined for {cls.name}", err=True)
                raise click.Abort()

            session = get(Session)

            items = session.scalars(select(cls.model)).all()
            schema = cls.schema(many=True)
            data = schema.dump(items)

            yaml.safe_dump({cls.name: data}, filename)

        export_command.help = f"Export {cls.name} data to a YAML file"
        return export_command

    def dispatch_request(self, **kwargs: Any) -> IntoResponse:
        args = request.args.to_dict()
        for arg in args:
            kwargs.setdefault(arg, args[arg])

        kwargs["action"] = kwargs.pop("action")
        response = self.dispatch_action(**kwargs)
        if request.headers.get("HX-Request"):
            partial = kwargs.get("partial")
            if partial:
                kwargs["action"] = partial
                self.logger.debug("Dispatching for partial", partial=partial)
                return self.dispatch_action(**kwargs)
        return response

    def query(self) -> Iterable[M]:
        session = get(Session)
        return session.execute(select(self.model).order_by(self.model.created)).scalars()

    def single(self, **kwargs: Any) -> M:
        session = get(Session)
        if (single := session.scalars(select(self.model).filter_by(**kwargs)).first()) is None:
            abort(404)
        return single

    def process(self, form: F, obj: M) -> bool:
        session = get(Session)
        form.populate_obj(obj=obj)
        session.add(obj)
        session.commit()
        return True

    def render_form(self, form: F, obj: M) -> IntoResponse:
        self._log_form_errors(form)
        return render_template(
            [f"admin/{self.name}/edit.html", "admin/portal/edit.html"], **{self.name: obj, "form": form}
        )

    def _log_form_errors(self, form: F) -> None:
        if has_app_context():
            if current_app.config["ENV"] not in ("production", "prd"):
                self.logger.error("Errors", errors=form.errors, data=form.data)

    @action()
    def edit(self, **kwargs: Any) -> IntoResponse:
        obj = self.single(**kwargs)
        form = self.form(obj=obj)

        if form.validate_on_submit():
            on_submit.send(self.__class__, **kwargs)
            if self.process(form, obj):
                on_update.send(self.__class__, **kwargs)
                return redirect_next(url_for(".list"))
        return self.render_form(form, obj)

    @action(url="/<key>/preview/")
    def preview(self, **kwargs: Any) -> IntoResponse:
        obj = self.single(**kwargs)
        return render_template(f"admin/{self.name}/preview.html", **{self.name: obj})

    def blank(self, **kwargs: Any) -> M:
        return self.model(**kwargs)

    @action(methods=["GET", "POST", "PUT"])
    def new(self, **kwargs: Any) -> IntoResponse:
        obj = self.blank(**kwargs)
        form = self.form(obj=obj)

        if form.validate_on_submit():
            on_submit.send(self.__class__, **kwargs)
            if self.process(form, obj):
                self.logger.debug("Saved", name=self.name, obj=obj)
                kwargs["name"] = self.name
                on_new.send(self.__class__, **kwargs)
                return redirect_next(url_for(".list"))

        return self.render_form(form, obj)

    @action
    def list(self, **kwargs: Any) -> IntoResponse:
        items = self.query()
        context: dict[str, Any] = {f"{self.name}s": items, "rows": items}
        if self.table is not None:
            context["table"] = self.table()
        return render_template(
            [f"admin/{self.name}/list.html", "admin/portal/list.html"],
            **context,
        )

    @action(permission="edit", methods=["GET", "DELETE"], attachments=True)
    def delete_attachment(self, *, attachment: str, partial: str, **kwargs: Any) -> IntoResponse:
        session = get(Session)
        obj = self.single(**kwargs)
        attachment = session.scalar(select(Attachment).where(Attachment.id == attachment))
        if attachment is not None:
            session.delete(attachment)
            session.commit()
            session.refresh(obj)
        if request.method == "DELETE":
            return "", 204
        form = self.form(obj=obj)
        return render_template(f"{self.attachments}", form=form, **{self.name: obj})

    @action
    def delete(self, **kwargs: Any) -> IntoResponse:
        session = get(Session)
        obj = self.single(**kwargs)

        session.delete(obj)
        session.commit()
        on_delete.send(self.__class__, **kwargs)
        if request.method == "DELETE":
            return "", 204
        return redirect_next(url_for(".list"))

    @classmethod
    def _parent_redirect_to(cls, action: str, **kwargs: Any) -> IntoResponse:
        return redirect_next(url_for(f".{cls.bp.name}.{action}", **kwargs))

    @classmethod
    def register_blueprint(cls, scaffold: Flask | Blueprint, namespace: str | None, url: str, key: str) -> None:
        cls.bp = Blueprint(namespace or cls.name, cls.__module__, url_prefix=f"/{url}/", template_folder="templates/")

        if getattr(cls, "schema", None) is not None:
            cls.importer_group.add_command(cls.importer_command())
            cls.exporter_group.add_command(cls.exporter_command())

        views = {}
        for name in dir(cls):
            if name.startswith("_"):
                continue
            try:
                attr = getattr(cls, name)
                if not callable(attr):
                    continue
                action = getattr(attr, "action", None)
            except Exception:
                cls.logger.exception("Error registering action", name=name)
            else:
                if action is not None:
                    if action.attachments and not cls.attachments:
                        continue

                    views[action.name] = view = require_permission(f"{cls.permission}.{action.permission}")(
                        cls.as_view(action.name)
                    )
                    cls.bp.add_url_rule(
                        action.url.replace("<key>", key),
                        endpoint=action.name,
                        view_func=view,
                        methods=action.methods,
                        defaults={"action": name, **action.defaults},
                    )

        scaffold.register_blueprint(cls.bp)

        # Register two views on the parent scaffold, to provide fallbacks with sensible names.
        scaffold.add_url_rule(
            f"/{url}/",
            endpoint=f"{cls.name}s",
            view_func=cls._parent_redirect_to,
            methods=["GET"],
            defaults={"action": "list"},
        )

        scaffold.add_url_rule(
            f"/{url}/{key}/",
            endpoint=cls.name,
            view_func=cls._parent_redirect_to,
            defaults={"action": "edit"},
            methods=["GET"],
        )

    @classmethod
    def register_portal(cls, portal: "Portal") -> None:
        if cls.nav is not None:
            portal.add(cls.nav)


C = TypeVar("C")


def iter_subclasses(cls: type[C]) -> Iterator[type[C]]:
    subcls: type[C]

    for subcls in cls.__subclasses__():
        yield from iter_subclasses(subcls)
        yield subcls


@AdminView.importer_group.command(name="all")
@click.option("--clear/--no-clear")
@click.argument("filename", type=click.File("r"))
@with_appcontext
def import_all(filename: IO[str], clear: bool) -> None:
    """Import all items known from a YAML file"""
    import yaml

    data = yaml.safe_load(filename)
    session = get(Session)

    for cls in iter_subclasses(AdminView):
        schema = getattr(cls, "schema", None)
        if schema is None:
            continue
        items = data.get(cls.name, None)
        if items is None:
            continue
        cls.logger.info(f"Importing {cls.name}", count=len(items))
        if isinstance(items, list):
            schema = schema(many=True)
            for item in schema.load(items):
                session.add(item)
        else:
            schema = schema()
            session.add(schema.load(items))


@AdminView.exporter_group.command(name="all")
@click.argument("filename", type=click.File("w"))
@with_appcontext
def export_all(filename: IO[str]) -> None:
    """Export all items known to a YAML file"""
    import yaml

    session = get(Session)
    data = {}

    for cls in iter_subclasses(AdminView):
        if cls.schema is None:
            continue

        cls.logger.info(f"Exporting {cls.name}")
        items = session.scalars(select(cls.model)).all()
        schema = cls.schema(many=True)
        data[cls.name] = schema.dump(items)

    yaml.safe_dump(data, filename)


class AdminBlueprint(Blueprint):
    @property
    def jinja_loader(self) -> FileSystemLoader | None:  # type: ignore[override]
        searchpath = []
        if self.template_folder:
            searchpath.append(os.path.join(self.root_path, self.template_folder))

        admin = current_app.blueprints.get("admin")
        if admin is not None:
            admin_template_folder = os.path.join(admin.root_path, admin.template_folder)  # type: ignore[arg-type]
            searchpath.append(admin_template_folder)

        return FileSystemLoader(searchpath)
