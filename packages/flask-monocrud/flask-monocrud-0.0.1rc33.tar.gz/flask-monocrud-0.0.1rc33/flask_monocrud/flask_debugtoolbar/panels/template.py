import collections
import json
import pprint
import sys
import uuid

from flask import (
    template_rendered, request, g,
    Response, current_app, abort, url_for
)
from flask_monocrud.flask_debugtoolbar import module
from flask_monocrud.flask_debugtoolbar.panels import DebugPanel
from flask_orphus import orequest
_ = lambda x: x


class TemplateDebugPanel(DebugPanel):
    """
    Panel that displays the time a response took in milliseconds.
    """
    name = 'Template'
    has_content = True

    # save the context for the 5 most recent requests
    template_cache = collections.deque(maxlen=5)

    @classmethod
    def get_cache_for_key(self, key):
        for cache_key, value in self.template_cache:
            if key == cache_key:
                return value
        raise KeyError(key)

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.key = str(uuid.uuid4())
        self.templates = []
        template_rendered.connect(self._store_template_info)

    def _store_template_info(self, sender, **kwargs):
        # only record in the cache if the editor is enabled and there is
        # actually a template for this request
        if not self.templates and is_editor_enabled():
            self.template_cache.append((self.key, self.templates))
        if kwargs.get("template").__dict__.get("name"):
            self.templates.append(kwargs)
        else:
            template_partial = kwargs.get("template").__dict__.get("globals").get("_render")
            template_name = template_partial.args[0]
            kwargs['template'].name = str(template_name).lstrip("<Flask '").rstrip("'>")
            self.templates.append(kwargs)

    def process_request(self, request):
        pass

    def process_response(self, request, response):
        pass

    def nav_title(self):
        return _('Templates')

    def nav_subtitle(self):
        return "%d rendered" % len(self.templates)

    def title(self):
        return _('Templates')

    def url(self):
        return ''

    def content(self):
        return self.render('panels/template.html', {
            'key': self.key,
            'templates': self.templates,
            'editable': is_editor_enabled(),
        })


def is_editor_enabled():
    return current_app.config.get('DEBUG_TB_TEMPLATE_EDITOR_ENABLED')


def require_enabled():
    if not is_editor_enabled():
        abort(403)


def _get_source(template):
    with open(template.filename, 'rb') as fp:
        source = fp.read()
    return source.decode(_template_encoding())


def _template_encoding():
    return getattr(current_app.jinja_loader, 'encoding', 'utf-8')


@module.route('/template/<key>')
def template_editor(key):
    require_enabled()
    # TODO set up special loader that caches templates it loads
    # and can override template contents
    templates = [t['template'] for t in
                 TemplateDebugPanel.get_cache_for_key(key)]
    templates_new = []
    for template in templates:
        if template.name == orequest.name:
            templates_new.append({
                "name": template.name,
                "source": _get_source(template)
            })
    return g.debug_toolbar.render('panels/template_editor.html', {
        'static_path': url_for('_debug_toolbar.static', filename=''),
        'request': request,
        'key': key,
        'templates': templates_new,
    })


@module.route('/template/<key>/save', methods=['POST'])
def save_template(key):
    require_enabled()
    templates_new = {}
    for template in TemplateDebugPanel.get_cache_for_key(key):
        if template.get('template').name == orequest.name:
            templates_new.update({
                "name": template.get('template').name,
                "source": _get_source(template.get('template')),
                "context": template.get('context'),
                "template": template
            })
    template = templates_new['template']
    content = orequest.content.encode(_template_encoding())
    with open(template.get('template').filename, 'wb') as fp:
        fp.write(content)
    return 'ok'


@module.route('/template/<key>', methods=['POST'])
def template_preview(key):
    require_enabled()
    templates_new = {}
    for template in TemplateDebugPanel.get_cache_for_key(key):
        if template.get('template').name == orequest.name:
            templates_new.update({
                "name": template.get('template').name,
                "source": _get_source(template.get('template')),
                "context": template.get('context'),
            })
    context = templates_new['context']

    content = orequest.content
    env = current_app.jinja_env.overlay(autoescape=True)
    try:
        template = env.from_string(content)
        return template.render(context)
    except Exception as e:
        tb = sys.exc_info()[2]
        try:
            while tb.tb_next:
                tb = tb.tb_next
            msg = {'lineno': tb.tb_lineno, 'error': str(e)}
            return Response(json.dumps(msg), status=400,
                            mimetype='application/json')
        finally:
            del tb
