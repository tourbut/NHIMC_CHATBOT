import fastapi from "$lib/fastapi";

export async function post_user(params, success_callback, failure_callback) {
    let url = "/users/signup/"
    await fastapi('post', url, params,success_callback,failure_callback)
}

export async function login(params, success_callback, failure_callback) {
    let url = "/users/login/"
    await fastapi('login', url, params,success_callback,failure_callback)
}

export async function logout(params, success_callback, failure_callback) {
    let url = "/users/logout/"
    await fastapi('post', url, params,success_callback,failure_callback)
}

export async function get_user(params, success_callback, failure_callback) {
    let url = "/users/get_user/"
    await fastapi('get', url, params,success_callback,failure_callback)
}

export async function get_userdetail(params, success_callback, failure_callback) {
    let url = "/users/get_userdetail/"
    await fastapi('get', url, params,success_callback,failure_callback)
}

export async function update_detail(params, success_callback, failure_callback) {
        let url = "/users/update_detail/"
        await fastapi('put', url, params,success_callback,failure_callback)
}

