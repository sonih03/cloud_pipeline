import { useMutation } from '@tanstack/react-query';
import { matchFoodImage } from '../api/imageRagApi';

export const useImageMatchQuery = () => {
    return useMutation({
        mutationFn: matchFoodImage,
        onError: (error) => {
            console.error('이미지 매칭 실패:', error);
        },
    });
};