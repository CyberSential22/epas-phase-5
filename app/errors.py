from flask import render_template

def register_error_handlers(app):
    """
    Registers custom error handlers for the Flask application.
    Prevents stack trace leaks in production.
    """
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500
