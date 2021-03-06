# -*- coding: utf-8 -*-

import os.path
import json

from flask import url_for, Markup, flash, abort, request, current_app
from flask_wtf import Form
from wtforms.fields.html5 import URLField
from wtforms import FileField, HiddenField, SubmitField, BooleanField
from wtforms.validators import Optional
from werkzeug.utils import secure_filename

from Image import FlaskImage, load_file_by_url


def allowed_file(filename):
    return 'ALLOWED_EXTENSIONS' not in current_app.config or\
        filename and '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in current_app.config[
            'ALLOWED_EXTENSIONS']


class ImageForm(Form):
    file = FileField('File')
    url = URLField(u'URL to image', validators=[Optional()])
    submit = SubmitField()

    foldername = HiddenField()
    filename = HiddenField()
    sizes = HiddenField()
    file_required = BooleanField(default=False)

    def __init__(self, image, sizes=[], *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

        if isinstance(image, FlaskImage):
            self.image = image
            self.image_id = image.image_id
        else:
            self.image_id = image
            self.image = FlaskImage.present_images.get(image)
            if not self.image:
                abort(404)
            self.image = self.image()

        if not self.foldername.data:
            self.foldername.data = kwargs.get('foldername')
        if not self.filename.data:
            self.filename.data = kwargs.get('filename') or self.image.name
        if not self.sizes.data:
            self.sizes.data = json.dumps(sizes or [])
        if self.file_required.data is False:
            self.file_required.data = bool(kwargs.get('file_required'))

        self.file_path = self.foldername.data\
            if self.foldername.data is not None else ''
        if self.filename.data is None:
            self.filename.data = self.determine_filename()


        self.file_path = os.path.join(self.file_path, self.filename.data)
        self.file_is_loaded = self.image.is_present(self.file_path)


    def determine_filename(self):
        files = os.listdir(self.image.get_img_path(self.file_path))
        max_filename = 0
        for file in map(lambda x: x.rsplit('.', 1)[0], files):
            try:
                int_file = int(file)
                if int_file > max_filename:
                    max_filename = int_file
            except:
                pass
        return str(max_filename + 1)

    def validate(self):
        if not Form.validate(self):
            return False
        sizes = json.loads(self.sizes.data)
        if not self.url.data and not self.file.data:
            print self.file_required.data
            if self.file_required.data:
                if not self.file_is_loaded:
                    flash('No file is provided')
                    return False
                else:
                    return True
            else:
                self.image.delete_file(self.file_path)
                flash('File has been deleted successfully')
                return True

        if self.url.data and allowed_file(self.url.data):
            try:
                self.file.data = load_file_by_url(self.url.data)
                flash('File has been downloaded')
            except:
                flash('Bad URL')
                return False

        if self.file.data and self.url.data or\
                (self.file.data.filename and
                    secure_filename(self.file.data.filename)):
            try:
                self.image.save_file(self.file.data, self.file_path, sizes)
            except IOError:
                os.makedirs(os.path.dirname(self.file_path))
                flash(u'Создана новая папка')
                self.image.save_file(self.file.data, self.file_path, sizes)
            flash('File has been saved successfully')
        else:
            flash('File extension is not allowed')
            return False
        return True

    def __call__(self, submit="Change photo", **kwargs):
        no_form = kwargs.get('no_form') if hasattr(kwargs, 'no_form') else type(self) != ImageForm
        s = '%s' % (
            self.hidden_tag() + self.file(**kwargs) +
            self.url(**kwargs) + self.foldername() +
            self.filename() + self.sizes() +
            self.file_required(style="display:none;") +
            (self.submit(value=submit, **kwargs) if not no_form else '')) +\
            (u'<font color="red">File is present on a server</font>'
                if self.file_is_loaded else '')
        if no_form:
            return Markup(s)
        return Markup(u'<form action="%s" method="post"'
                      u'enctype="multipart/form-data">%s</form>' % (
                          url_for('imagemanager.load_image',
                                  image_id=self.image_id,
                                  next=kwargs.get('next') or request.path),
                          s))
