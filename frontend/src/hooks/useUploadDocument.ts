import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../api/client';

type UploadResponse = {
  status: string;
  sections_created: number;
  matches_created: number;
};

export type UploadPayload = {
  data: FormData;
  onProgress?: (value: number) => void;
};

export const useUploadDocument = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ data, onProgress }: UploadPayload) => {
      const response = await apiClient.post<UploadResponse>('/documents/upload', data, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (event) => {
          if (!onProgress) {
            return;
          }
          if (event.total) {
            const percent = Math.round((event.loaded / event.total) * 100);
            onProgress(Math.min(100, Math.max(0, percent)));
          }
        },
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['guidelines'] });
      queryClient.invalidateQueries({ queryKey: ['matches'] });
    },
  });
};
