from flask import Flask, render_template, request, redirect, url_for, g,abort
from PIL import Image
import os
from werkzeug.utils import secure_filename
import numpy as np
from forms import MyForm,ChoiceForm
import matplotlib.pyplot as plt
import tkinter as tk

app = Flask(__name__, static_folder='static')
app.config['UPLOAD_FOLDER'] = 'upload'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LfG3V4mAAAAAG3PPRa70tHKfwoOrwRyU2HqCFf4'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LfG3V4mAAAAAKevCkHyhxKmY4mPucBwHO4DMMc_'
app.config['RECAPTCHA_OPTIONS'] = {'theme': 'white'}

@app.route('/protected')
def protected():
    # Проверяем, решена ли reCAPTCHA
    if request.args.get('captcha') == 'solved':
        return redirect(url_for('image', captcha='solved'))
    if request.args.get('captcha') == 'unsolved':
        return "Captcha not succed"
    return abort(403)

@app.route('/', methods=['GET', 'POST'])
def submit():
    form = MyForm()
    if form.validate_on_submit():
        return redirect(url_for('protected', captcha='solved'))

    return render_template('index.html', form=form)

@app.route('/image', methods=['GET'])
def image():
    form = ChoiceForm()
    return render_template('upload-image.html',form=form)

@app.route('/image/upload', methods=['GET','POST'])
def upload():
    # Получаем загруженный файл из формы
    file1 = request.files['image1']
    file2 = request.files['image2']
    form = ChoiceForm()
    # Проверяем, что файл существует и имеет разрешенное расширение
    if file1 and file2 and allowed_file(file1.filename) and allowed_file(file2.filename):
        glue_direction = form.glue_direction.data
        # Сохраняем файл на сервере
        filename1 = secure_filename(file1.filename)
        filename2 = secure_filename(file2.filename)
        file1.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))
        # Выполняем необходимые операции с изображением
        image1_path = os.path.join(app.config['UPLOAD_FOLDER'], filename1)

        file2.save(os.path.join(app.config['UPLOAD_FOLDER'], filename2))
        # Выполняем необходимые операции с изображением
        image2_path = os.path.join(app.config['UPLOAD_FOLDER'], filename2)

        #Получаем имя для графика и рисуем его
        graname = filename1.split('.')[0] + "_graph.png"
        print(graname)
        plot_color_distribution(image1_path, graname)

        image_changed_path = "static/changed"
        # Обработка изображения
        if glue_direction == 'hr':
            # Меняем местами левую и правую часть изображения
            glue_hr_and_save(image1_path,image2_path,filename1,image_changed_path)
            filename1 = "horizontal_" + filename1

        elif glue_direction == 'vr':
            # Меняем местами верхнюю и нижнюю часть изображения
            glue_vr_and_save(image1_path,image2_path,filename1,image_changed_path)
            filename1 = "vertical_" + filename1


        return render_template("changed_image.html",filename = filename1, graph_name = graname)
    else:
        return 'Недопустимый файл'


def allowed_file(filename):
    # Проверяем разрешенные расширения файлов
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def glue_hr_and_save(image1_path,image2_path,file_name,image_folder):
    # Открываем изображение с помощью Pillow
    image1 = Image.open(image1_path)
    image2 = Image.open(image2_path)

    width1, height1 = image1.size
    width2, height2 = image2.size

    new_image = Image.new('RGB', (width1 + width2, max(height1, height2)))
    new_image.paste(image1, (0, 0))
    new_image.paste(image2, (width1, 0))

    new_image.save(f"{image_folder}/horizontal_{file_name}")
def glue_vr_and_save(image1_path,image2_path,file_name,image_folder):
    # Открываем изображение с помощью Pillow
    image1 = Image.open(image1_path)
    image2 = Image.open(image2_path)

    width1, height1 = image1.size
    width2, height2 = image2.size

    new_image = Image.new('RGB', (max(width1, width2), height1 + height2))
    new_image.paste(image1, (0, 0))
    new_image.paste(image2, (0, height1))

    new_image.save(f"{image_folder}/vertical_{file_name}")
def plot_color_distribution(image_path,name):
    # Загрузка изображения с помощью Pillow
    image = Image.open(image_path)

    # Преобразование изображения в массив NumPy
    image_array = np.array(image)

    # Получение гистограммы распределения цветов по каналам
    red_hist = np.histogram(image_array[:, :, 0], bins=256, range=(0, 256))
    green_hist = np.histogram(image_array[:, :, 1], bins=256, range=(0, 256))
    blue_hist = np.histogram(image_array[:, :, 2], bins=256, range=(0, 256))

    # Рисование графика распределения цветов
    plt.figure(figsize=(10, 6))
    plt.title('Color Distribution')
    plt.xlabel('Color Intensity')
    plt.ylabel('Frequency')
    plt.xlim(0, 255)
    plt.plot(red_hist[1][:-1], red_hist[0], color='red', label='Red')
    plt.plot(green_hist[1][:-1], green_hist[0], color='green', label='Green')
    plt.plot(blue_hist[1][:-1], blue_hist[0], color='blue', label='Blue')
    plt.legend()

    plt.savefig(f"static/graph/{name}", dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == '__main__':
    app.run()