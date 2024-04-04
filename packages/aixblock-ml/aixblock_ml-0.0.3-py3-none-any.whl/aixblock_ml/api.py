import logging
import os
from flask import Flask, request, jsonify, send_file
from rq.exceptions import NoSuchJobError
from flask_cors import CORS

from .model import AIxBlockMLManager, AIXBLOCK_ML_BACKEND_V2_DEFAULT
from .exceptions import exception_handler

logger = logging.getLogger(__name__)

_server = Flask(__name__)
_manager = AIxBlockMLManager()


def init_app(model_class, **kwargs):
    global _manager
    _manager.initialize(model_class, **kwargs)
    CORS(_server)
    return _server


@_server.route('/predict', methods=['POST'])
@exception_handler
def _predict():
    data = request.json
    tasks = data.get('tasks')
    project = data.get('project')
    label_config = data.get('label_config')
    force_reload = data.get('force_reload', False)
    try_fetch = data.get('try_fetch', True)
    params = data.get('params') or {}
    predictions, model = _manager.predict(
        tasks, project, label_config, force_reload, try_fetch, **params)
    response = {
        'results': predictions,
        'model_version': model.model_version
    }
    return jsonify(response)


@_server.route('/setup', methods=['POST'])
@exception_handler
def _setup():
    data = request.json
    logger.debug(data)
    project = data.get('project')
    ml_id = data.get('ml_id')
    schema = data.get('schema')
    force_reload = data.get('force_reload', False)
    # host name for uploaded files and building urls
    hostname = data.get('hostname', '')
    # user access token to retrieve data
    access_token = data.get('access_token', '')
    model = _manager.fetch(project,ml_id, schema, force_reload,
                           hostname=hostname, access_token=access_token)
    logger.debug('Fetch model version: {}'.format(model.model_version))
    return jsonify({'model_version': model.model_version})


@_server.route('/train', methods=['POST'])
@exception_handler
def _train():
    logger.warning("=> Warning: API /train is deprecated since Label Studio 1.4.1. "
                   "ML backend used API /train for training previously, "
                   "but since 1.4.1 Label Studio backend and ML backend use /webhook for the training run.")
    data = request.json
    annotations = data.get('annotations', 'No annotations provided')
    project = data.get('project')
    label_config = data.get('label_config')
    params = data.get('params', {})
    if isinstance(project, dict):
        project = ""
    if len(annotations) == 0:
        return jsonify('No annotations found.'), 400
    if 'num_epochs' in params:
        if int(params['num_epochs']) > 100:
            params['num_epochs'] = 20
    if 'batch_size' in params:
        if int(params['batch_size']) > 8:
            params['batch_size'] = 1
    if 'image_width' in params:
        if int(params['image_width']) > 640:
            params['image_width'] = 224
    if 'image_height' in params:
        if int(params['image_height']) > 640:
            params['image_height'] = 224
    job = _manager.train(annotations, project, label_config, **params)
    response = {'job': job.id} if job else {}
    return jsonify(response), 201


@_server.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    event = data.pop('action')
    run = _manager.webhook(event, data)
    return jsonify(run), 201


@_server.route('/is_training', methods=['GET'])
@exception_handler
def _is_training():
    project = request.args.get('project')
    output = _manager.is_training(project)
    return jsonify(output)


@_server.route('/health', methods=['GET'])
@_server.route('/', methods=['GET'])
@exception_handler
def health():
    return jsonify({
        'status': 'UP',
        'model_dir': _manager.model_dir,
        'v2': os.getenv('AIXBLOCK_ML_BACKEND_V2', default=AIXBLOCK_ML_BACKEND_V2_DEFAULT)
    })


@_server.route('/metrics', methods=['GET'])
@exception_handler
def metrics():
    return jsonify({})


@_server.route('/model', methods=['POST'])
@exception_handler
def _model():
    data = request.json
    project = data.get('project')
    label_config = data.get('label_config')
    force_reload = data.get('force_reload', False)
    try_fetch = data.get('try_fetch', True)
    params = data.get('params') or {}
    predictions, model = _manager.model(
        project, label_config, force_reload, try_fetch, **params)
