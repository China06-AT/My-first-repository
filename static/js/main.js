// Объект для хранения координат
let coordinates = {
    'OHRANA_TRUDA': {
        'LEFT': {},
        'RIGHT': {}
    },
    'LEFT': {},
    'RIGHT': {}
};

// Переменная для хранения текущего изображения
let currentImagePath = null;

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Загружаем координаты по умолчанию
    fetchDefaultCoordinates();
    
    // Событие при изменении типа сертификата
    document.getElementById('cert-type').addEventListener('change', updateCoordinateView);
    
    // Событие при изменении плотности сетки
    document.getElementById('grid-density').addEventListener('input', function() {
        document.getElementById('grid-density-value').textContent = this.value;
    });
    
    // Кнопки для управления координатами
    document.getElementById('save-coords-btn').addEventListener('click', saveCoordinates);
    document.getElementById('reset-coords-btn').addEventListener('click', resetCoordinates);
    document.getElementById('export-coords-btn').addEventListener('click', exportCoordinates);
    document.getElementById('import-coords-btn').addEventListener('click', function() {
        document.getElementById('import-coords-input').click();
    });
    document.getElementById('import-coords-input').addEventListener('change', importCoordinates);
    
    // Кнопки для генерации сертификата
    document.getElementById('generate-btn').addEventListener('click', generateCertificate);
    document.getElementById('create-grid-btn').addEventListener('click', createCoordinateGrid);
});

// Загрузка координат по умолчанию с сервера
function fetchDefaultCoordinates() {
    fetch('/get_default_coordinates')
        .then(response => response.json())
        .then(data => {
            coordinates = data;
            updateCoordinateView();
        })
        .catch(error => {
            showToast('Ошибка загрузки координат: ' + error.message, 'error');
        });
}

// Обновление отображения координат на основе выбранного типа сертификата
function updateCoordinateView() {
    const certType = document.getElementById('cert-type').value;
    
    // Определяем, какие координаты использовать
    let leftCoords, rightCoords;
    if (certType === 'Безопасность и Охрана труда') {
        leftCoords = coordinates['OHRANA_TRUDA']['LEFT'];
        rightCoords = coordinates['OHRANA_TRUDA']['RIGHT'];
    } else {
        leftCoords = coordinates['LEFT'];
        rightCoords = coordinates['RIGHT'];
    }
    
    // Очистка контейнеров
    document.getElementById('left-coords').innerHTML = '';
    document.getElementById('right-coords').innerHTML = '';
    
    // Заполнение левой стороны
    for (const key in leftCoords) {
        if (leftCoords.hasOwnProperty(key)) {
            const [x, y] = leftCoords[key];
            
            const div = document.createElement('div');
            div.className = 'coord-input-group';
            div.innerHTML = `
                <span class="coord-label">${key}:</span>
                <div class="coord-inputs">
                    <input type="number" class="form-control form-control-sm coord-x" id="left-${key}-x" value="${x}">
                    <span>X</span>
                    <input type="number" class="form-control form-control-sm coord-y" id="left-${key}-y" value="${y}">
                    <span>Y</span>
                </div>
            `;
            document.getElementById('left-coords').appendChild(div);
        }
    }
    
    // Заполнение правой стороны
    for (const key in rightCoords) {
        if (rightCoords.hasOwnProperty(key)) {
            const [x, y] = rightCoords[key];
            
            const div = document.createElement('div');
            div.className = 'coord-input-group';
            div.innerHTML = `
                <span class="coord-label">${key}:</span>
                <div class="coord-inputs">
                    <input type="number" class="form-control form-control-sm coord-x" id="right-${key}-x" value="${x}">
                    <span>X</span>
                    <input type="number" class="form-control form-control-sm coord-y" id="right-${key}-y" value="${y}">
                    <span>Y</span>
                </div>
            `;
            document.getElementById('right-coords').appendChild(div);
        }
    }
}

