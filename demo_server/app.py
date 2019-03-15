from flask import Flask, request, jsonify
from flask_opentracing import FlaskTracer
from opentracing_instrumentation.client_hooks import install_all_patches

from loadbalance.consulconfig import AppConfig
from loadbalance.registryservice import RegistryService
from opentracer.config import initialize_tracer

app = Flask(__name__)
flask_tracer = None


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route("/db/gameinfo/getgameinfo")
def get_game_info():
    game_id = request.args.get('gameId')
    game_list = []
    game_list.append("test-game-0")
    game_list.append("test-game-1")
    game_list.append("test-game-2")
    game_list.append("test-game-3")
    game_list.append("test-game-4")
    game_list.append("test-game-5")
    hash_code_game_id = hash(game_id)
    list_count = len(game_list)
    index = hash_code_game_id % list_count
    result = {"gameId": game_id, "gameName": game_list[index]}
    return jsonify(result)


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
