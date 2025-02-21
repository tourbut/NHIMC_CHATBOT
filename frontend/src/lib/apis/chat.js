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

export async function get_messages_by_chatbot(params, success_callback, failure_callback) {
    let url = "/chat/get_messages_by_chatbot/"
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

export async function get_deptllm(params, success_callback, failure_callback) {
    let url = "/chat/get_deptllm/"
    await fastapi('get', url, params,success_callback,failure_callback)
}

export async function create_chatbot(params, success_callback, failure_callback) {
    let url = "/chat/create_chatbot/"
    await fastapi('post', url, params,success_callback,failure_callback)
}

export async function update_chatbot(params, success_callback, failure_callback) {
    let url = "/chat/update_chatbot/"
    await fastapi('put', url, params,success_callback,failure_callback)
}

export async function get_chatbot_list_by_userid(params, success_callback, failure_callback) {
    let url = "/chat/get_chatbot_list_by_userid/"
    await fastapi('get', url, params,success_callback,failure_callback)
}

export async function get_chatbot_list_by_public(params, success_callback, failure_callback) {
    let url = "/chat/get_chatbot_list_by_public/"
    await fastapi('get', url, params,success_callback,failure_callback)
}

export async function get_chatbot(params, success_callback, failure_callback) {
    let url = "/chat/get_chatbot/"
    await fastapi('get', url, params,success_callback,failure_callback)
}

export async function get_botdocuments(params, success_callback, failure_callback) {
    let url = "/chat/get_botdocuments/"
    await fastapi('get', url, params,success_callback,failure_callback)
}

export async function send_message_bot(params, success_callback, failure_callback,streamCallback) {
    let url = "/chat/send_message_bot/"
    await fastapi('stream', url, params,success_callback,failure_callback,streamCallback)
}

export async function clear_messages(params, success_callback, failure_callback) {
    let url = "/chat/clear_messages/"
    await fastapi('put', url, params,success_callback,failure_callback)
}