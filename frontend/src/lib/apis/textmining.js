import fastapi from "$lib/fastapi";

export async function create_topic(params, success_callback, failure_callback) {
    let url = "/textmining/create_topic/"
    await fastapi('post', url, params,success_callback,failure_callback)
}

export async function get_topics(params, success_callback, failure_callback) {
    let url = "/textmining/get_topics/"
    await fastapi('get', url, params,success_callback,failure_callback)
}

export async function get_topic(params, success_callback, failure_callback) {
    let url = "/textmining/get_topic/"
    await fastapi('get', url, params,success_callback,failure_callback)
}

export async function update_topic(params, success_callback, failure_callback) {
    let url = "/textmining/update_topic/"
    await fastapi('put', url, params,success_callback,failure_callback)
}

export async function create_tmllm(params, success_callback, failure_callback) {
    let url = "/textmining/create_tmllm/"
    await fastapi('post', url, params,success_callback,failure_callback)
}

export async function update_tmchat(params, success_callback, failure_callback) {
    let url = "/textmining/update_tmchat/"
    await fastapi('put', url, params,success_callback,failure_callback)
}

export async function update_tmllm(params, success_callback, failure_callback) {
    let url = "/textmining/update_tmllm/"
    await fastapi('put', url, params,success_callback,failure_callback)
}

export async function get_tmllm(params, success_callback, failure_callback) {
    let url = "/textmining/get_tmllm/"
    await fastapi('get', url, params,success_callback,failure_callback)
}

export async function get_llm(params, success_callback, failure_callback) {
    let url = "/textmining/get_llm/"
    await fastapi('get', url, params,success_callback,failure_callback)
}

export async function create_tmchat(params, success_callback, failure_callback) {
    let url = "/textmining/create_tmchat/"
    await fastapi('post', url, params,success_callback,failure_callback)
}

export async function get_tmchats(params, success_callback, failure_callback) {
    let url = "/textmining/get_tmchats/"
    await fastapi('get', url, params,success_callback,failure_callback)
}

export async function get_tmchat(params, success_callback, failure_callback) {
    let url = "/textmining/get_tmchat"
    await fastapi('get', url, params,success_callback,failure_callback)
}

export async function create_tmoutputschema(params, success_callback, failure_callback) {
    let url = "/textmining/create_tmoutputschema/"
    await fastapi('post', url, params,success_callback,failure_callback)
}

export async function get_tmoutputschemas(params, success_callback, failure_callback) {
    let url = "/textmining/get_tmoutputschemas/"
    await fastapi('get', url, params,success_callback,failure_callback)
}

export async function update_tmoutputschema(params, success_callback, failure_callback) {
    let url = "/textmining/update_tmoutputschema/"
    await fastapi('put', url, params,success_callback,failure_callback)
}

export async function create_tmoutputschemaattr(params, success_callback, failure_callback) {
    let url = "/textmining/create_tmoutputschemaattr/"
    await fastapi('post', url, params,success_callback,failure_callback)
}

export async function get_tmoutputschemaattrs(params, success_callback, failure_callback) {
    let url = "/textmining/get_tmoutputschemaattrs/"
    await fastapi('get', url, params,success_callback,failure_callback)
}

export async function create_userprompt(params, success_callback, failure_callback) {
    let url = "/textmining/create_userprompt/"
    await fastapi('post', url, params,success_callback,failure_callback)
}

export async function get_userprompts(params, success_callback, failure_callback) {
    let url = "/textmining/get_userprompts/"
    await fastapi('get', url, params,success_callback,failure_callback)
}

export async function create_tminstruct(params, success_callback, failure_callback) {
    let url = "/textmining/create_tminstruct/"
    await fastapi('post', url, params,success_callback,failure_callback)
}

export async function get_tminstructs(params, success_callback, failure_callback) {
    let url = "/textmining/get_tminstructs/"
    await fastapi('get', url, params,success_callback,failure_callback)
}

export async function get_tminstruct(params, success_callback, failure_callback) {
    let url = "/textmining/get_tminstruct/"
    await fastapi('get', url, params,success_callback,failure_callback)
}

export async function update_tminstruct(params, success_callback, failure_callback) {
    let url = "/textmining/update_tminstruct/"
    await fastapi('put', url, params,success_callback,failure_callback)
}


export async function send_message(params, success_callback, failure_callback,streamCallback) {
    let url = "/textmining/send_message/"
    await fastapi('post', url, params,success_callback,failure_callback,streamCallback)
}

export async function send_stream_message(params, success_callback, failure_callback,streamCallback) {
    let url = "/textmining/send_stream_message/"
    await fastapi('stream', url, params,success_callback,failure_callback,streamCallback)
}

export async function get_messages(params, success_callback, failure_callback) {
    let url = "/textmining/get_messages/"
    await fastapi('get', url, params,success_callback,failure_callback)
}

export async function create_tmextract(params, success_callback, failure_callback) {
    let url = "/textmining/create_tmextract/"
    await fastapi('post', url, params,success_callback,failure_callback)
}

export async function get_tmextracts(params, success_callback, failure_callback) {
    let url = "/textmining/get_tmextracts/"
    await fastapi('get', url, params,success_callback,failure_callback)
}

export async function get_tmextract(params, success_callback, failure_callback) {
    let url = "/textmining/get_tmextract/"
    await fastapi('get', url, params,success_callback,failure_callback)
}

export async function get_tmextracts_by_topic(params, success_callback, failure_callback) {
    let url = "/textmining/get_tmextracts_by_topic/"
    await fastapi('get', url, params,success_callback,failure_callback)
}

export async function create_tmexecset(params, success_callback, failure_callback) {
    let url = "/textmining/create_tmexecset/"
    await fastapi('post', url, params,success_callback,failure_callback)
}

export async function get_tmexecsets(params, success_callback, failure_callback) {
    let url = "/textmining/get_tmexecsets/"
    await fastapi('get', url, params,success_callback,failure_callback)
}

export async function create_tmmaster(params, success_callback, failure_callback) {
    let url = "/textmining/create_tmmaster/"
    await fastapi('post', url, params,success_callback,failure_callback)
}

export async function get_tmmasters(params, success_callback, failure_callback) {
    let url = "/textmining/get_tmmasters/"
    await fastapi('get', url, params,success_callback,failure_callback)
}

export async function get_tmmaster(params, success_callback, failure_callback) {
    let url = "/textmining/get_tmmaster/"
    await fastapi('get', url, params,success_callback,failure_callback)
}