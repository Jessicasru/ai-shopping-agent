import { useCallback, useRef, useState } from 'react';
import { Upload } from 'lucide-react';
import { cn } from '../lib/utils';

const ACCEPTED_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/heic'];

export function StyleDropzone({ onFilesAdded, imageCount, maxFiles = 15 }) {
  const [isDragOver, setIsDragOver] = useState(false);
  const inputRef = useRef(null);

  const processFiles = useCallback(
    (fileList) => {
      if (!fileList) return;
      const remaining = maxFiles - imageCount;
      if (remaining <= 0) return;
      const validFiles = Array.from(fileList)
        .filter((f) => ACCEPTED_TYPES.includes(f.type))
        .slice(0, remaining);
      if (validFiles.length > 0) {
        onFilesAdded(validFiles);
      }
    },
    [imageCount, maxFiles, onFilesAdded],
  );

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback(
    (e) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragOver(false);
      processFiles(e.dataTransfer.files);
    },
    [processFiles],
  );

  const handleClick = useCallback(() => {
    inputRef.current?.click();
  }, []);

  const handleChange = useCallback(
    (e) => {
      processFiles(e.target.files);
      if (inputRef.current) {
        inputRef.current.value = '';
      }
    },
    [processFiles],
  );

  const isFull = imageCount >= maxFiles;

  return (
    <div
      role="button"
      tabIndex={0}
      aria-label="Upload outfit images by clicking or dragging files here"
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={isFull ? undefined : handleClick}
      onKeyDown={(e) => {
        if ((e.key === 'Enter' || e.key === ' ') && !isFull) {
          e.preventDefault();
          handleClick();
        }
      }}
      className={cn(
        'relative flex flex-col items-center justify-center rounded-lg px-6 py-16 md:py-24 transition-all duration-300 ease-out',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[hsl(var(--ring))] focus-visible:ring-offset-2 focus-visible:ring-offset-[hsl(var(--background))]',
        isFull
          ? 'border-2 border-dashed border-[hsl(var(--border)/0.6)] bg-[hsl(var(--dropzone))] opacity-50 cursor-not-allowed'
          : isDragOver
            ? 'border-2 border-solid border-[hsl(var(--foreground)/0.4)] bg-[hsl(var(--dropzone-hover))] cursor-pointer'
            : 'border-2 border-dashed border-[hsl(var(--border))] bg-[hsl(var(--dropzone))] hover:border-[hsl(var(--foreground)/0.2)] hover:bg-[hsl(var(--dropzone-hover))] cursor-pointer',
      )}
    >
      <div
        className={cn(
          'mb-5 flex h-12 w-12 items-center justify-center rounded-full transition-all duration-300',
          isDragOver ? 'bg-[hsl(var(--foreground)/0.1)] scale-110' : 'bg-[hsl(var(--foreground)/0.04)]',
        )}
      >
        <Upload
          className={cn(
            'h-5 w-5 transition-all duration-300',
            isDragOver
              ? 'text-[hsl(var(--foreground))] -translate-y-0.5'
              : 'text-[hsl(var(--muted-foreground))]',
          )}
        />
      </div>

      <p className="mb-1 font-serif text-lg md:text-xl text-[hsl(var(--foreground))]">
        {isFull
          ? 'Maximum images reached'
          : 'Drop 10\u201315 images of outfits you love'}
      </p>

      <p className="text-sm text-[hsl(var(--muted-foreground))]">
        {isFull
          ? `${maxFiles} of ${maxFiles} images uploaded`
          : imageCount === 0
            ? 'Drag and drop or click to browse'
            : `${imageCount} image${imageCount !== 1 ? 's' : ''} selected \u2014 ${
                imageCount < 10
                  ? `add ${10 - imageCount} more`
                  : 'ready to analyze'
              }`}
      </p>

      <span
        className={cn(
          'mt-5 inline-block rounded-full border border-[hsl(var(--border))] px-5 py-1.5 text-xs tracking-[0.12em] uppercase text-[hsl(var(--muted-foreground))] transition-colors duration-300',
          !isFull && 'hover:text-[hsl(var(--foreground))] hover:border-[hsl(var(--foreground)/0.3)]',
        )}
      >
        Browse files
      </span>

      <p className="mt-4 text-[11px] text-[hsl(var(--muted-foreground)/0.6)]">
        JPG, PNG, WebP accepted
      </p>

      <input
        ref={inputRef}
        type="file"
        accept={ACCEPTED_TYPES.join(',')}
        multiple
        className="sr-only"
        onChange={handleChange}
        aria-hidden="true"
        tabIndex={-1}
        disabled={isFull}
      />
    </div>
  );
}
