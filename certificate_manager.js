// Глобальные переменные
let coordinates = {};
let currentTemplate = 'electrosafety';
let currentSection = 'LEFT';
let gridSize = 20;
let gridVisible = false;
let isSnapToGrid = false;
let clickX = 0;
let clickY = 0;
let templateImage = null;
let pdfDocument = null;
let gridOpacity = 50;
let showCoordinates = true;
let scale = 1;
let pdfLoaded = false;

// Элементы DOM
const templateImageElement = document.getElementById('template-image');
const certificatePreview = document.getElementById('certificate-preview');
const coordinatesDisplay = document.getElementById('coordinates-display');
const gridOverlay = document.getElementById('grid-overlay');
const crosshair = document.getElementById('crosshair');
const templateSelect = document.getElementById('template-select');
const sectionSelect = document.getElementById('section-select');
const coordinateName = document.getElementById('coordinate-name');
const saveCoordinateBtn = document.getElementById('save-coordinate');
const clearCoordinatesBtn = document.getElementById('clear-coordinates');
const toggleGridBtn = document.getElementById('toggle-grid');
const uploadTemplateBtn = document.getElementById('upload-template');
const templateFileInput = document.getElementById('template-file');
const coordinatesTableBody = document.getElementById('coordinates-table-body');
const copyCoordinatesBtn = document.getElementById('copy-coordinates');
const snapToGridCheckbox = document.getElementById('snap-to-grid');
const gridSizeRange = document.getElementById('grid-size-setting');
const gridOpacityInput = document.getElementById('grid-opacity-input');
const showCoordinatesCheckbox = document.getElementById('show-coordinates');

// Карта шаблонов сертификатов
const templateMap = {
    'ELECTROBEZ': {
        name: 'Электробезопасность',
        file: 'Электробез корочка .pdf',
        previewImage: 'Электробез корочка .jpg'
    },
    'OHRANA_TRUDA': {
        name: 'Безопасность и охрана труда',
        file: 'Безопастность и охрана труда корочка.pdf',
        previewImage: 'Безопастность и охрана труда корочка.jpg'
    },
    'POZHARNAYA': {
        name: 'Пожарная безопасность',
        file: 'Пожарная безопастность корочка.pdf',
        previewImage: 'Пожарная безопастность корочка.jpg'
    },
    'PROMBEZ': {
        name: 'Промышленная безопасность',
        file: 'Промбез корочка.pdf',
        previewImage: 'Промбез корочка.jpg'
    }
};

// Карта описаний полей
const fieldDescriptions = {
    'protocol_number': 'Номер удостоверения',
    'workplace': 'Организация',
    'fullname': 'ФИО',
    'job_title': 'Должность',
    'group_text': 'Группа допуска',
    'cert_day': 'День выдачи',
    'cert_month': 'Месяц выдачи',
    'cert_year': 'Год выдачи',
    'cert_date': 'Дата проверки',
    'reason': 'Причина проверки',
    'group': 'Группа (римская)',
    'mark': 'Оценка',
    'next_date': 'Дата следующей проверки'
};

// Константы для типов шаблонов и их файловых путей
const TEMPLATE_PATHS = {
    'electrosafety': 'Электробез корочка .pdf',
    'workersafety': 'Безопастность и охрана труда корочка.pdf',
    'firesafety': 'Пожарная безопастность корочка.pdf',
    'industrialsafety': 'Промбез корочка.pdf'
};

// Константы для перевода типов шаблонов в значения Python
const TEMPLATE_PY_VALUES = {
    'electrosafety': 'Курс по электробезопасности',
    'workersafety': 'Безопасность и Охрана труда',
    'firesafety': 'Пожарная безопасность',
    'industrialsafety': 'Промышленная безопасность'
};

// Инициализация PDF.js
pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.4.120/pdf.worker.min.js';

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    // Загрузка сохраненных координат из localStorage
    loadCoordinates();
    
    // Загрузка начального изображения шаблона
    loadTemplateImage(currentTemplate);
    
    // Инициализация UI элементов
    initUI();
    
    // Обновление таблицы координат
    updateCoordinatesTable();
    
    // Загрузка настроек из localStorage
    loadSettings();
});

