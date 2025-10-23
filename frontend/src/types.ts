export type Guideline = {
  id: number;
  externalId: string;
  title: string;
  body: string;
  language: string;
};

export type Match = {
  id: number;
  guidelineId: number;
  regulationId: number;
  score: number;
  confidence: number;
  rationale: string;
  status: string;
  reviewer?: string | null;
  reviewerNotes?: string | null;
};
