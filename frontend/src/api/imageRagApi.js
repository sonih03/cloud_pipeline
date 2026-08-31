import client from './client';

export const imageRagApi = {
    matchImage: async (imageFile) => {
        const formData = new FormData();
        formData.append('file', imageFile);

        const response = await client.post('/rag/match-image', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    },
};