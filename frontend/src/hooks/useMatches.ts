import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import type { Match, Guideline, Regulation, TextSpan } from '../types';

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
  guideline_excerpt: string | null;
  regulation_excerpt: string | null;
  guideline_span_start: number | null;
  guideline_span_end: number | null;
  regulation_span_start: number | null;
  regulation_span_end: number | null;
  guideline_section?: ApiGuideline | null;
  regulation_section?: ApiRegulation | null;
};

type ApiGuideline = {
  id: number;
  external_id: string;
  title: string;
  body: string;
  language: string;
};

type ApiRegulation = {
  id: number;
  external_id: string;
  title: string;
  body: string;
  region: string;
  regulation_type: string;
  language: string;
};

const toSpan = (start: number | null, end: number | null): TextSpan | null => {
  if (typeof start !== 'number' || typeof end !== 'number') {
    return null;
  }
  if (end <= start) {
    return null;
  }
  return { start, end };
};

const toGuideline = (guideline?: ApiGuideline | null): Guideline | null => {
  if (!guideline) {
    return null;
  }
  return {
    id: guideline.id,
    externalId: guideline.external_id,
    title: guideline.title,
    body: guideline.body,
    language: guideline.language,
  };
};

const toRegulation = (regulation?: ApiRegulation | null): Regulation | null => {
  if (!regulation) {
    return null;
  }
  return {
    id: regulation.id,
    externalId: regulation.external_id,
    title: regulation.title,
    body: regulation.body,
    region: regulation.region,
    regulationType: regulation.regulation_type,
    language: regulation.language,
  };
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
  guidelineExcerpt: match.guideline_excerpt,
  regulationExcerpt: match.regulation_excerpt,
  guidelineSpan: toSpan(match.guideline_span_start, match.guideline_span_end),
  regulationSpan: toSpan(match.regulation_span_start, match.regulation_span_end),
  guidelineSection: toGuideline(match.guideline_section ?? null),
  regulationSection: toRegulation(match.regulation_section ?? null),
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
