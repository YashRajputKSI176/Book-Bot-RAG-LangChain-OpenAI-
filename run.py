from app.app_init import app
from app.api.routes import api_routes

app.register_blueprint(api_routes)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3017, debug=True)