// Инициализация пользовательского интерфейса
function initUI() {
    // Настройка обработчиков событий для редактора координат
    certificatePreview.addEventListener('mousemove', handleMouseMove);
    certificatePreview.addEventListener('mouseleave', handleMouseLeave);
    certificatePreview.addEventListener('click', handleMouseClick);
    
    // Обработчики для элементов управления
    templateSelect.addEventListener('change', handleTemplateChange);
    sectionSelect.addEventListener('change', handleSectionChange);
    saveCoordinateBtn.addEventListener('click', saveCoordinate);
    clearCoordinatesBtn.addEventListener('click', clearCoordinates);
    toggleGridBtn.addEventListener('click', toggleGrid);
    uploadTemplateBtn.addEventListener('click', () => templateFileInput.click());
    templateFileInput.addEventListener('change', handleFileUpload);
    copyCoordinatesBtn.addEventListener('click', copyCoordinatesToClipboard);
    snapToGridCheckbox.addEventListener('change', () => {
        isSnapToGrid = snapToGridCheckbox.checked;
    });
    gridSizeRange.addEventListener('change', () => {
        gridSize = parseInt(gridSizeRange.value);
        if (gridVisible) {
            drawGrid();
        }
    });
    gridOpacityInput.addEventListener('change', () => {
        gridOpacity = parseInt(gridOpacityInput.value);
        if (gridVisible) {
            drawGrid();
        }
    });
    showCoordinatesCheckbox.addEventListener('change', () => {
        showCoordinates = showCoordinatesCheckbox.checked;
        if (showCoordinates) {
            displayCoordinateMarkers();
        } else {
            document.getElementById('coordinatesOverlay').innerHTML = '';
        }
    });
    
    // Инициализация вкладки генератора сертификатов
    document.getElementById('cert-template').addEventListener('change', toggleGroupField);
    document.getElementById('generate-certificate').addEventListener('click', generateCertificate);
    
    // Начальная настройка видимости поля группы
    toggleGroupField();
}

// Загрузка координат из localStorage
function loadCoordinates() {
    const savedCoordinates = localStorage.getItem('certificateCoordinates');
    if (savedCoordinates) {
        try {
            coordinates = JSON.parse(savedCoordinates);
        } catch (e) {
            console.error('Ошибка при загрузке координат:', e);
            coordinates = {};
        }
    }
}

// Сохранение координат в localStorage
function saveCoordinates() {
    localStorage.setItem('certificateCoordinates', JSON.stringify(coordinates));
}

// Загрузка изображения шаблона
function loadTemplateImage(template) {
    if (templateMap[template]) {
        // В реальном приложении здесь может быть код для конвертации PDF в изображение
        // Для демонстрации используем заготовленные изображения
        templateImageElement.src = templateMap[template].previewImage;
        templateImageElement.onload = () => {
            // После загрузки изображения сбрасываем размер canvas и перерисовываем сетку
            if (gridVisible) {
                drawGrid();
            }
            // Отображаем сохраненные маркеры координат
            displayCoordinateMarkers();
        };
    }
}

// Обработка движения мыши над изображением
function handleMouseMove(e) {
    const rect = templateImageElement.getBoundingClientRect();
    let x = Math.round(e.clientX - rect.left);
    let y = Math.round(e.clientY - rect.top);
    
    // Привязка к сетке если включена
    if (isSnapToGrid) {
        x = Math.round(x / gridSize) * gridSize;
        y = Math.round(y / gridSize) * gridSize;
    }
    
    // Отображение координат
    coordinatesDisplay.textContent = `X: ${x}, Y: ${y}`;
    
    // Позиционирование перекрестия
    crosshair.style.display = 'block';
    crosshair.style.left = `${x}px`;
    crosshair.style.top = `${y}px`;
    
    // Сохраняем текущие координаты клика
    clickX = Math.round(x);
    clickY = Math.round(y);
}

