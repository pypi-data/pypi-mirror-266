from jinja2 import Environment, FileSystemLoader, select_autoescape

jinja__environment = Environment(
    loader=FileSystemLoader(""), autoescape=select_autoescape()
)


def render_template(template_path, context):
    """
    Get the template from the filesystem, and fill it in.
    Returns a string
    """
    template = jinja__environment.get_template(template_path)
    return template.render(context)
