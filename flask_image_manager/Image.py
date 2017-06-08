# -*- coding: utf-8 -*-

from PIL import Image as PIL_IMAGE
from cStringIO import StringIO
import os.path
import urllib2

from flask import current_app, render_template_string

hdr = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 '
    '(KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,'
    'application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'}

image_html_template =\
    '''<img src="{{src}}" id="{{kwargs.id}}" class="{{kwargs.class}}"'''\
    ''' onerror="{{ ("this.onerror=null;this.src='" + default + "';") if'''\
    ''' default else ''}}{{ kwargs.onerror }}" alt="{{ kwargs.alt }}"'''\
    ''' width="{{ kwargs.width }}" style="{{kwargs.style}}">'''


def load_file_by_url(url):
    return StringIO(urllib2.urlopen(
        urllib2.Request(url, headers=hdr)).read())


def get_img_pathname(pathname, size=None):
    if size is not None and size in current_app.config['IMAGE_SIZES']:
        pathname += "-" + str(size)
    return pathname + '.' + current_app.config['IMAGE_EXTENSION']


class Image(object):

    def __init__(self, path, **kwargs):
        self.path = path

        self.name = kwargs.get('name')
        self.default_img = kwargs.get('default')

    def __set_name(self, name):
        name = name or self.name
        if not name:
            raise Exception('"name" was not set')
        return name

    def is_present(self, name=None, size=None):
        name = self.__set_name(name)
        return os.path.isfile(self.get_img_abs_path(name, size))

    def get_img_path(self, name=None, size=None):
        name = self.__set_name(name)
        return get_img_pathname(os.path.join(self.path, name), size)

    def get_img_abs_path(self, *args):
        return current_app.config['STATIC_BASEDIR'] + self.get_img_path(*args)

    def save_file(self, file, name=None, sizes=[]):
        name = self.__set_name(name)
        file = PIL_IMAGE.open(file)
        if self.is_present(name):
            self.delete_file(name)
        file.save(self.get_img_abs_path(name))
        for size in sizes:
            width = current_app.config['IMAGE_SIZES'].get(size)
            if not width:
                continue
            resized = file.resize(
                (width, file.size[1] * width / file.size[0]),
                PIL_IMAGE.ANTIALIAS) if width < file.size[0] else file
            resized.save(self.get_img_abs_path(name, size))

    def save_file_by_url(self, url, *args, **kwargs):
        self.save_file(load_file_by_url(url), *args, **kwargs)

    def save_file_by_path(self, path, *args, **kwargs):
        with open(path) as file:
            self.save_file(file, *args, **kwargs)

    def delete_file(self, name=None):
        name = self.__set_name(name)
        try:
            os.remove(self.get_img_abs_path(name))
        except:
            pass
        for size in current_app.config['IMAGE_SIZES'].iterkeys():
            try:
                os.remove(self.get_img_abs_path(name, size))
            except:
                pass

    def __call__(self, name=None, size=None, **kwargs):
        name = self.__set_name(name)
        if size is not None and not self.is_present(name, size):
            size = None
        path = self.get_img_path(name, size)
        return render_template_string(
            image_html_template,
            src=path,
            default=self.default_img,
            kwargs=kwargs)


class FlaskImage(Image):
    """docstring for FlaskImage"""
    present_images = {}

    def __init__(self, image_id, path, name, **kwargs):
        super(FlaskImage, self).__init__(path, name=name, **kwargs)
        self.image_id = image_id
        self.present_images[image_id] = self.__class__


def FlaskModelImage(image_id, path, name_fun, **kwargs):
    class ClosureImage(FlaskImage):
        """docstring for ClosureImage"""

        def __init__(self, name=None):
            super(ClosureImage, self).__init__(image_id, path, name, **kwargs)

    FlaskImage.present_images[image_id] = ClosureImage
    def foo(self):
        try:
            return name_fun(self)
        except:
            return None
    return property(lambda self: ClosureImage(foo(self)))
