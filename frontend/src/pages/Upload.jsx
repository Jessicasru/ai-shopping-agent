import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles } from 'lucide-react';
import { cn } from '../lib/utils';
import { StyleDropzone } from '../components/StyleDropzone';
import { ImageGrid } from '../components/ImageGrid';
import { analyzeStyle } from '../api';

const MIN_FILES = 10;
const MAX_FILES = 15;

export default function Upload() {
  const navigate = useNavigate();
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFilesAdded = useCallback((files) => {
    const newImages = files.map((file) => ({
      id: `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
      file,
      url: URL.createObjectURL(file),
    }));
    setImages((prev) => [...prev, ...newImages]);
  }, []);

  const handleRemove = useCallback((id) => {
    setImages((prev) => {
      const image = prev.find((img) => img.id === id);
      if (image) {
        URL.revokeObjectURL(image.url);
      }
      return prev.filter((img) => img.id !== id);
    });
  }, []);

  const isReady = images.length >= MIN_FILES;

  const handleAnalyze = useCallback(async () => {
    if (!isReady) return;
    setLoading(true);
    setError(null);
    try {
      await analyzeStyle(images.map((img) => img.file));
      navigate('/profile');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [isReady, images, navigate]);

  return (
    <div className="mx-auto max-w-3xl px-6 py-16">
      <h1 className="font-serif text-3xl md:text-4xl tracking-tight text-[hsl(var(--foreground))]">
        Upload Style Photos
      </h1>
      <p className="mt-3 text-sm text-[hsl(var(--muted-foreground))]">
        Add outfit photos, fashion inspiration, or screenshots of items you love.
      </p>

      {/* Dropzone */}
      <section aria-label="Image upload area" className="mt-8 mb-8">
        <StyleDropzone
          onFilesAdded={handleFilesAdded}
          imageCount={images.length}
          maxFiles={MAX_FILES}
        />
      </section>

      {/* Image Grid */}
      {images.length > 0 && (
        <section aria-label="Uploaded images" className="mb-10">
          <div className="mb-4 flex items-center justify-between">
            <p className="text-xs tracking-[0.15em] uppercase text-[hsl(var(--muted-foreground))]">
              Your selections
            </p>
            <p className="text-xs text-[hsl(var(--muted-foreground))] tabular-nums">
              {images.length} / {MAX_FILES}
            </p>
          </div>
          <ImageGrid images={images} onRemove={handleRemove} />
        </section>
      )}

      {/* Progress indicator */}
      {images.length > 0 && images.length < MIN_FILES && (
        <div className="mb-10">
          <div className="h-px w-full bg-[hsl(var(--border))] overflow-hidden rounded-full">
            <div
              className="h-full bg-[hsl(var(--foreground)/0.3)] transition-all duration-700 ease-out"
              style={{ width: `${(images.length / MIN_FILES) * 100}%` }}
            />
          </div>
          <p className="mt-2.5 text-center text-xs text-[hsl(var(--muted-foreground))]">
            {MIN_FILES - images.length} more image
            {MIN_FILES - images.length !== 1 ? 's' : ''} needed to unlock
            analysis
          </p>
        </div>
      )}

      {error && (
        <p className="mb-6 text-sm text-red-600 text-center">{error}</p>
      )}

      {/* Analyze Button */}
      <div className="flex justify-center">
        <button
          type="button"
          disabled={!isReady || loading}
          onClick={handleAnalyze}
          className={cn(
            'group relative flex items-center gap-2.5 rounded-full px-8 py-3.5 text-sm tracking-[0.1em] uppercase transition-all duration-500',
            isReady && !loading
              ? 'bg-[hsl(var(--foreground))] text-[hsl(var(--background))] hover:gap-3.5 cursor-pointer'
              : 'bg-[hsl(var(--muted))] text-[hsl(var(--muted-foreground))] cursor-not-allowed',
          )}
        >
          <Sparkles
            className={cn(
              'h-4 w-4 transition-transform duration-500',
              isReady && !loading && 'group-hover:rotate-12',
            )}
          />
          {loading ? 'Analyzing...' : 'Analyze My Style'}
        </button>
      </div>
    </div>
  );
}
