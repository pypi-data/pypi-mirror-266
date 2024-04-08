from gskChat.errors import MissingRequirementsError
import requests
from flask import send_from_directory
from flask import Flask
def serve_video(bg):
    return send_from_directory('bg.mp4', bg, mimetype='video/mp4')

def run_gui(host: str = '0.0.0.0', port: int = 8080, debug: bool = False) -> None:
    
    from gskChat.cookies import set_cookies
    set_cookies(".pi.ai", {
    "__cf_bm": "xl24W1jFDqUOA2pgru9qd2ELX0KcravVqZPnxTxBhi4-1710933366-1.0.1.1-i.GvNWyw5XE6z02JZ2NfbslFhtKbB8EQBVldzZWOvUlzY0o5lLxungD.7FPt0BfBn9_sxkUKbZr_xoxQMoRamg"
    })
    
    try:
        from .server.app     import app
        from .server.website import Website
        from .server.backend import Backend_Api
    except ImportError:
        raise MissingRequirementsError('Install "flask" package for the gui')

    if debug:
        import gskChat
        gskChat.debug.logging = True
    config = {
        'host' : host,
        'port' : port,
        'debug': debug
    }
    
    site = Website(app)
    for route in site.routes:
        app.add_url_rule(
            route,
            view_func = site.routes[route]['function'],
            methods   = site.routes[route]['methods'],
        )
    
    backend_api  = Backend_Api(app)
    for route in backend_api.routes:
        app.add_url_rule(
            route,
            view_func = backend_api.routes[route]['function'],
            methods   = backend_api.routes[route]['methods'],
        )
    
    print(f"Running on port {config['port']}")
    app.run(**config)
    print(f"Closing port {config['port']}")
