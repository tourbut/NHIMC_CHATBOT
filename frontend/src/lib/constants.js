import { dev } from '$app/environment';

export const WEB_NAME = '국민건강보험 일산병원 챗봇';
export const FASTAPI_BASE_URL = dev ? 'http://localhost:8000' : '';
export const API_URL = `${FASTAPI_BASE_URL}/api/v1`;