// Обработка ухода мыши с изображения
function handleMouseLeave() {
    crosshair.style.display = 'none';
    coordinatesDisplay.textContent = 'X: 0, Y: 0';
}

// Обработка клика по изображению
function handleMouseClick(e) {
    const rect = templateImageElement.getBoundingClientRect();
    let x = Math.round(e.clientX - rect.left);
    let y = Math.round(e.clientY - rect.top);
    
    // Привязка к сетке если включена
    if (isSnapToGrid) {
        x = Math.round(x / gridSize) * gridSize;
        y = Math.round(y / gridSize) * gridSize;
    }
    
    coordinatesDisplay.textContent = `X: ${x}, Y: ${y}`;
    coordinateName.focus();
}

// Обработка изменения выбранного шаблона
function handleTemplateChange() {
    currentTemplate = templateSelect.value;
    loadTemplateImage(currentTemplate);
    updateCoordinatesTable();
}

// Обработка изменения выбранной секции
function handleSectionChange() {
    currentSection = sectionSelect.value;
    updateCoordinatesTable();
    displayCoordinateMarkers();
}

// Сохранение новой координаты
function saveCoordinate() {
    const name = coordinateName.value.trim();
    if (!name) {
        alert('Введите название координаты!');
        coordinateName.focus();
        return;
    }
    
    if (clickX === 0 && clickY === 0) {
        alert('Кликните по изображению для выбора координат!');
        return;
    }
    
    // Создаем структуру если нужно
    if (!coordinates[currentTemplate]) {
        coordinates[currentTemplate] = {};
    }
    if (!coordinates[currentTemplate][currentSection]) {
        coordinates[currentTemplate][currentSection] = {};
    }
    
    // Сохраняем координату
    coordinates[currentTemplate][currentSection][name] = [clickX, clickY];
    
    // Обновляем UI
    saveCoordinates();
    updateCoordinatesTable();
    displayCoordinateMarkers();
    
    // Сбрасываем поле ввода
    coordinateName.value = '';
}

// Обновление таблицы координат
function updateCoordinatesTable() {
    coordinatesTableBody.innerHTML = '';
    
    // Проверяем существование соответствующей структуры
    if (!coordinates[currentTemplate] || !coordinates[currentTemplate][currentSection]) {
        return;
    }
    
    // Добавляем строки для каждой координаты
    for (const [name, coords] of Object.entries(coordinates[currentTemplate][currentSection])) {
        const row = document.createElement('tr');
        
        const nameCell = document.createElement('td');
        nameCell.textContent = name;
        
        const coordsCell = document.createElement('td');
        coordsCell.textContent = `(${coords[0]}, ${coords[1]})`;
        
        const actionsCell = document.createElement('td');
        
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'btn btn-sm btn-outline-danger';
        deleteBtn.innerHTML = '<i class="bi bi-trash"></i>';
        deleteBtn.addEventListener('click', () => {
            deleteCoordinate(name);
        });
        
        actionsCell.appendChild(deleteBtn);
        
        row.appendChild(nameCell);
        row.appendChild(coordsCell);
        row.appendChild(actionsCell);
        
        coordinatesTableBody.appendChild(row);
    }
}

// Удаление координаты
function deleteCoordinate(name) {
    if (coordinates[currentTemplate] && 
        coordinates[currentTemplate][currentSection] && 
        coordinates[currentTemplate][currentSection][name]) {
        
        delete coordinates[currentTemplate][currentSection][name];
        
        // Если секция пуста, удаляем её
        if (Object.keys(coordinates[currentTemplate][currentSection]).length === 0) {
            delete coordinates[currentTemplate][currentSection];
            
            // Если шаблон пуст, удаляем его
            if (Object.keys(coordinates[currentTemplate]).length === 0) {
                delete coordinates[currentTemplate];
            }
        }
        
        saveCoordinates();
        updateCoordinatesTable();
        displayCoordinateMarkers();
    }
}

