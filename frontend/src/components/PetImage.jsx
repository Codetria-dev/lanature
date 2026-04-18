/**
 * PetImage Component - Phase 5 Performance Optimization
 *
 * Displays pet images with lazy loading and WebP format support.
 * Falls back to default avatar if no image is available.
 *
 * Props:
 *   pet: Pet object with image_url field
 *   size: 'thumbnail' (100x100) | 'preview' (400x400) | 'full' (800x800)
 *   className: Additional CSS classes
 *   loading: 'lazy' | 'eager' (default: 'lazy')
 */

import React from 'react';

export function PetImage({ pet, size = 'preview', className = '', loading = 'lazy' }) {
  const getSizeVariant = (baseUrl, sizeType) => {
    if (!baseUrl) return '/default-pet-avatar.svg';

    // Replace generic image path with size-specific version
    // /api/v1/uploads/pets/5/image.webp → /api/v1/uploads/pets/5/pet-5-{size}.webp
    if (baseUrl.endsWith('image.webp')) {
      const petId = baseUrl.match(/pets\/(\d+)/)?.[1];
      if (petId) {
        return `/api/v1/uploads/pets/${petId}/pet-${petId}-${sizeType}.webp`;
      }
    }

    return baseUrl;
  };

  const imageSrc = getSizeVariant(pet?.image_url, size);
  const altText = pet?.name || 'Pet';

  return (
    <img
      src={imageSrc}
      alt={altText}
      loading={loading}
      className={`rounded-lg object-cover ${className}`}
      onError={(e) => {
        // Fallback to default avatar on error
        e.target.src = '/default-pet-avatar.svg';
      }}
    />
  );
}


/**
 * PetImageUpload Component
 *
 * Handles pet image uploads with preview.
 *
 * Props:
 *   petId: ID of the pet to upload image for
 *   currentImageUrl: Current pet image URL
 *   onUploadSuccess: Callback function when upload succeeds
 *   onUploadError: Callback function when upload fails
 */

export function PetImageUpload({ petId, currentImageUrl, onUploadSuccess, onUploadError }) {
  const [preview, setPreview] = React.useState(currentImageUrl);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState(null);
  const fileInputRef = React.useRef(null);

  const handleFileSelect = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file size (5MB max)
    if (file.size > 5 * 1024 * 1024) {
      setError('File too large. Max size: 5MB');
      return;
    }

    // Validate file type
    if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
      setError('Invalid image format. Allowed: JPEG, PNG, WebP');
      return;
    }

    setError(null);
    setLoading(true);

    try {
      // Create preview
      const reader = new FileReader();
      reader.onload = (event) => {
        setPreview(event.target.result);
      };
      reader.readAsDataURL(file);

      // Upload file
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`/api/v1/pets/${petId}/image`, {
        method: 'POST',
        body: formData,
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Upload failed');
      }

      const data = await response.json();
      onUploadSuccess?.(data);
    } catch (err) {
      setError(err.message || 'Upload failed');
      onUploadError?.(err);
      setPreview(currentImageUrl);
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveImage = async () => {
    if (!confirm('Remove pet image?')) return;

    setLoading(true);
    try {
      const response = await fetch(`/api/v1/pets/${petId}/image`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to delete image');
      }

      setPreview(null);
      onUploadSuccess?.({ image_url: null });
    } catch (err) {
      setError(err.message);
      onUploadError?.(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-4">
      {/* Image Preview */}
      <div className="relative w-32 h-32 bg-gray-100 rounded-lg overflow-hidden">
        {preview ? (
          <img
            src={preview}
            alt="Preview"
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-400">
            No image
          </div>
        )}
        {loading && (
          <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
            <div className="text-white text-sm">Uploading...</div>
          </div>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div className="text-red-500 text-sm">{error}</div>
      )}

      {/* Upload Controls */}
      <div className="flex gap-2">
        <input
          ref={fileInputRef}
          type="file"
          accept="image/jpeg,image/png,image/webp"
          onChange={handleFileSelect}
          disabled={loading}
          className="hidden"
        />
        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          disabled={loading}
          className="px-3 py-2 bg-blue-500 text-white text-sm rounded hover:bg-blue-600 disabled:opacity-50"
        >
          {loading ? 'Uploading...' : 'Upload Image'}
        </button>

        {preview && (
          <button
            type="button"
            onClick={handleRemoveImage}
            disabled={loading}
            className="px-3 py-2 bg-red-500 text-white text-sm rounded hover:bg-red-600 disabled:opacity-50"
          >
            Remove
          </button>
        )}
      </div>

      {/* Info Text */}
      <p className="text-xs text-gray-500">
        Supported: JPEG, PNG, WebP (max 5MB)
      </p>
    </div>
  );
}
