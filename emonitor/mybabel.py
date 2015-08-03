import os
from flask import _request_ctx_stack
from flask.ext.babel import Babel, get_locale, format_datetime
from babel import support


def myget_translations():
    """Returns the correct gettext translations that should be used for
    this request.  This will never fail and return a dummy translation
    object if used outside of the request or if a translation cannot be
    found.
    """
    ctx = _request_ctx_stack.top
    if ctx is None:
        return None
    translations = getattr(ctx, 'babel_translations', None)
    dirname = os.path.join(ctx.app.root_path, ctx.app.config.get('LANGUAGE_DIR'))  # base translations
    files = []

    if os.path.exists(dirname):
        try:
            for mo in [f[:-3] for f in os.listdir(os.path.join(dirname, str(get_locale()) + '/LC_MESSAGES')) if f.endswith('.mo')]:
                files.append(support.Translations.load(dirname, [get_locale()], domain=mo))
        except:
            pass

    # load translations of blueprints
    for bp_name in ctx.app.blueprints:
        dirname = os.path.join(ctx.app.blueprints[bp_name].root_path, 'translations')
        if not os.path.exists(dirname):
            continue
        files.append(support.Translations.load(dirname, [get_locale()], domain=bp_name))

    for f in files:
        if not translations:
            translations = f
        else:
            try:
                if f.files[0] not in translations.files:
                    translations.files.extend(f.files)
                    translations._catalog.update(f._catalog)
            except:
                pass

    ctx.babel_translations = translations
    return translations


class MyBabel(Babel):

    def init_app(self, app):
        super(MyBabel, self).init_app(app)
        app.jinja_env.install_gettext_callables(
            lambda x: myget_translations().ugettext(x),
            lambda s, p, n: myget_translations().ungettext(s, p, n),
            newstyle=True
        )
        app.jinja_env.filters['datetime'] = format_datetime

    @staticmethod
    def gettext(string, **variables):
        t = myget_translations()
        if t is None:
            return string % variables
        return t.ugettext(string) % variables