// Сохранение изменений координат
function saveCoordinates() {
    const certType = document.getElementById('cert-type').value;
    
    try {
        // Обновляем координаты в зависимости от типа сертификата
        if (certType === 'Безопасность и Охрана труда') {
            for (const key in coordinates['OHRANA_TRUDA']['LEFT']) {
                const xInput = document.getElementById(`left-${key}-x`);
                const yInput = document.getElementById(`left-${key}-y`);
                
                if (xInput && yInput) {
                    const x = parseInt(xInput.value);
                    const y = parseInt(yInput.value);
                    
                    if (isNaN(x) || isNaN(y)) {
                        showToast(`Некорректное значение для ${key}`, 'error');
                        return;
                    }
                    
                    coordinates['OHRANA_TRUDA']['LEFT'][key] = [x, y];
                }
            }
            
            for (const key in coordinates['OHRANA_TRUDA']['RIGHT']) {
                const xInput = document.getElementById(`right-${key}-x`);
                const yInput = document.getElementById(`right-${key}-y`);
                
                if (xInput && yInput) {
                    const x = parseInt(xInput.value);
                    const y = parseInt(yInput.value);
                    
                    if (isNaN(x) || isNaN(y)) {
                        showToast(`Некорректное значение для ${key}`, 'error');
                        return;
                    }
                    
                    coordinates['OHRANA_TRUDA']['RIGHT'][key] = [x, y];
                }
            }
        } else {
            for (const key in coordinates['LEFT']) {
                const xInput = document.getElementById(`left-${key}-x`);
                const yInput = document.getElementById(`left-${key}-y`);
                
                if (xInput && yInput) {
                    const x = parseInt(xInput.value);
                    const y = parseInt(yInput.value);
                    
                    if (isNaN(x) || isNaN(y)) {
                        showToast(`Некорректное значение для ${key}`, 'error');
                        return;
                    }
                    
                    coordinates['LEFT'][key] = [x, y];
                }
            }
            
            for (const key in coordinates['RIGHT']) {
                const xInput = document.getElementById(`right-${key}-x`);
                const yInput = document.getElementById(`right-${key}-y`);
                
                if (xInput && yInput) {
                    const x = parseInt(xInput.value);
                    const y = parseInt(yInput.value);
                    
                    if (isNaN(x) || isNaN(y)) {
                        showToast(`Некорректное значение для ${key}`, 'error');
                        return;
                    }
                    
                    coordinates['RIGHT'][key] = [x, y];
                }
            }
        }
        
        showToast('Координаты успешно сохранены', 'success');
    } catch (error) {
        showToast(`Ошибка при сохранении координат: ${error.message}`, 'error');
    }
}

// Сброс координат к значениям по умолчанию
function resetCoordinates() {
    fetchDefaultCoordinates();
    showToast('Координаты сброшены к стандартным значениям', 'success');
}

// Экспорт координат в JSON файл
function exportCoordinates() {
    const dataStr = JSON.stringify(coordinates, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileName = 'coordinates_' + new Date().toISOString().slice(0,10) + '.json';
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileName);
    linkElement.click();
    
    showToast(`Координаты сохранены в ${exportFileName}`, 'success');
}

// Импорт координат из JSON файла
function importCoordinates(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = function(e) {
        try {
            const loadedData = JSON.parse(e.target.result);
            
            // Проверка структуры загруженных данных
            if (!loadedData.OHRANA_TRUDA || !loadedData.LEFT || !loadedData.RIGHT) {
                throw new Error("Некорректный формат файла координат");
            }
            
            coordinates = loadedData;
            updateCoordinateView();
            showToast(`Координаты загружены из ${file.name}`, 'success');
        } catch (error) {
            showToast(`Ошибка при загрузке координат: ${error.message}`, 'error');
        }
    };
    reader.readAsText(file);
    
    // Сбросить значение input, чтобы можно было выбрать тот же файл повторно
    event.target.value = '';
}

