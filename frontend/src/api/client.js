import axios from 'axios';

const client = axios.create({
    baseURL: '', // Nginx 프록시(/auth, /rag)를 타므로 상대 경로 사용
    timeout: 120000,
});

// 요청 인터셉터: localStorage에 토큰이 있으면 Authorization 헤더에 Bearer 토큰 자동 주입
client.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

export default client;