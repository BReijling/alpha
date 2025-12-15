from sqlalchemy.schema import DDLElement
from sqlalchemy import MetaData, event, inspect, table
from sqlalchemy.ext import compiler


class CreateView(DDLElement):
    def __init__(self, name, selectable):
        self.name = name
        self.selectable = selectable


class DropView(DDLElement):
    def __init__(self, name):
        self.name = name


@compiler.compiles(CreateView)
def _create_view(element, compiler, **kw):
    return "CREATE OR REPLACE VIEW %s AS %s" % (
        element.name,
        compiler.sql_compiler.process(element.selectable, literal_binds=True),
    )


@compiler.compiles(DropView)
def _drop_view(element, compiler, **kw):
    return "DROP VIEW %s" % (element.name)


class View:
    def __init__(self, name: str, metadata: MetaData, selectable):
        t = table(name)

        t._columns._populate_separate_keys(
            col._make_proxy(t) for col in selectable.selected_columns
        )

        event.listen(metadata, "after_create", CreateView(name, selectable))
        event.listen(
            metadata, "before_drop", DropView(name).execute_if(callable_=self.view_exists)  # type: ignore
        )
        return t

    def view_exists(self, ddl, target, connection, **kw):
        return ddl.name in inspect(connection).get_view_names()

    def view_doesnt_exist(self, ddl, target, connection, **kw):
        return not self.view_exists(ddl, target, connection, **kw)
