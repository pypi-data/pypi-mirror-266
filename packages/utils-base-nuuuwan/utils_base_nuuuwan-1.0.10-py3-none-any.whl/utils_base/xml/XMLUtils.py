from utils_base.ds.String import String
from utils_base.xml._ import _

FONT_FAMILY = 'sans-serif'
DEFAULT_ATTRIB_MAP = {
    'html': {
        'style': 'font-family: %s;' % FONT_FAMILY,
    },
    'svg': {
        'xmlns': 'http://www.w3.org/2000/svg',
    },
}


class XMLUtils:
    @staticmethod
    def render_link_styles(css_file='styles.css'):
        return _('link', None, {'rel': 'stylesheet', 'href': css_file})

    @staticmethod
    def style(**kwargs):
        style_content = ''.join(
            list(
                map(
                    lambda item: '%s:%s;'
                    % (String(str(item[0])).kebab, str(item[1])),
                    kwargs.items(),
                )
            )
        )
        return dict(style=style_content)
