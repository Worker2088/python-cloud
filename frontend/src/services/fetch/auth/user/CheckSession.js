//import {API_USER_INFO} from "../../../../UrlConstants.jsx";
//import UnauthorizedException from "../../../../exception/UnauthorizedException.jsx";
//
//
//export const checkSession = async () => {
//    if (import.meta.env.VITE_MOCK_FETCH_CALLS) {
//        console.log("Mocked fetch call for check session");
//        return {
//            username: "mocked_user"
//        };
//    }
//
//    // --- ИЗМЕНЕНИЕ: Достаем сохраненный ID сессии из памяти браузера ---
//    const sessionId = localStorage.getItem("session_id");
//
//    const response = await fetch(API_USER_INFO, {
//        method: 'GET',
//        credentials: 'include',
//        // --- ИЗМЕНЕНИЕ: Передаем ID сессии в заголовках запроса бэкенду ---
//        headers: {
//            'Content-Type': 'application/json',
//            // Стандартный способ передачи токенов/сессий:
//            'Authorization': `Bearer ${sessionId}`
//
//            // ЕСЛИ ваш бэкенд ждет кастомный заголовок, раскомментируйте строчку ниже:
//            // 'X-Session-ID': sessionId
//        }
//    });
//
//    console.log("Проверка сессии: ");
//    console.log(response);
//    if (!response.ok) {
//        console.log("Ошибка со статусом: " + response.status);
//        const error = await response.json();
//        throw new UnauthorizedException(error.detail);
//    }
//
//    return await response.json();
//}


import {API_USER_INFO} from "../../../../UrlConstants.jsx";
import UnauthorizedException from "../../../../exception/UnauthorizedException.jsx";


export const checkSession = async () => {
    if (import.meta.env.VITE_MOCK_FETCH_CALLS) {
        console.log("Mocked fetch call for check session");
        return {
            username: "mocked_user"
        };
    }

    const response = await fetch(API_USER_INFO, {
        method: 'GET',
        credentials: 'include'
    });

    console.log("Проверка сессии: ");
    console.log(response);
    if (!response.ok) {
        console.log("Ошибка со статусом: " + response.status);
        const error = await response.json();
        throw new UnauthorizedException(error.detail);
    }

    return await response.json();
}