// Очистка всех координат
function clearCoordinates() {
    if (confirm('Вы уверены, что хотите удалить все координаты?')) {
        coordinates = {};
        saveCoordinates();
        updateCoordinatesTable();
        displayCoordinateMarkers();
    }
}

// Переключение отображения сетки
function toggleGrid() {
    gridVisible = !gridVisible;
    
    if (gridVisible) {
        drawGrid();
        toggleGridBtn.innerHTML = '<i class="bi bi-grid-3x3"></i> Скрыть сетку';
    } else {
        clearGrid();
        toggleGridBtn.innerHTML = '<i class="bi bi-grid-3x3"></i> Показать сетку';
    }
}

// Отрисовка сетки
function drawGrid() {
    const ctx = gridOverlay.getContext('2d');
    clearGrid();
    
    gridOverlay.width = templateImageElement.width;
    gridOverlay.height = templateImageElement.height;
    
    ctx.strokeStyle = 'rgba(0, 150, 255, 0.5)';
    ctx.lineWidth = 0.5;
    
    // Вертикальные линии
    for (let x = 0; x <= templateImageElement.width; x += gridSize) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, templateImageElement.height);
        ctx.stroke();
        
        // Метки для основных линий
        if (x % (gridSize * 5) === 0) {
            ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
            ctx.font = '10px Arial';
            ctx.fillText(x.toString(), x + 2, 10);
        }
    }
    
    // Горизонтальные линии
    for (let y = 0; y <= templateImageElement.height; y += gridSize) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(templateImageElement.width, y);
        ctx.stroke();
        
        // Метки для основных линий
        if (y % (gridSize * 5) === 0) {
            ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
            ctx.font = '10px Arial';
            ctx.fillText(y.toString(), 2, y + 10);
        }
    }
}

// Очистка сетки
function clearGrid() {
    const ctx = gridOverlay.getContext('2d');
    ctx.clearRect(0, 0, gridOverlay.width, gridOverlay.height);
}

// Обработка загрузки файла
function handleFileUpload(e) {
    const file = e.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    
    if (file.type === 'application/pdf') {
        alert('PDF-файлы требуют дополнительной обработки. В демо-версии загрузите уже конвертированные изображения.');
        return;
    }
    
    reader.onload = function(event) {
        templateImageElement.src = event.target.result;
        templateImageElement.onload = function() {
            if (gridVisible) {
                drawGrid();
            }
        };
    };
    
    reader.readAsDataURL(file);
}

// Отображение маркеров координат на изображении
function displayCoordinateMarkers() {
    // Удаляем существующие маркеры
    const existingMarkers = certificatePreview.querySelectorAll('.coordinate-marker');
    existingMarkers.forEach(marker => marker.remove());
    
    // Если нет координат для текущего шаблона и секции, выходим
    if (!coordinates[currentTemplate] || !coordinates[currentTemplate][currentSection]) {
        return;
    }
    
    // Создаем маркеры для каждой координаты
    for (const [name, coords] of Object.entries(coordinates[currentTemplate][currentSection])) {
        const marker = document.createElement('div');
        marker.className = 'coordinate-marker';
        marker.style.left = `${coords[0]}px`;
        marker.style.top = `${coords[1]}px`;
        marker.setAttribute('data-name', name);
        
        certificatePreview.appendChild(marker);
    }
}

// Копирование координат в буфер обмена
function copyCoordinatesToClipboard() {
    const codeModal = new bootstrap.Modal(document.getElementById('codeModal'));
    const coordinatesCode = document.getElementById('coordinates-code');
    
    // Генерируем Python код для координат
    let code = 'COORDINATES = {\n';
    
    for (const template in coordinates) {
        code += `    # Координаты для шаблона ${template}\n`;
        code += `    '${template}': {\n`;
        
        for (const section in coordinates[template]) {
            code += `        '${section}': {\n`;
            
            for (const name in coordinates[template][section]) {
                const [x, y] = coordinates[template][section][name];
                const desc = fieldDescriptions[name] || 'Пользовательское поле';
                code += `            '${name}': (${x}, ${y}),  # ${desc}\n`;
            }
            
            code += '        },\n';
        }
        
        code += '    },\n';
    }
    
    code += '}';
    coordinatesCode.textContent = code;
    
    // Показываем модальное окно
    codeModal.show();
    
    // Настраиваем копирование кода
    document.getElementById('copy-code-btn').addEventListener('click', () => {
        navigator.clipboard.writeText(code).then(() => {
            alert('Код скопирован в буфер обмена!');
        });
    });
}

