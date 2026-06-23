//1111
//
//
export const mapToFrontFormat = window.APP_CONFIG.functions.mapObjectToFrontFormat;

//22222
//const platformMapper = window.APP_CONFIG.functions.mapObjectToFrontFormat;
//
//export const mapToFrontFormat = (object) => {
//    const mapped = platformMapper(object);
//    return {
//        ...mapped,
//        // Гарантируем фронтенду наличие флага папки, если тип DIRECTORY или имя заканчивается на слэш
//        folder: object.type === 'DIRECTORY' || mapped.type === 'DIRECTORY' || (object.name && object.name.endsWith('/'))
//    };
//};

//333
//const platformMapper = window.APP_CONFIG.functions.mapObjectToFrontFormat;
//
//export const mapToFrontFormat = (obj) => {
//    // Вызываем базовый маппер (чтобы сохранить структуру)
//    const mapped = platformMapper(obj);
//
//    const isFolder = obj.type === 'DIRECTORY';
//
//    // 1. Исправляем ИМЯ: если это папка, фронту обязательно нужен слэш на конце
//    let correctedName = obj.name;
//    if (isFolder && !correctedName.endsWith('/')) {
//        correctedName += '/';
//    }
//
//    // 2. Исправляем БАЗОВЫЙ ПУТЬ: добавляем слэш к родительскому пути, если он есть и не пустой
//    let basePath = obj.path || '';
//    if (basePath && !basePath.endsWith('/')) {
//        basePath += '/';
//    }
//
//    // 3. Собираем ПОЛНЫЙ ПУТЬ: гарантируем правильную вложенность (например, "f0/f0/")
//    let correctedFullPath = basePath + correctedName;
//
//    return {
//        ...mapped,
//        lastModified: obj.lastModified || null, // сохраняем дату, если она есть
//        name: correctedName,
//        path: correctedFullPath,
//        folder: isFolder
//    };
//};