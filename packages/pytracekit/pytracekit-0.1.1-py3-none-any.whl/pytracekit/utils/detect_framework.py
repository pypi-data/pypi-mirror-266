from pytracekit.constants.common import FALCON, FASTAPI, FLASK


def detect_framework(app):
    if app is None:
        return FALCON

    # FastAPI detection based on its characteristic method or attribute
    if hasattr(app, "add_api_route") or (hasattr(app, "state") and hasattr(app, "router")):
        return FASTAPI

    # Flask detection based on its characteristic method or attribute
    if hasattr(app, "add_url_rule") or hasattr(app, "route"):
        return FLASK

    # Falcon detection based on its characteristic method or attribute
    if hasattr(app, "add_route") or hasattr(app, "_middleware"):
        return FALCON

    # Default to Falcon if no distinctive features found
    return FALCON
