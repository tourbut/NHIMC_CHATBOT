import fastapi from "$lib/fastapi";

export async function send_message(params, success_callback, failure_callback,streamCallback) {
    let url = "/chat/send_message/"
    await fastapi('stream', url, params,success_callback,failure_callback,streamCallback)
}

export async function create_chat(params, success_callback, failure_callback) {
    let url = "/chat/create_chat/"
    await fastapi('post', url, params,success_callback,failure_callback)
}

export async function get_chat(params, success_callback, failure_callback) {
    let url = "/chat/get_chat/"
    await fastapi('get', url, params,success_callback,failure_callback)
}

export async function get_chat_list(params, success_callback, failure_callback) {
    let url = "/chat/get_chat_list/"
    await fastapi('get', url, params,success_callback,failure_callback)
}

export async function get_userllm(params, success_callback, failure_callback) {
    let url = "/chat/get_userllm/"
    await fastapi('get', url, params,success_callback,failure_callback)
}

export async function get_messages(params, success_callback, failure_callback) {
    let url = "/chat/get_messages/"
    await fastapi('get', url, params,success_callback,failure_callback)
}

export async function delete_chat(params, success_callback, failure_callback) {
    let url = "/chat/delete_chat/"
    await fastapi('put', url, params,success_callback,failure_callback)
}

export async function get_documents(params, success_callback, failure_callback) {
    let url = "/chat/get_documents/"
    await fastapi('get', url, params,success_callback,failure_callback)
}