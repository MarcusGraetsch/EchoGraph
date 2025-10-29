import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import type { Guideline } from '../types';

type ApiGuideline = {
  id: number;
  external_id: string;
  title: string;
  body: string;
  language: string;
};

const transform = (guideline: ApiGuideline): Guideline => ({
  id: guideline.id,
  externalId: guideline.external_id,
  title: guideline.title,
  body: guideline.body,
  language: guideline.language,
});

export const useGuidelines = (language: string | null) =>
  useQuery({
    queryKey: ['guidelines', language],
    queryFn: async () => {
      const response = await apiClient.get<ApiGuideline[]>('/guidelines', {
        params: language ? { language } : undefined,
      });
      return response.data.map(transform);
    },
  });
