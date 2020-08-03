import json
import os
import logger
from flask import Flask, jsonify, request
from PIL import Image
from werkzeug.utils import secure_filename

from config import app
from models import database, Img, Task


def saves_the_checked_file_to_database(sent_file):
    """Сохраняет проверенный файл в базу данных,
    парсит данные в json,
    дополнительно выполняя проверку имени файла,
    присваивает файлу уникальное имя и
    возвращает ответ в json формате"""

    sent_filename = sent_file.filename
    path_to_picture = os.path.join(app.config['UPLOAD_FOLDER'], sent_filename)
    picture_name = secure_filename(str(sent_filename))
    file_data = Img(picture_name=picture_name, path_to_picture=path_to_picture)
    try:
        database.session.add(file_data)
        database.session.commit()
        image_database = Img.query.order_by(Img.date).all()
        with open('parse database/image_database.json', 'w') as image_base_to_json:
            json.dump(str(image_database), image_base_to_json, indent=-2, ensure_ascii=False)
        response = jsonify({'result': 'success',
                            'filename': sent_filename,
                            'id': file_data.image_id,
                            'description': 'the file is saved and ready for processing'})
        return response, 202
    except Exception:
        response = jsonify({'result': 'error', 'description': 'error adding to database'})
        return response, 499


def save_task():
    """Сохраняет задачу клиента в базу данных и парсит её в json"""
    sent_json = {
        'id': request.json['id'],
        'required_height': request.json['required_height'],
        'required_width': request.json['required_width']
    }
    sent_id = sent_json['id']
    try:
        processed_file = Img.query.get(sent_id)
        task_name = processed_file.picture_name.rsplit('.', 1)[0]
        file_format = processed_file.picture_name.rsplit('.', 1)[1]
        required_image_height = sent_json['required_height']
        required_image_width = sent_json['required_width']
        task_path = processed_file.path_to_picture
        task = Task(task_name=task_name, file_format=file_format, required_height=required_image_height,
                    required_width=required_image_width, task_path=task_path)
        database.session.add(task)
        database.session.commit()
        task_database = Task.query.order_by(Task.date).all()
        with open('parse database/tasks_database.json', 'w') as tasks_base_to_json:
            json.dump(str(task_database), tasks_base_to_json, indent=-2, ensure_ascii=False)
        return task.task_id, 201
    except ExceptionWhenAddingTaskToDatabase:
        response = jsonify({'result': 'error', 'description': 'when adding a task to the database, an unknown error '
                                                              'occurred (the connection to the server may have been '
                                                              'broken)'})
        return response, 499


def change_image(id):
    """Изменяет изображение, согласно полученной задачи и сохраняет его на сервере"""
    from models import database, Task
    tasks_data = database.session.query(Task).filter_by(task_id=id).first()
    path_to_save_done_task = os.path.join(app.config['COMPLETED_FOLDER'])
    task_path = tasks_data.task_path
    processed_image = Image.open(task_path)
    image_height = tasks_data.required_height
    image_width = tasks_data.required_width
    resize_img = processed_image.resize((image_height, image_width), Image.ANTIALIAS)
    processed_img_name = f"task_id={tasks_data.task_id}_{tasks_data.task_name}." \
                         f"{tasks_data.file_format}"
    file_path = os.path.join(path_to_save_done_task, processed_img_name)
    resize_img.save(file_path)
    tasks_data.is_it_done_now = True
    database.session.add(tasks_data)
    database.session.commit()
    processed_image.close()
    response = jsonify({'result': 'success',
                        'file_name': processed_img_name,
                        'id': tasks_data.task_id,
                        'done': tasks_data.is_it_done_now})
    logger.LOG.info(f'change image name: {processed_img_name}, path: {file_path} response 200, "User-Agent": {request.headers.get("User-Agent")}')
    return response, 200
