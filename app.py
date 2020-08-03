import subprocess
import logger
from flask import abort, jsonify, Flask, make_response, request
from PIL import Image

from config import app, server_url
from models import database, Img, Task


@app.route('/')
def index():
    """Если сервер готов к работе, присылает json с ответом"""
    response = jsonify(
        {
            'annotate': 'This small API allows you to change the height and width of images in ".jpg" and "png" '
                        'formats according '
            'to the specified dimensions. ',

            'server_status': 'waiting',
            'NOTE': 'For Windows, use the double quotation mark escaping with two double quotation marks: "" "FILE '
                    'PATH" ""',
            'server_route': [
                'GET-requests',
                '1. {"/"} - this route',
                'example: curl -i http://SERVER URL/',
                '2. {"/image_change_service/api/v1.0/images/< int: id >"} - '
                'retrieving file data by id',
                'example: curl -i http://SERVER URL/image_change_service/api/v1.0/images/1',
                '3. {"/image_change_service/api/v1.0/images/tasks_counter"} - '
                'displaying tasks on the server',
                'example: curl -i http://SERVER URL/image_change_service/api/v1.0/images/tasks_counter',
                '4. {"SERVER_URL/image_change_service/api/v1.0/download_file/<int:task_id>"} - '
                'saving the processed file on the client side',
                'example: start http://SERVER_URL/image_change_service/api/v1.0/download_file/TASK_ID',
                '=============================================',
                'POST-requests',
                '1. {"/image_change_service/api/v1.0/send_file"} - '
                'add file for processing',
                'example: curl -i -F file=@"local path to the file on your device" -F press=OK http://SERVER '
                'URL/image_change_service/api/v1.0/send_file',
                '2. {"/image_change_service/api/v1.0/add_task"} - add task',
                'example: curl -i -H "Content-Type: application/json" -X POST -d " {"""id""": 1, '
                '"""required_height""": height, """required_width""": width}" '
                'http://SERVER_URL//image_change_service/api/v1.0/add_task',
            ]
        }
    )
    logger.LOG.debug(f"Successful connection, response 200, 'User-Agent': {request.headers.get('User-Agent')}")
    return response, 200


@app.route('/image_change_service/api/v1.0/images/<int:id>')
def get_image(id):
    """Отображает информацию о картинке по её id"""
    from checker import check_the_id_passed_in_the_get_request
    response = check_the_id_passed_in_the_get_request(id)
    return response


@app.route('/image_change_service/api/v1.0/images/tasks_counter')
def show_tasks_counter():
    """В ответ на get-запрос, присылает json с количеством задач на сервере"""
    from checker import tasks_counter
    response = tasks_counter()
    return response


@app.route('/image_change_service/api/v1.0/download_file/<int:id>')
def download_file(id):
    """По GET-запросу, сохраняет файл на стороне клиента"""
    from checker import get_output_file
    response = get_output_file(id)
    return response


@app.route('/image_change_service/api/v1.0/send_file', methods=['GET', 'POST'])
def send_file():
    if request.method == 'GET':
        render_template('form.html')
        response = jsonify({'result': 'success'})
        logger.LOG.debug(f"Successful connection, 'User-Agent': {request.headers.get('User-Agent')}")
        return response
    if request.method == 'POST':
        from checker import checking_file
        from saver import saves_the_checked_file_to_database
        sent_file = request.files['file']
        check = checking_file(sent_file)
        logger.LOG.debug(f"checking file: {check}, 'User-Agent': {request.headers.get('User-Agent')}")
        if check == 415:
            response = abort(415)
            return response
        if check == 422:
            response = abort(422)
            return response
        if check == 202:
            response = saves_the_checked_file_to_database(sent_file)
            return response
    response = jsonify({'error': 'method not allowed'})
    logger.LOG.warning(f" {response}{request.method}, 'User-Agent': {request.headers.get('User-Agent')}")
    return response


@app.route('/image_change_service/api/v1.0/add_task', methods=['POST'])
def add_task():
    """В ответ на post-запрос, возвращает информацию о результатах обработки
        переданной задачи"""
    from checker import check_sent_id_in_post_request
    from saver import save_task, change_image
    response = check_sent_id_in_post_request()
    if response[1] == 200:
        response = save_task()
        if response[1] == 201:
            id = response[0]
            response = change_image(id)
    return response


@app.errorhandler(400)
def missing_data(error):
    result = make_response(jsonify({'result': 'error',
                                    'description': 'missing data in the request body'}), 400)
    return result


@app.errorhandler(401)
def empty_string_error(error):
    result = make_response(jsonify({'result': 'error',
                                    'description': 'file name cannot be an empty string'}), 401)
    return result


@app.errorhandler(404)
def unsupported_media_type(error):
    result = make_response(jsonify({'result': 'error', 'description': 'incomprehensible file name'}), 404)
    return result


@app.errorhandler(406)
def unsupported_media_type(error):
    result = make_response(jsonify({'result': 'error', 'description': 'incorrect path'}), 406)
    return result


@app.errorhandler(415)
def unsupported_media_type(error):
    result = make_response(jsonify({'result': 'error',
                                    'description': 'unsupported media type. The server accepts jpg or png extension '
                                                   'files'}), 415)
    return result


@app.errorhandler(422)
def unprocessable_entity_type(error):
    result = make_response(jsonify({'result': 'error',
                                    'description': 'A file of an invalid format was sent under valid extension. '
                                                   'The server accepts jpg or png format files '}), 422)
    return result


if __name__ == '__main__':
    database.create_all()
    app.run(host='localhost', port=85, debug=True)