#     response = {
#         'model_build_date': predictions.model_build_date,
#         'model_url': predictions.model_url,
#         'model_map':  predictions.model_url,
#         'model_recall':  predictions.model_url,
#         'model_precision':  predictions.model_url,
#         'model_version': model.model_version
#     }
    return jsonify(predictions)


@_server.route('/toolbar_predict', methods=['POST'])
@exception_handler
def _toolbar_predict():
    data = request.json
    project = data.get('project')
    image = data.get('image')
    clickpoint = data.get('clickpoint')
    polygons = data.get('polygons')
    vertices = data.get('vertices')
    label_config = data.get('label_config')
    force_reload = data.get('force_reload', False)
    try_fetch = data.get('try_fetch', True)
    text = data.get('text')
    question = data.get('question')
    params = data.get('params') or {}
    params['text'] = text
    params['question'] = question
    predictions, model = _manager.toolbar_predict(
        image, clickpoint, polygons, vertices, project, label_config, force_reload, try_fetch, **params)
    response = {
        'results': predictions,
        'model_version': model.model_version
    }
    return jsonify(response)
@_server.route('/toolbar_predict_sam', methods=['POST'])
@exception_handler
def _toolbar_predict_sam():
    data = request.json
    project = data.get('project')
    image = data.get('image')
    clickpoint = data.get('clickpoint')
    polygons = data.get('polygons')
    vertices = data.get('vertices')
    label_config = data.get('label_config')
    force_reload = data.get('force_reload', False)
    try_fetch = data.get('try_fetch', True)
    voice = data.get('voice')
    prompt = data.get('prompt')
    image_pref = data.get('image_pref')
    draw_polygons = data.get('draw_polygons')
    params = data.get('params') or {}
    predictions, model = _manager.toolbar_predict_sam(
        image, clickpoint, polygons, vertices, project, voice,prompt,image_pref,draw_polygons,label_config, force_reload, try_fetch, **params)
    response = {
        'results': predictions,
        'model_version': model.model_version
    }
    return jsonify(response)
@_server.route('/action', methods=['POST'])
@exception_handler
def _action():
    data = request.json
    project = data.get('project')
    command = data.get('command')
    collection = data.get('data')
    label_config = data.get('label_config')
    force_reload = data.get('force_reload', False)
    try_fetch = data.get('try_fetch', True)
    
    params = data.get('params') or {}
    response_collection, model = _manager.action(
        project,command, collection,label_config, force_reload, try_fetch, **params)
    response = {
        'results': response_collection,
        'model_version': model.model_version
    }
    return jsonify(response)
@_server.route('/preview', methods=['GET'])
@exception_handler
def _preview():
    project = request.args.get('project')
    output = _manager.preview(project)
    return output


@_server.route('/download', methods=['GET'])
@exception_handler
def _download():
    import io
    project = request.args.get('project')
    model_path = _manager.download(project)
    return model_path


@_server.errorhandler(NoSuchJobError)
def no_such_job_error_handler(error):
    logger.warning('Got error: ' + str(error))
    return str(error), 410


@_server.errorhandler(FileNotFoundError)
def file_not_found_error_handler(error):
    logger.warning('Got error: ' + str(error))
    return str(error), 404


@_server.errorhandler(AssertionError)
def assertion_error(error):
    logger.error(str(error), exc_info=True)
    return str(error), 500


@_server.errorhandler(IndexError)
def index_error(error):
    logger.error(str(error), exc_info=True)
    return str(error), 500


@_server.before_request
def log_request_info():
    logger.debug('Request headers: %s', request.headers)
    logger.debug('Request body: %s', request.get_data())


@_server.after_request
def log_response_info(response):
    logger.debug('Response status: %s', response.status)
    logger.debug('Response headers: %s', response.headers)
    logger.debug('Response body: %s', response.get_data())
    return response


@_server.after_request
def after_request(r):
    r.direct_passthrough = False
    return r
