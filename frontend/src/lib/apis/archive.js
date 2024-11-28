import fastapi from "$lib/fastapi";
import fastapi_file from "$lib/fastapi_file";

export async function request_archiving(params, success_callback, failure_callback) {
    let url = "/archive/run_archiving/"
    await fastapi('post', url, params,success_callback,failure_callback)
}

export async function get_archive_list(params,success_callback, failure_callback) {
    let url = "/archive/get_archive_list/"
    await fastapi('get', url, params,success_callback,failure_callback)
}

export async function get_archive(get_id,params,success_callback, failure_callback) {
    let url = `/archive/get_archive/${get_id}`
    await fastapi('get', url, params,success_callback,failure_callback)
}

export async function delete_archive(params,success_callback, failure_callback) {
    let url = `/archive/delete_archive/`
    await fastapi('put', url, params,success_callback,failure_callback)
}

export async function delete_file(params,success_callback, failure_callback) {
    let url = `/archive/delete_file/`
    await fastapi('put', url, params,success_callback,failure_callback)
}

export async function upload_flies(params,file,success_callback, failure_callback) {
    let url = `/archive/upload_flies/`
    await fastapi_file('upload',url, params,file,success_callback,failure_callback)
}

export async function get_file(get_id,params,success_callback, failure_callback) {
    let url = `/archive/get_file/${get_id}`
    await fastapi('get', url, params,success_callback,failure_callback)
}

export async function download_file(get_id,file,success_callback, failure_callback) {
    let url = `/archive/download_file/${get_id}`
    await fastapi_file('download', url, file,success_callback,failure_callback)
}