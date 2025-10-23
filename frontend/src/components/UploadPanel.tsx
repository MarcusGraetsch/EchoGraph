import React from 'react';
import { useUploadDocument } from '../hooks/useUploadDocument';

const DEFAULT_CATEGORY = 'guideline';

export const UploadPanel: React.FC = () => {
  const [category, setCategory] = React.useState<string>(DEFAULT_CATEGORY);
  const [language, setLanguage] = React.useState<string>('en');
  const [title, setTitle] = React.useState<string>('');
  const [file, setFile] = React.useState<File | null>(null);
  const uploadMutation = useUploadDocument();

  const resetForm = React.useCallback(() => {
    setFile(null);
    setTitle('');
    setCategory(DEFAULT_CATEGORY);
    setLanguage('en');
  }, []);

  const onFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selected = event.target.files?.[0] ?? null;
    setFile(selected);
    if (selected && !title) {
      const base = selected.name.replace(/\.[^.]+$/, '');
      setTitle(base);
    }
  };

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!file || !title.trim()) {
      return;
    }
    const formData = new FormData();
    formData.append('category', category);
    formData.append('language', language);
    formData.append('title', title.trim());
    formData.append('file', file);
    uploadMutation.mutate(formData, {
      onSuccess: () => {
        resetForm();
      },
    });
  };

  return (
    <section className="upload-panel">
      <h2>Upload document</h2>
      <p className="upload-panel__helper">
        Provide a guideline or regulation file to generate new graph relationships.
      </p>
      <form onSubmit={handleSubmit} className="upload-panel__form">
        <label className="upload-panel__field">
          <span>Document title</span>
          <input
            type="text"
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            placeholder="Cloud guideline name"
            required
          />
        </label>
        <label className="upload-panel__field">
          <span>Category</span>
          <select value={category} onChange={(event) => setCategory(event.target.value)}>
            <option value="guideline">Cloud guideline</option>
            <option value="regulation">Regulation or framework</option>
          </select>
        </label>
        <label className="upload-panel__field">
          <span>Language</span>
          <input
            type="text"
            value={language}
            onChange={(event) => setLanguage(event.target.value)}
            placeholder="en"
          />
        </label>
        <label className="upload-panel__field">
          <span>File</span>
          <input type="file" accept=".pdf,.doc,.docx,.txt" onChange={onFileChange} required />
        </label>
        <button type="submit" disabled={uploadMutation.isPending}>
          {uploadMutation.isPending ? 'Uploading…' : 'Ingest document'}
        </button>
      </form>
      {uploadMutation.isSuccess && (
        <p className="upload-panel__status" role="status">
          {`Added ${uploadMutation.data.sections_created} sections and ${uploadMutation.data.matches_created} matches.`}
        </p>
      )}
      {uploadMutation.isError && (
        <p className="upload-panel__status upload-panel__status--error" role="alert">
          Unable to upload document. Please try again.
        </p>
      )}
    </section>
  );
};
