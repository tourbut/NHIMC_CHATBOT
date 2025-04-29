import { API_URL } from '$lib/constants';
import qs from "qs";
import { user_token } from '$lib/stores';
import { get } from "svelte/store";
import { goto } from '$app/navigation';

const fastapi = async (operation, url, params, success_callback, failure_callback, streamCallback) => {
    /*
        operation: get, post, put, delete, stream
        url: /api/v1/xxx
        params: {key: value}
        success_callback: api 호출 성공 시 실행할 함수
        failure_callback: api 호출 실패 시 실행할 함수
        streamCallback: 스트리밍 데이터 처리 함수 (optional)
    */

    let method = operation === 'stream' ? 'post' : operation;
    let content_type = 'application/json';
    let body = JSON.stringify(params);

    if (operation === 'login') {
        method = 'post';
        content_type = 'application/x-www-form-urlencoded';
        body = qs.stringify(params);
    }

    let _url = API_URL + url;

    if (method === 'get' || method === 'delete') {
        _url += "?" + new URLSearchParams(params);
    }

    let options = {
        method: method,
        headers: {
            'Content-Type': content_type
        }
    };

    const access_token = get(user_token);

    if (access_token) {
        options.headers['Authorization'] = `Bearer ${access_token}`;
    }

    if (method !== 'get') {
        options['body'] = body;
    }

    await fetch(_url, options)
        .then(async response => {

            if (response.status === 204) {
                if (success_callback) {
                    success_callback();
                }
                return;
            }
            
            if (operation === 'stream' && streamCallback) {
                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let buffer = '';
            
                async function processStream() {
                    while (true) {
                        const { done, value } = await reader.read();
                        if (done) {
                            // 마지막 버퍼 처리
                            if (buffer.trim()) {
                                try {
                                    const parsed = JSON.parse(buffer);
                                    streamCallback(parsed);
                                } catch (e) {
                                    console.error("Final chunk parsing failed:", e);
                                }
                            }
                            return;
                        }
            
                        buffer += decoder.decode(value, { stream: true });
                        
                        // 줄바꿈으로 분할 (NDJSON 형식)
                        const lines = buffer.split('\n');
                        buffer = lines.pop(); // 마지막 조각 보관
            
                        for (const line of lines) {
                            if (!line.trim()) continue; // 빈 줄 무시
                            try {
                                const parsed = JSON.parse(line);
                                streamCallback(parsed);
                            } catch (e) {
                                console.error("JSON parse error:", e, "on line:", line);
                            }
                        }
                    }
                }
            
                processStream().catch(error => {
                    console.error("Stream processing failed:", error);
                });
            } else {
                response.json()
                    .then(json => {
                        if (response.status >= 200 && response.status < 300) {
                            if (success_callback) {
                                success_callback(json);
                            }
                        } else if (operation !== 'login' && response.status === 401) {
                            user_token.set('');
                            alert("로그인이 필요합니다.");
                            goto('/login');
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

export default fastapi;
