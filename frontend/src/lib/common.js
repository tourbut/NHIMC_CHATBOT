import { toasts } from '$lib/stores';
import { v4 as uuidv4 } from 'uuid';


export function addToast(category,message) {
    toasts.update((toasts) => {
        return [...toasts, { id: uuidv4(), category ,message }];
    });
}

export function removeToast(id) {
    toasts.update((toasts) => {
        return toasts.filter((toast) => toast.id !== id);
    });
}
