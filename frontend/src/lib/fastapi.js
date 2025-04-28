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

                async function readStream() {
                    let buffer = '';
                    try {
                        while (true) {
                            const { done, value } = await reader.read();
                            if (done) break;
                
                            buffer += decoder.decode(value, { stream: true });
                
                            // 여러 개의 JSON 객체가 연속으로 오거나, 쪼개져 올 수 있으므로
                            let startIdx = 0;
                            let openBraces = 0;
                            let inString = false;
                            for (let i = 0; i < buffer.length; i++) {
                                const char = buffer[i];
                                if (char === '"' && buffer[i - 1] !== '\\') {
                                    inString = !inString;
                                }
                                if (!inString) {
                                    if (char === '{') openBraces++;
                                    if (char === '}') openBraces--;
                                }
                                if (openBraces === 0 && !inString && i > startIdx) {
                                    const jsonString = buffer.slice(startIdx, i + 1);
                                    try {
                                        const parsedData = JSON.parse(jsonString);
                                        streamCallback(parsedData);
                                    } catch (parseError) {
                                        console.warn("JSON 파싱 실패:", parseError, jsonString);
                                    }
                                    startIdx = i + 1;
                                }
                            }
                            // 남은 조각은 buffer에 남겨둠
                            buffer = buffer.slice(startIdx);
                        }
                        // 스트림 종료 후 남은 버퍼 처리
                        if (buffer.trim()) {
                            try {
                                const parsedData = JSON.parse(buffer);
                                streamCallback(parsedData);
                            } catch (parseError) {
                                console.warn("마지막 JSON 파싱 실패:", parseError, buffer);
                            }
                        }
                    } catch (error) {
                        console.error("Stream read error:", error);
                    }
                }

                await readStream();
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
