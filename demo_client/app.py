
import requests
from flask import Flask, jsonify
from flask import request
from opentracing_instrumentation.client_hooks import install_all_patches

from loadbalance.consulconfig import AppConfig
from loadbalance.lbrequest import LoadBalanceSession
from loadbalance.registryservice import RegistryService
from opentracer.config import initialize_tracer
from flask_opentracing import FlaskTracer

app = Flask(__name__)
flask_tracer = None


@app.route('/')
def index():
    user_agent = request.headers.get('User-Agent')
    return '<h1>hello world! , Your browers is %s</h1>' % user_agent


@app.route('/user/<name>')
def user(name):
    get_game_detail_url = "http://127.0.0.1:18080/api/getgamedetail?gameid=123"
    requests.get(get_game_detail_url)
    return '<h1>hello, %s!</h1>' % name


@app.route('/api/gameinfo/<gameid>')
def get_game_room(gameid):
    request_url = "http://db-service/db/gameinfo/getgameinfo?gameid={game_id}".format(game_id=gameid)
    request_session = LoadBalanceSession()
    db_service_response = request_session.get(request_url)
    return db_service_response.content


@app.route('/api/health/check')
def health_check():
    status = {'Status': 'UP'}
    return jsonify(status)


if __name__ == '__main__':
    app_config = AppConfig.load_config()
    port = app_config.service_port
    ip_address = app_config.service_ip_address
    registry_service = RegistryService()
    registry_service.registry_service()
    flask_tracer = FlaskTracer(initialize_tracer('./config/appConfig.yaml'), True, app)
    install_all_patches()
    app.run(port=port, host=ip_address, debug=True)


