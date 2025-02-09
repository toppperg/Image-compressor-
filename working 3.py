from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from PIL import Image
from flask import send_file
import os
import webbrowser

app = Flask(__name__, template_folder='D:/Image-resizer-dont-delete-akhil/Image-Size-Compressor-main/templates', static_folder='D:/Image-resizer-dont-delete-akhil/Image-Size-Compressor-main/static')

# Set the base directory
BASE_DIR = 'D:/Image-resizer-dont-delete-akhil/Image-Size-Compressor-main'

# Set the upload folder and allowed extensions
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'uploads')
app.config['COMPRESSED_FOLDER'] = os.path.join(BASE_DIR, 'static/compressed')
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png', 'gif'}

def allowed_file(filename):
    # Check if the file extension is allowed
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def compress_image(input_path, output_path, desired_size, desired_byte_format, photo_option):
    # Open the input image
    with Image.open(input_path) as img:
        # Calculate the initial size of the image
        size = os.path.getsize(input_path)
        # Convert the desired size to bytes
        if desired_byte_format == 'KB':
            desired_size = int(desired_size.replace("KB", "")) * 1024
        elif desired_byte_format == 'MB':
            desired_size = int(desired_size.replace("MB", "")) * 1024 * 1024
        elif desired_byte_format == 'GB':
            desired_size = int(desired_size.replace("GB", "")) * 1024 * 1024 * 1024
        else:
            raise ValueError("Invalid size format! Use KB, MB, or GB.")
        
        # If the image size is already smaller than the desired size, return the input image
        if size < desired_size:
            return img
        
        # Apply photo option if selected
        if photo_option:
            width, height = img.size
            img = img.resize((200, 250))
        
        # Initialize the quality parameter
        quality = 100
        
        # Compress the image until the desired size is reached
        while size > desired_size:
            if quality <= 0:
                break
            img.convert("RGB").save(output_path, "JPEG", quality=quality)
            size = os.path.getsize(output_path)
            quality -= 5
        
        # Return the compressed image
        return img

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        print("1 clear")
        file = request.files['file']
        
        # If the user does not select a file, submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        # Check if the file is allowed
        if file and allowed_file(file.filename):
            # Save the uploaded file to the uploads folder
            filename = secure_filename(file.filename)
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(input_path)
            print("2")
            # Compress the image and save it to the uploads folder with a "_compressed" suffix
            output_path = os.path.join(app.config['COMPRESSED_FOLDER'], os.path.splitext(filename)[0] + "_compressed.jpg")
            desired_size = request.form['size']
            desired_byte_format = request.form['option']
            photo_option = 'photo-option' in request.form  # Check if photo option is selected
            compress_image(input_path, output_path, desired_size, desired_byte_format, photo_option)
            
            # Return the download link for the compressed image
            return render_template('result.html', filename=os.path.basename(output_path))
            
    return render_template('index.html')

@app.route('/static/compressed/<filename>')
def download(filename):
    # Return the download link for the compressed image
    path = os.path.join(app.config['COMPRESSED_FOLDER'], filename)
    return send_file(path, as_attachment=True)

if __name__ == '__main__':
    # Open the browser automatically
    webbrowser.open('http://localhost:5000')
    app.run(debug=True)
