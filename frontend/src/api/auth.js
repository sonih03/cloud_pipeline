import client from './client';

export const authApi = {
    register: async (username, password) => {
        const response = await client.post('/auth/register', { username, password });
        return response.data;
    },

    login: async (username, password) => {
        const response = await client.post('/auth/login', { username, password });
        return response.data;
    },

    logout: async () => {
        const response = await client.post('/auth/logout');
        return response.data;
    },

    getMe: async () => {
        const response = await client.get('/auth/me');
        return response.data;
    },
};