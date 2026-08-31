import { apiClient } from './client';

export const matchFoodImage = async ({ file, topKSamples = 3 }) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('top_k_samples', topKSamples);

    const response = await apiClient.post('/rag/match-image', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });

    return response.data;
};