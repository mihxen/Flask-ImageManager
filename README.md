# Flask-ImageManager
Easy way to manage your images in Flask application.

### Requires
- Jinja
- Flask
- Flask-WTF
- Definition of a "IMAGE_EXTENSION" variable in a configuration file (for example to 'png')
- Definition of a "BASEDIR" variable in a configuration file which contains a path to the folder with static files

### Other configuration variables
- "IMAGE_SIZES" is a python dictionary of available image labels and widths {'lg': 800,}
- "ALLOWED_EXTENSIONS" is a list of extensions which are allowed to be saved to a server
- "IMAGE_URL" is a URL of route for image manipulations ("<IMAGE_URL>/load_image/<image_id>"). By default "IMAGE_URL" = "/imagemanager"

### How it works

Flask-ImageManager provides some classes and a route for image manipulation.
### Installation

```bash
git clone https://github.com/mihxen/Flask-ImageManager
cd Flask-ImageManager
python setup.py install
```

#### Registering

```python
from flask import Flask
from flask_image_manager import ImageManager

app = Flask(__name__)

# set config variables
app.config['IMAGE_EXTENSION'] = "jpg"
app.config['BASEDIR'] = "path/to/static/folder"

# Initialize the extension
ImageManager(app)

```
### Simple usage

```python
from flask_image_manager import Image
from flask import render_template_string

image = Image('/static/img', 'test', default='/static/img/no-photo.png')
image.save_file_by_url('url', sizes=['lg', 'sm'])
render_template_string('{{ image(size='sm') }}', image=image)
# call method also supports 'class', 'style', ... optional parameters

```

In template

```html
<img src="/static/img/test-sm.jpg" class="" onerror="this.onerror=null;this.src='/static/img/no-photo.png';">
```

### Usage with SQLAlchemy


```python
from flask_image_manager import FlaskModelImage
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Product(db.Model):
    __tablename__ = 'product'

    id = db.Column(db.Integer, primary_key=True)
    image = FlaskModelImage(
        image_id='product_img',
        path='static/img/products',  
        name_fun=lambda x: 'product_%d' % x.id,
        default="static/nophoto.jpg")
```

##### `FlaskModelImage()` Parameters:

- **image_id**: This parameter is necessary for Form updates.
- **path**: Path to folder where images are contained.
- **name_fun**: Function which constructs the name of an image from product id.
- **default**: Optional parameter.

### Form updates

```python
from flask import render_template_string
from flask_image_manager import ImageForm

product = Product.query.get_or_404(4)
img_form = ImageForm(product.image,
                     sizes=app.config['IMAGE_SIZES'])
render_template_string('{{ image_form() }}',
                        img_form=image_form)
```

**img_form** will be rendered on a HTML page and the image for class can be set in all provided **sizes** 
