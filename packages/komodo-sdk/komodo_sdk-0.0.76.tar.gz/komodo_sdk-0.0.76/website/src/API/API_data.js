import axios from "axios";

export function ApiPost(path, body) {
    const user = JSON.parse(localStorage.getItem('komodoUser'))
    return new Promise((resolve, reject) => {
        let headers = {
            "Content-Type": "application/json",
            "X-User-Email": user?.email,
        };
        axios
            .post(path, body, {
                headers: headers,
            })
            .then((response) => {
                resolve(response);
            })
            .catch((err) => {
                reject(err.response);
            });
    });
}

export function ApiGet(path, email) {
    const user = JSON.parse(localStorage.getItem('komodoUser'))
    return new Promise((resolve, reject) => {
        let headers = {
            "Content-Type": "application/json",
            "X-User-Email": user?.email || "test@kmdo.app",
        };
        axios
            .get(`${path}`, {
                headers: headers,
            })
            .then((response) => {
                resolve(response);
            })
            .catch((err) => {
                reject(err.response);
            });
    });
}

export function ApiDelete(path, body) {
    const user = JSON.parse(localStorage.getItem('komodoUser'))
    return new Promise((resolve, reject) => {
        let headers = {
            "Content-Type": "application/json",
            "X-User-Email": user?.email,
        };
        axios
            .delete(`${path}`, {
                headers: headers,
                data: body,
            })
            .then((response) => {
                resolve(response);
            })
            .catch((err) => {
                reject(err.response);
            });
    });
}

export function ApiPatch(path, body) {
    const user = JSON.parse(localStorage.getItem('komodoUser'))
    return new Promise((resolve, reject) => {
        let headers = {
            "Content-Type": "application/json",
            "X-User-Email": user?.email,
        };
        axios
            .patch(`${path}`, body, {
                headers: headers,
            })
            .then((response) => {
                resolve(response);
            })
            .catch((err) => {
                reject(err.response);
            });
    });
}
export function ApiPut(path, body) {
    const user = JSON.parse(localStorage.getItem('komodoUser'))
    return new Promise((resolve, reject) => {
        let headers = {
            "Content-Type": "application/json",
            "X-User-Email": user?.email,
        };
        axios
            .put(`${path}`, body, {
                headers: headers,
            })
            .then((response) => {
                resolve(response);
            })
            .catch((err) => {
                reject(err.response);
            });
    });
}