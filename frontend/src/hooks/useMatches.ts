import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import type { Match } from '../types';

type ApiMatch = {
  id: number;
  guideline_id: number;
  regulation_id: number;
  score: number;
  confidence: number;
  rationale: string;
  status: string;
  reviewer: string | null;
  reviewer_notes: string | null;
};

const transform = (match: ApiMatch): Match => ({
  id: match.id,
  guidelineId: match.guideline_id,
  regulationId: match.regulation_id,
  score: match.score,
  confidence: match.confidence,
  rationale: match.rationale,
  status: match.status,
  reviewer: match.reviewer,
  reviewerNotes: match.reviewer_notes,
});

export const useMatches = (guidelineId: string | null) =>
  useQuery({
    queryKey: ['matches', guidelineId],
    enabled: Boolean(guidelineId),
    queryFn: async () => {
      const response = await apiClient.get<ApiMatch[]>(`/guidelines/${guidelineId}/matches`);
      return response.data.map(transform);
    },
  });
