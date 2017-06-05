# -*- coding: utf-8 -*-

from flask import Blueprint, redirect, request

from ImageForm import ImageForm
from Image import Image, FlaskImage, FlaskModelImage


def load_img(image_id):
    ImageForm(image_id).validate()
    return redirect(request.args.get('next', '/'))


class ImageManager(object):

    def __init__(self, app=None, **kwargs):
        if app:
            self.init_app(app)

    def init_app(self, app):

        if 'IMAGE_EXTENSION' not in app.config:
            raise Exception(
                'IMAGE_EXTENSION must be set in application configuration')

        if 'BASEDIR' not in app.config:
            raise Exception(
                'BASEDIR must be set in application configuration')

        if 'IMAGE_SIZES' not in app.config:
            app.config['IMAGE_SIZES'] = {
                'lg': 800,
                'md': 500,
                'sm': 300,
            }
        if 'ALLOWED_EXTENSIONS' in app.config:
            app.config['ALLOWED_EXTENSIONS'] = map(
                str.lower, app.config['ALLOWED_EXTENSIONS'])

        module = Blueprint("imagemanager", __name__)
        module.add_url_rule('/load_image/<image_id>',
                            'load_image', load_img, methods=['POST'])
        app.register_blueprint(module, url_prefix=app.config.get(
            'IMAGE_URL') or '/imagemanager')
