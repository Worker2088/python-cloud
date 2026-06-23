//import {API_REGISTRATION} from "../../../UrlConstants.jsx";
//import {throwSpecifyException} from "../../../exception/ThrowSpecifyException.jsx";
//
//
//export const sendRegistrationForm = async (registrationData) =>{
//    if (import.meta.env.VITE_MOCK_FETCH_CALLS) {
//        console.log("Mocked fetch call for registration");
//
//        return {
//            username: "mocked_user"
//        };
//    }
//
//    console.log("Запрос на регистрацию: " + registrationData);
//
//
//    const response = await fetch(API_REGISTRATION, {
//        method: 'POST',
//        headers: {
//            'Content-Type': 'application/json',
//        },
//        credentials: 'include',
//
//        body: JSON.stringify(registrationData),
//    });
//
//    console.log("Ответ на запрос о регистрации: ");
//    console.log(response);
//    if (!response.ok) {
//        console.log("Ошибка со статусом: " + response.status);
//        const errorMessage = await response.json();
//        console.log(errorMessage);
//        throwSpecifyException(response.status, errorMessage);
//    }
//
//    // --- ИЗМЕНЕНИЕ: Читаем JSON-ответ бэкенда ---
//    const data = await response.json();
//
//    // --- ИЗМЕНЕНИЕ: Сохраняем session_id в localStorage при успешной регистрации ---
//    if (data && data.session_id) {
//        localStorage.setItem("session_id", data.session_id);
//        console.log("ID сессии после регистрации сохранен в localStorage:", data.session_id);
//    }
//
//    return data;
//}


import {API_REGISTRATION} from "../../../UrlConstants.jsx";
import {throwSpecifyException} from "../../../exception/ThrowSpecifyException.jsx";


export const sendRegistrationForm = async (registrationData) =>{
    if (import.meta.env.VITE_MOCK_FETCH_CALLS) {
        console.log("Mocked fetch call for registration");

        return {
            username: "mocked_user"
        };
    }

    console.log("Запрос на регистрацию: " + registrationData);


    const response = await fetch(API_REGISTRATION, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'include',

        body: JSON.stringify(registrationData),
    });

    console.log("Ответ на запрос о регистрации: ");
    console.log(response);
    if (!response.ok) {
        console.log("Ошибка со статусом: " + response.status);
        const errorMessage = await response.json();
        console.log(errorMessage);
        throwSpecifyException(response.status, errorMessage);
    }

    return await response.json(response);
}