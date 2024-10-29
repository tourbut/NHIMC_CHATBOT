import { API_URL } from '$lib/constants';
import { user_token } from '$lib/stores';
import { get } from "svelte/store";

const fastapi_file= async (operation, url, file, success_callback, failure_callback) => {
    let _url = API_URL + url;
    let formData = new FormData();
    formData.append('file', file);

    let options;
    
    if (operation === 'upload') {
        options = {
            method: 'post',
            headers: {

            },
            body: formData
        };
    }
    else if (operation === 'download') {
        options = {
            method: 'get',
            headers: {
                
            }
        };
    }
    else {
        alert("Invalid operation: " + operation);
        return;
    }

    const access_token = get(user_token);

    if (access_token) {
        options.headers['Authorization'] = `Bearer ${access_token}`;
    }
    if (operation === 'upload') {
        await fetch(_url, options)
            .then(response => {
                response.json()
                    .then(json => {
                        if (response.status >= 200 && response.status < 300) {
                            if (success_callback) {
                                success_callback(json);
                            }
                        } else {
                            if (failure_callback) {
                                failure_callback(json);
                            } else {
                                alert(JSON.stringify(json));
                            }
                        }
                    })
                    .catch(error => {
                        alert(JSON.stringify(error));
                    });
            })
            .catch(error => {
                console.error("Fetch error:", error.message || error);
                if (failure_callback) {
                    failure_callback(error);
                } else {
                    alert("Fetch error: " + JSON.stringify(error));
                }
            });
    }
    else if (operation === 'download') {
        await fetch(_url, options)
            .then(response => {
                if (response.status === 200) {
                    response.blob()
                        .then(blob => {
                            const url = window.URL.createObjectURL(blob);
                            const a = document.createElement('a');
                            a.href = url;
                            if (blob.type === "application/octet-stream") {
                                a.download = file.name+"."+file.ext;
                            }
                            else {
                                a.download = file.name;
                            }
                            document.body.appendChild(a);
                            a.click();
                            window.URL.revokeObjectURL(url);
                            document.body.removeChild(a);
                        })
                        .catch(error => {
                            alert(JSON.stringify(error));
                        });
                } else {
                    response.json()
                        .then(json => {
                            if (failure_callback) {
                                failure_callback(json);
                            } else {
                                alert(JSON.stringify(json));
                            }
                        })
                        .catch(error => {
                            alert(JSON.stringify(error));
                        });
                }
            })
            .catch(error => {
                console.error("Fetch error:", error.message || error);
                if (failure_callback) {
                    failure_callback(error);
                } else {
                    alert("Fetch error: " + JSON.stringify(error));
                }
            });
    }
    else {
        alert("Invalid operation: " + operation);
    }
}

export default fastapi_file;