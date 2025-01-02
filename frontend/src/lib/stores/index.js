import { writable } from 'svelte/store';
import { WEB_NAME } from '$lib/constants';

const persist_storage = (key, initValue) => {
    const storedValueStr = sessionStorage.getItem(key)
    const store = writable(storedValueStr != null ? JSON.parse(storedValueStr) : initValue)
    store.subscribe((val) => {
        sessionStorage.setItem(key, JSON.stringify(val))
    })
    return store
}

export const APP_NAME = persist_storage("APP_NAME",WEB_NAME);
export const user_token = persist_storage("user_token","");
export const username = persist_storage("username","");
export const dept_cd = persist_storage("dept_cd","");
export const dept_nm = persist_storage("dept_nm","");
export const is_admin = persist_storage("is_admin","");
export const toasts = persist_storage("toasts",[]);