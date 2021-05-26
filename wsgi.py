"""
WSGI config for project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

from app.app_factory import create_app
from app.settings import EnvConfiguration

application = create_app(EnvConfiguration)
application.run(host="0.0.0.0", port=8089, debug=True)
