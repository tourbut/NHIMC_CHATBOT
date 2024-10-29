import fastapi from "$lib/fastapi";

export async function get_llm(params, success_callback, failure_callback) {
    let url = "/settings/get_llm/"
    await fastapi('get', url, params,success_callback,failure_callback)
}

export async function create_apikey(params, success_callback, failure_callback) {
    let url = "/settings/create_apikey/"
    await fastapi('post', url, params,success_callback,failure_callback)
}

export async function get_apikey(params, success_callback, failure_callback) {
    let url = "/settings/get_apikey/"
    await fastapi('get', url, params,success_callback,failure_callback)
}

export async function update_apikey(params, success_callback, failure_callback) {
    let url = "/settings/update_apikey/"
    await fastapi('put', url, params,success_callback,failure_callback)
}

export async function create_userllm(params, success_callback, failure_callback) {
    let url = "/settings/create_userllm/"
    await fastapi('post', url, params,success_callback,failure_callback)
}

export async function get_userllm(params, success_callback, failure_callback) {
    let url = "/settings/get_userllm/"
    await fastapi('get', url, params,success_callback,failure_callback)
}

export async function update_userllm(params, success_callback, failure_callback) {
    let url = "/settings/update_userllm/"
    await fastapi('put', url, params,success_callback,failure_callback)
}

export async function get_userusage(params, success_callback, failure_callback) {
    let url = "/settings/get_userusage/"
    await fastapi('get', url, params,success_callback,failure_callback)
}