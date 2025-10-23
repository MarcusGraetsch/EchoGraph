export type Guideline = {
    id: number;
    externalId: string;
    title: string;
    body: string;
    language: string;
};

export type Regulation = {
    id: number;
    externalId: string;
    title: string;
    body: string;
    region: string;
    regulationType: string;
    language: string;
};

export type TextSpan = {
    start: number;
    end: number;
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
    guidelineExcerpt?: string | null;
    regulationExcerpt?: string | null;
    guidelineSpan?: TextSpan | null;
    regulationSpan?: TextSpan | null;
    guidelineSection?: Guideline | null;
    regulationSection?: Regulation | null;
};
