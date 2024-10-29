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