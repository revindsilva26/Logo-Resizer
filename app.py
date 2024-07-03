from flask import Flask, request, send_file, render_template_string
from PIL import Image, ImageOps
import requests
from io import BytesIO
import cairosvg

app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Logo Resizer</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background-color: #f4f4f4;
            margin: 0;
        }
        .container {
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            width: 100%;
            max-width: 400px;
            text-align: center;
        }
        h1 {
            font-size: 24px;
            margin-bottom: 20px;
            color: #333;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: #555;
        }
        input[type="text"] {
            width: calc(100% - 20px);
            padding: 10px;
            margin-bottom: 20px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        button {
            background-color: #007BFF;
            color: #fff;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background-color: #0056b3;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Logo Resizer</h1>
        <form method="post" action="/process">
            <label for="url">Image URL:</label>
            <input type="text" id="url" name="url" placeholder="Enter image URL here">
            <button type="submit">Resize</button>
        </form>
    </div>
</body>
</html>
''')


@app.route('/process', methods=['POST'])
def process():
    image_url = request.form['url']
    response = requests.get(image_url)
    content = response.content

    if image_url.endswith(".svg"):
        content = cairosvg.svg2png(bytestring=content)
    
    img = Image.open(BytesIO(content)).convert("RGBA")
    img_old = add_white_background(img)

    img_new = expand2square(img_old, (255 , 255, 255)).resize((300, 300))

    img_io = BytesIO()
    img_new.save(img_io, 'JPEG')
    img_io.seek(0)

    return send_file(img_io, mimetype='image/jpeg', as_attachment=True, download_name='padded_image.jpg')

def add_white_background(img):
    white_bg = Image.new("RGBA", img.size,(255, 255, 255, 255))
    white_bg.paste(img, (0,0), img)
    final_image = white_bg.convert("RGB")
    return final_image


def expand2square(pil_img, background_color):
    width, height = pil_img.size
    if width == height:
        return pil_img
    elif width > height:
        result = Image.new(pil_img.mode, (width, width), background_color)
        result.paste(pil_img, (0, (width - height) // 2))
        return result
    else:
        result = Image.new(pil_img.mode, (height, height), background_color)
        result.paste(pil_img, ((height - width) // 2, 0))
        return result

if __name__ == '__main__':
    app.run(debug=True)
