from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from config import app

database = SQLAlchemy(app)


class Img(database.Model):
    image_id = database.Column(database.Integer, primary_key=True)
    picture_name = database.Column(database.String())
    path_to_picture = database.Column(database.Text)
    date = database.Column(database.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return r"{" + '"id": "{}", "name": "{}", "path": "{}", "date": "{}"'.format(self.image_id, self.picture_name,
                                                                                    self.path_to_picture,
                                                                                    self.date) + r"}"


class Task(database.Model):
    task_id = database.Column(database.Integer, primary_key=True)
    task_name = database.Column(database.String())
    file_format = database.Column(database.String())
    required_height = database.Column(database.Integer, default=1)
    required_width = database.Column(database.Integer, default=1)
    is_it_done_now = database.Column(database.Boolean, default=False)
    date = database.Column(database.DateTime, default=datetime.utcnow)
    task_path = database.Column(database.Text)

    def __repr__(self):
        return r"{" + '"id": "{}", "name": "{}", "format": "{}", "height": "{}", ' \
                      '"width": "{}", "date": "{}"'.format(self.task_id, self.task_name, self.file_format,
                                                           self.required_height, self.required_width, self.date) + r"}"
