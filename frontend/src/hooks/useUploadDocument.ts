import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../api/client';

type UploadResponse = {
  status: string;
  sections_created: number;
  matches_created: number;
};

export const useUploadDocument = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: FormData) => {
      const response = await apiClient.post<UploadResponse>('/documents/upload', payload, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['guidelines'] });
      queryClient.invalidateQueries({ queryKey: ['matches'] });
    },
  });
};
