from flask import request, current_app, abort, g
from flask_monocrud.flask_debugtoolbar import module
from flask_monocrud.flask_debugtoolbar.panels import DebugPanel
from flask_monocrud.flask_debugtoolbar.utils import format_fname, format_sql
import itsdangerous
from application.providers.BaseConnectionProvider import query_ran, BaseConnectionProvider
import pprint


_ = lambda x: x


def query_signer():
    return itsdangerous.URLSafeSerializer(current_app.config['SECRET_KEY'],
                                          salt='fdt-sql-query')


def is_select(statement):
    prefix = b'select' if isinstance(statement, bytes) else 'select'
    return statement.lower().strip().startswith(prefix)


def dump_query(statement, params):
    if not params or not is_select(statement):
        return None

    try:
        return query_signer().dumps([statement, params])
    except TypeError:
        return None


def load_query(data):
    try:
        statement, params = query_signer().loads(request.args['query'])
    except (itsdangerous.BadSignature, TypeError):
        abort(406)

    # Make sure it is a select statement
    if not is_select(statement):
        abort(406)

    return statement, params


def extension_used():
    return True


def recording_enabled():
    return True


def is_available():
    sqlalchemy_available = False
    return True


def get_queries():
    from app import get_singleton_object
    if get_singleton_object().queries:
        return get_singleton_object().queries
    else:
        return []


class SQLAlchemyDebugPanel(DebugPanel):
    """
    Panel that displays the time a response took in milliseconds.
    """
    name = 'Masonite ORM'

    def log_queries(self, data):
        print(data)
        session = data.get("session")
        request_id = data.get("request_id")
        path = data.get("path")

        self.queries.append(data)
        return self.queries

    query_ran.connect(log_queries)

    @property
    def has_content(self):
        return bool(get_queries()) or not is_available()

    def process_request(self, request):
        pass

    def process_response(self, request, response):
        pass

    def nav_title(self):
        return _('Masonite ORM')

    def nav_subtitle(self):
        count = len(get_queries())

        if not count and not is_available():
            return 'Unavailable'

        return '%d %s' % (count, 'query' if count == 1 else 'queries')

    def title(self):
        return _('Masonite ORM queries')

    def url(self):
        return ''

    def content(self):
        queries = get_queries()

        if not queries and not is_available():
            return self.render('panels/sqlalchemy_error.html', {
                'sqlalchemy_available': False,
                'extension_used': extension_used(),
                'recording_enabled': recording_enabled(),
            })

        data = []
        for query in queries:
            data.append({
                'duration': float(query.get('duration', 0)),
                'sql': format_sql(query.get("statement"), query.get("parameters")),
                'signed_query': dump_query(query.get("statement"), query.get("parameters")),
                'username': query.get("username"),
                'path': query.get("path")
            })
        return self.render('panels/sqlalchemy.html', {'queries': data})


# Panel views


@module.route('/sqlalchemy/sql_select', methods=['GET', 'POST'])
@module.route('/sqlalchemy/sql_explain', methods=['GET', 'POST'],
              defaults=dict(explain=True))
def sql_select(explain=False):
    statement, params = load_query(request.args['query'])
    engine = SQLAlchemy().get_engine(current_app)

    if explain:
        if engine.driver == 'pysqlite':
            statement = 'EXPLAIN QUERY PLAN\n%s' % statement
        else:
            statement = 'EXPLAIN\n%s' % statement
    from masoniteorm.query.QueryBuilder import QueryBuilder
    result = QueryBuilder().explain(statement)
    return g.debug_toolbar.render('panels/sqlalchemy_select.html', {
        'result': result,
        'headers': result[0].keys(),
        'sql': format_sql(statement, params),
        'duration': float(request.args['duration']),
    })
