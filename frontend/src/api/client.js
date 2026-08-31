import axios from 'axios';

export const apiClient = axios.create({
    baseURL: '', // Vite 프록시를 통해 /rag 경로로 전달
    timeout: 60000,
});