// Переключение видимости поля группы в зависимости от типа сертификата
function toggleGroupField() {
    const selectedTemplate = document.getElementById('cert-template').value;
    const groupContainer = document.getElementById('group-container');
    
    if (selectedTemplate === 'Курс по электробезопасности') {
        groupContainer.style.display = 'block';
    } else {
        groupContainer.style.display = 'none';
    }
}

// Генерация сертификата (демо-функционал)
function generateCertificate() {
    const templateValue = document.getElementById('cert-template').value;
    const fullname = document.getElementById('cert-fullname').value;
    const workplace = document.getElementById('cert-workplace').value;
    
    if (!fullname || !workplace) {
        alert('Пожалуйста, заполните ФИО и Организацию');
        return;
    }
    
    // В реальном приложении здесь будет код для генерации сертификата
    // В демо просто показываем соответствующее изображение шаблона
    
    let templateKey = '';
    switch (templateValue) {
        case 'Курс по электробезопасности':
            templateKey = 'ELECTROBEZ';
            break;
        case 'Безопасность и Охрана труда':
            templateKey = 'OHRANA_TRUDA';
            break;
        case 'Пожарная безопасность':
            templateKey = 'POZHARNAYA';
            break;
        case 'Промышленная безопасность':
            templateKey = 'PROMBEZ';
            break;
    }
    
    document.getElementById('preview-certificate').src = templateMap[templateKey].previewImage;
    
    // Включаем кнопки для скачивания/печати
    document.getElementById('download-certificate').disabled = false;
    document.getElementById('print-certificate').disabled = false;
    
    // Добавляем запись в историю
    addHistoryEntry(templateValue, fullname);
}

// Добавление записи в историю генерации
function addHistoryEntry(templateType, fullname) {
    const historyTable = document.getElementById('history-table-body');
    const row = document.createElement('tr');
    
    const dateCell = document.createElement('td');
    dateCell.textContent = new Date().toLocaleString();
    
    const nameCell = document.createElement('td');
    nameCell.textContent = fullname;
    
    const typeCell = document.createElement('td');
    typeCell.textContent = templateType;
    
    const actionsCell = document.createElement('td');
    const viewBtn = document.createElement('button');
    viewBtn.className = 'btn btn-sm btn-outline-primary';
    viewBtn.innerHTML = '<i class="bi bi-eye"></i>';
    actionsCell.appendChild(viewBtn);
    
    row.appendChild(dateCell);
    row.appendChild(nameCell);
    row.appendChild(typeCell);
    row.appendChild(actionsCell);
    
    historyTable.appendChild(row);
}

// Загрузка настроек из localStorage
function loadSettings() {
    if (localStorage.getItem('gridSize')) {
        gridSize = parseInt(localStorage.getItem('gridSize'));
        document.getElementById('grid-size-setting').value = gridSize;
    }
    
    if (localStorage.getItem('gridOpacity')) {
        gridOpacity = parseInt(localStorage.getItem('gridOpacity'));
        document.getElementById('grid-opacity-input').value = gridOpacity;
    }
    
    if (localStorage.getItem('snapToGrid')) {
        isSnapToGrid = localStorage.getItem('snapToGrid') === 'true';
        document.getElementById('snap-to-grid').checked = isSnapToGrid;
    }
    
    if (localStorage.getItem('showCoordinates')) {
        showCoordinates = localStorage.getItem('showCoordinates') === 'true';
        document.getElementById('show-coordinates').checked = showCoordinates;
    }
} 