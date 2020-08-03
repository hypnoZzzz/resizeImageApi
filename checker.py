import json
import os
import logger
from flask import abort, Flask, jsonify, request, Request, send_file, send_from_directory
from jsonschema import validate
from PIL import Image
from config import app


def checking_file(sent_file):
    """Проверяет имя, формат, расширение, целостность файла"""
    logger.LOG.info(f'file transfer attempt: {sent_file.filename}, "User-Agent": {request.headers.get("User-Agent")}')
    ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
    magic_numbers = {'png': bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A]),
                     'jpg': bytes([0xff, 0xd8, 0xff])}
    file_extension = '.' in sent_file.filename and sent_file.filename.rsplit('.', 1)[1]
    if file_extension not in ALLOWED_EXTENSIONS or '.' not in sent_file.filename:
        logger.LOG.info(f'extension: {file_extension}, response 415, "User-Agent": {request.headers.get("User-Agent")}')
        response = 415
        return response
    assert type(sent_file.filename) is str
    # possibly_path_to_save = 'uploads/' + sent_file.filename # for linux-type system
    possibly_path_to_save = os.path.join(app.config['UPLOAD_FOLDER'], sent_file.filename)  # for Windows
    sent_file.save(possibly_path_to_save)
    checked_file = open(possibly_path_to_save, 'rb')
    file_head = checked_file.read()
    if file_head.startswith(magic_numbers['jpg']) not in file_head or \
            file_head.startswith(magic_numbers['png']) not in file_head:
        checked_file.close()
        os.remove(possibly_path_to_save)
        logger.LOG.info(f'unsuccessful file transfer attempt (unsupported format) {sent_file.filename}, response 422, '
                        f'"User-Agent": {request.headers.get("User-Agent")}')
        response = 422
        return response
    checked_file.close()

    verification_image = Image.open(possibly_path_to_save)
    try:
        verification_image.verify()
        checked_file.close()
        logger.LOG.info(f'{sent_file.filename} accepted, response 202, "User-Agent": {request.headers.get("User-Agent")}')
        return 202
    except Exception:
        logger.LOG.info(f'unsuccessful file transfer attempt (the file is damaged) {sent_file.filename}, response 422, "User-Agent": {request.headers.get("User-Agent")}')
        response = 422
        return response


def check_the_id_passed_in_the_get_request(id):
    """Проверяет id, полученное от клиента"""
    logger.LOG.debug(f"sent id: {id}")
    from models import database, Img
    required_id = database.session.query(Img).filter_by(image_id=id).first()
    if required_id is None:
        logger.LOG.info(f'file not found in database, response 404, "User-Agent": {request.headers.get("User-Agent")}')
        response = jsonify({'result': 'error',
                            'description': 'there is no file with this id in the database'})
        return response, 404
    assert type(id) is int
    logger.LOG.info(f'file found, (id: {id}), response 200, "User-Agent": {request.headers.get("User-Agent")}')
    response = jsonify({'result': 'success',
                        'description': 'file found',
                        'filename': required_id.picture_name,
                        'id': required_id.image_id})
    return response, 200


def check_sent_id_in_post_request():
    """Проверяет данные, присланные клиентом в post-запросе"""
    from models import database, Img
    data = {
        'id': request.json['id'],
        'required_height': request.json['required_height'],
        'required_width': request.json['required_width']
    }
    schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "required_height": {"type": "integer"},
            "required_width": {"type": "integer"}
        },
        "required": ["id", "required_height", "required_width"],
        "additionalProperties": False
    }
    maybe_json = validate(data, schema) # эта проверка не срабатывает
    if maybe_json is not None:
        logger.LOG.info(f'wrong json: {request.json}, response 400, "User-Agent": {request.headers.get("User-Agent")}')
        response = abort(400)
        return response, 400
    sent_id = data['id']
    required_image_height = data['required_height']
    required_image_width = data['required_width']
    logger.LOG.info(f"id: {sent_id}, height: {required_image_height}, width: {required_image_width}")
    assert type(sent_id) is int
    assert type(required_image_height) is int
    assert type(required_image_width) is int
    if sent_id <= 0:
        logger.LOG.info(f'id <= 0, response 406, "User-Agent": {request.headers.get("User-Agent")}')
        response = jsonify({'result': 'error',
                            'description': '"id" can only be an integer greater than zero'})
        return response, 406
    if required_image_height < 1 or required_image_height > 9999:
        logger.LOG.info(f'height < 1 or > 9999, response 406, "User-Agent": {request.headers.get("User-Agent")}')
        response = jsonify({'result': 'error',
                            'description': 'the allowable range for height '
                                           'values ​​is from 1 to 9999 inclusive. The height value must be of type '
                                           '"integer"'})
        return response, 406
    if required_image_width < 1 or required_image_width > 9999:
        logger.LOG.info(f'width < 1 or > 9999, response 406, "User-Agent": {request.headers.get("User-Agent")}')
        response = jsonify({'result': 'error',
                            'description': 'the allowable range for width '
                                           'values ​​is from 1 to 9999 inclusive. The width value must be of type '
                                           '"integer"'})
        return response, 406
    response = check_the_id_passed_in_the_get_request(sent_id)
    return response


def tasks_counter():
    """Счётчик количества задач на сервере"""
    from models import database, Task
    completed_tasks = database.session.query(Task).filter_by(is_it_done_now=True).count()
    uncompleted_tasks = database.session.query(Task).filter_by(is_it_done_now=False).count()
    total_tasks = completed_tasks + uncompleted_tasks
    response = jsonify({'total_tasks': total_tasks,
                        'completed_tasks': completed_tasks,
                        'uncompleted_tasks': uncompleted_tasks})
    return response, 200


def get_output_file(id):
    """Проверяет id отформатированного файла и
    создаёт Stream соединение с клиентом для передачи файла"""
    from models import database, Task
    done_file = database.session.query(Task).filter_by(task_id=id).first()
    if done_file is None:
        logger.LOG.info(f'task file not found in database, response 404, "User-Agent": {request.headers.get("User-Agent")}')
        response = jsonify({'result': 'error',
                            'description': 'there is no file with this id in the database'})
        return response, 404
    assert type(id) is int
    filename = f"task_id={done_file.task_id}_{done_file.task_name}.{done_file.file_format}"
    logger.LOG.info(f'task filename: {filename}, "User-Agent": {request.headers.get("User-Agent")}')
    path = 'completed/'+filename  # for linux-type system
    link_to_file = send_file(path, as_attachment=True)
    logger.LOG.info(f'link to file: {link_to_file}, "User-Agent": {request.headers.get("User-Agent")}')
    return link_to_file, 200
