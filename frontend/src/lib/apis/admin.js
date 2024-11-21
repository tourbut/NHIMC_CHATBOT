import fastapi from "$lib/fastapi";

export async function get_llm(params, success_callback, failure_callback) {
    let url = "/admin/get_llm/"
    await fastapi('get', url, params,success_callback,failure_callback)
}

export async function create_llm(params, success_callback, failure_callback) {
    let url = "/admin/create_llm/"
    await fastapi('post', url, params,success_callback,failure_callback)
}

export async function update_llm(params, success_callback, failure_callback) {
    let url = "/admin/update_llm/"
    await fastapi('put', url, params,success_callback,failure_callback)
}

export async function get_dept(params, success_callback, failure_callback) {
    let url = "/admin/get_dept/"
    await fastapi('get', url, params,success_callback,failure_callback)
}

export async function get_apikey(params, success_callback, failure_callback) {
    let url = "/admin/get_apikey/"
    await fastapi('get', url, params,success_callback,failure_callback)
}

export async function create_apikey(params, success_callback, failure_callback) {
    let url = "/admin/create_apikey/"
    await fastapi('post', url, params,success_callback,failure_callback)
}

export async function update_apikey(params, success_callback, failure_callback) {
    let url = "/admin/update_apikey/"
    await fastapi('put', url, params,success_callback,failure_callback)
}

export async function get_deptllm(params, success_callback, failure_callback) {
    let url = "/admin/get_deptllm/"
    await fastapi('get', url, params,success_callback,failure_callback)
}

export async function create_deptllm(params, success_callback, failure_callback) {
    let url = "/admin/create_deptllm/"
    await fastapi('post', url, params,success_callback,failure_callback)
}

export async function update_deptllm(params, success_callback, failure_callback) {
    let url = "/admin/update_deptllm/"
    await fastapi('put', url, params,success_callback,failure_callback)
}

export async function get_deptusage(params, success_callback, failure_callback) {
    let url = "/admin/get_deptusage/"
    await fastapi('get', url, params,success_callback,failure_callback)
}