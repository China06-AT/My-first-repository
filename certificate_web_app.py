from flask import Flask, render_template, request, jsonify, send_file
import os
import json
from pathlib import Path
from datetime import datetime, timedelta
import tempfile
import shutil

# Импортируем генератор сертификатов
from image_certificate_generator import ImageCertificateGenerator

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['GENERATED_FOLDER'] = 'static/generated'

# Создаем папки, если они не существуют
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['GENERATED_FOLDER'], exist_ok=True)

# Инициализируем генератор сертификатов
generator = ImageCertificateGenerator()

# Получаем координаты по умолчанию
default_coordinates = generator.COORDINATES

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_certificate', methods=['POST'])
def generate_certificate():
    try:
        # Получаем данные из запроса
        data = request.json
        
        # Извлекаем основные данные
        cert_type = data.get('cert_type', 'Безопасность и Охрана труда')
        fullname = data.get('fullname', '')
        workplace = data.get('workplace', '')
        job_title = data.get('job_title', '')
        with_grid = data.get('with_grid', True)
        grid_density = data.get('grid_density', 20)
        coordinates = data.get('coordinates', default_coordinates)
        
        # Обновляем координаты в генераторе
        generator.COORDINATES = coordinates
        
        # Подготавливаем даты
        now = datetime.now()
        next_year = now + timedelta(days=365)
        
        # Собираем данные для генерации
        cert_data = {
            'position': cert_type,
            'fullname': fullname,
            'workplace': workplace,
            'job_title': job_title,
            'qualification_group': '' if cert_type == 'Безопасность и Охрана труда' else '3',
            'cert_date': now,
            'next_date': next_year
        }
        
        # Генерируем сертификат
        success, files = generator.generate_document(
            cert_data, 
            debug_mode=with_grid,
            grid_density=grid_density
        )
        
        if success and files:
            # Получаем путь к сгенерированному файлу
            generated_file = files[0]
            
            # Копируем файл в публичную папку
            filename = os.path.basename(generated_file)
            target_path = os.path.join(app.config['GENERATED_FOLDER'], filename)
            shutil.copy2(generated_file, target_path)
            
            # Возвращаем путь к файлу
            return jsonify({
                'success': True,
                'file_path': f'/static/generated/{filename}',
                'message': 'Сертификат успешно создан'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Не удалось создать сертификат'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Ошибка: {str(e)}'
        })

@app.route('/create_grid', methods=['POST'])
def create_grid():
    try:
        # Получаем данные из запроса
        data = request.json
        
        # Извлекаем параметры сетки
        template_name = data.get('template_name', 'ohrana_truda')
        grid_spacing = data.get('grid_spacing', 20)
        minor_grid_step = data.get('minor_grid_step', 5)
        grid_opacity = data.get('grid_opacity', 80)
        
        # Создаем координатную сетку
        grid_path = generator.create_detailed_grid(
            template_name=template_name,
            grid_spacing=grid_spacing,
            minor_grid_step=minor_grid_step,
            grid_opacity=grid_opacity,
            show_labels=True,
            open_file=False
        )
        
        if grid_path:
            # Копируем файл в публичную папку
            filename = os.path.basename(grid_path)
            target_path = os.path.join(app.config['GENERATED_FOLDER'], filename)
            shutil.copy2(grid_path, target_path)
            
            # Возвращаем путь к файлу
            return jsonify({
                'success': True,
                'file_path': f'/static/generated/{filename}',
                'message': 'Координатная сетка успешно создана'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Не удалось создать координатную сетку'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Ошибка: {str(e)}'
        })

@app.route('/get_default_coordinates', methods=['GET'])
def get_default_coordinates():
    return jsonify(default_coordinates)

if __name__ == '__main__':
    app.run(debug=True, port=5000) 