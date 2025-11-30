# AddiPi Files Service
from flask import Flask
from flask_cors import CORS
from config.config import init_config
from routes.files_bp import files_bp
from routes.health_bp import health_bp


app = Flask(__name__)

long_origin = (
    "http://addipi-files."
    "b3aaefdfe9dzdea0.swedencentral.azurecontainer.io:5000"
)

CORS(app)

init_config(app)


app.register_blueprint(files_bp, url_prefix='/files')

app.register_blueprint(health_bp)


if __name__ == "__main__":
    print("AddiPi Files Service starting...")
    app.run(host='0.0.0.0', port=app.config['PORT'], debug=True)