// Генерация сертификата
function generateCertificate() {
    // Сначала сохраняем координаты
    saveCoordinates();
    
    // Получаем тестовые данные
    const certType = document.getElementById('cert-type').value;
    const fullname = document.getElementById('fullname').value;
    const workplace = document.getElementById('workplace').value;
    const jobTitle = document.getElementById('job-title').value;
    const withGrid = document.getElementById('with-grid').checked;
    const gridDensity = parseInt(document.getElementById('grid-density').value);
    
    if (!fullname || !workplace || !jobTitle) {
        showToast("Заполните все данные сертификата", 'error');
        return;
    }
    
    // Показываем индикатор загрузки
    document.getElementById('pdf-placeholder').innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Загрузка...</span></div><p class="mt-2">Генерация сертификата...</p>';
    document.getElementById('pdf-placeholder').style.display = 'flex';
    document.getElementById('pdf-viewer').style.display = 'none';
    document.getElementById('view-controls').style.display = 'none';
    
    // Формируем данные запроса
    const requestData = {
        cert_type: certType,
        fullname: fullname,
        workplace: workplace,
        job_title: jobTitle,
        with_grid: withGrid,
        grid_density: gridDensity,
        coordinates: coordinates
    };
    
    // Отправляем запрос на сервер
    fetch('/generate_certificate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Успешная генерация - показываем изображение вместо PDF
            currentImagePath = data.file_path;
            
            // Добавляем случайный параметр для предотвращения кэширования
            const imageUrl = currentImagePath + '?v=' + new Date().getTime();
            
            document.getElementById('pdf-placeholder').style.display = 'none';
            document.getElementById('pdf-viewer').style.display = 'block';
            document.getElementById('image-preview').src = imageUrl;
            
            // Показываем кнопки управления просмотром
            document.getElementById('view-controls').style.display = 'block';
            document.getElementById('view-full-btn').href = imageUrl;
            
            showToast('Сертификат успешно создан', 'success');
        } else {
            // Ошибка генерации
            document.getElementById('pdf-placeholder').innerHTML = '<p>Ошибка генерации сертификата</p>';
            showToast(data.message, 'error');
        }
    })
    .catch(error => {
        document.getElementById('pdf-placeholder').innerHTML = '<p>Ошибка генерации сертификата</p>';
        showToast('Ошибка: ' + error.message, 'error');
    });
}

// Создание координатной сетки
function createCoordinateGrid() {
    // Получаем параметры сетки
    const certType = document.getElementById('cert-type').value;
    const templateName = certType === 'Безопасность и Охрана труда' ? 'ohrana_truda' : 'korotchka';
    const gridSpacing = parseInt(document.getElementById('grid-density').value);
    
    // Показываем индикатор загрузки
    document.getElementById('pdf-placeholder').innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Загрузка...</span></div><p class="mt-2">Создание координатной сетки...</p>';
    document.getElementById('pdf-placeholder').style.display = 'flex';
    document.getElementById('pdf-viewer').style.display = 'none';
    document.getElementById('view-controls').style.display = 'none';
    
    // Формируем данные запроса
    const requestData = {
        template_name: templateName,
        grid_spacing: gridSpacing,
        minor_grid_step: Math.max(1, Math.floor(gridSpacing / 5)),
        grid_opacity: 80
    };
    
    // Отправляем запрос на сервер
    fetch('/create_grid', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Успешная генерация - показываем изображение вместо PDF
            currentImagePath = data.file_path;
            
            // Добавляем случайный параметр для предотвращения кэширования
            const imageUrl = currentImagePath + '?v=' + new Date().getTime();
            
            document.getElementById('pdf-placeholder').style.display = 'none';
            document.getElementById('pdf-viewer').style.display = 'block';
            document.getElementById('image-preview').src = imageUrl;
            
            // Показываем кнопки управления просмотром
            document.getElementById('view-controls').style.display = 'block';
            document.getElementById('view-full-btn').href = imageUrl;
            
            showToast('Координатная сетка успешно создана', 'success');
        } else {
            // Ошибка генерации
            document.getElementById('pdf-placeholder').innerHTML = '<p>Ошибка создания координатной сетки</p>';
            showToast(data.message, 'error');
        }
    })
    .catch(error => {
        document.getElementById('pdf-placeholder').innerHTML = '<p>Ошибка создания координатной сетки</p>';
        showToast('Ошибка: ' + error.message, 'error');
    });
}

// Функция для отображения уведомлений
function showToast(message, type = 'success') {
    const toastId = 'toast-' + Date.now();
    const toastHtml = `
        <div id="${toastId}" class="toast toast-${type}" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header">
                <strong class="me-auto">${type === 'success' ? 'Успех' : 'Ошибка'}</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    document.getElementById('toast-container').insertAdjacentHTML('beforeend', toastHtml);
    
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, { autohide: true, delay: 5000 });
    toast.show();
    
    // Автоматическое удаление элемента уведомления после скрытия
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
} 