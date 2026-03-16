import React, { useState, useRef, useEffect } from 'react';
import toast from 'react-hot-toast';

interface ImageViewerProps {
  imageUrl?: string;
  imageData?: string; // Base64 encoded image data
  alt?: string;
  className?: string;
  onExport?: (format: 'png' | 'jpg' | 'tiff') => void;
  isLoading?: boolean;
}

interface ZoomControls {
  scale: number;
  translateX: number;
  translateY: number;
}

const ImageViewer: React.FC<ImageViewerProps> = ({
  imageUrl,
  imageData,
  alt = 'Satellite Image',
  className = '',
  onExport,
  isLoading = false,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const imageRef = useRef<HTMLImageElement>(null);

  const [zoomControls, setZoomControls] = useState<ZoomControls>({
    scale: 1,
    translateX: 0,
    translateY: 0,
  });

  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [imageLoaded, setImageLoaded] = useState(false);

  // Reset zoom when image changes
  useEffect(() => {
    setZoomControls({
      scale: 1,
      translateX: 0,
      translateY: 0,
    });
    setImageLoaded(false);
  }, [imageUrl, imageData]);

  const handleZoomIn = () => {
    setZoomControls(prev => ({
      ...prev,
      scale: Math.min(prev.scale * 1.2, 5), // Max zoom 5x
    }));
  };

  const handleZoomOut = () => {
    setZoomControls(prev => ({
      ...prev,
      scale: Math.max(prev.scale / 1.2, 0.1), // Min zoom 0.1x
    }));
  };

  const handleFitToScreen = () => {
    setZoomControls({
      scale: 1,
      translateX: 0,
      translateY: 0,
    });
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    if (zoomControls.scale > 1) {
      setIsDragging(true);
      setDragStart({
        x: e.clientX - zoomControls.translateX,
        y: e.clientY - zoomControls.translateY,
      });
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging && zoomControls.scale > 1) {
      setZoomControls(prev => ({
        ...prev,
        translateX: e.clientX - dragStart.x,
        translateY: e.clientY - dragStart.y,
      }));
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? 0.9 : 1.1;
    setZoomControls(prev => ({
      ...prev,
      scale: Math.min(Math.max(prev.scale * delta, 0.1), 5),
    }));
  };

  const handleExport = (format: 'png' | 'jpg' | 'tiff') => {
    if (onExport) {
      onExport(format);
    } else {
      // Default export implementation
      if (imageRef.current) {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        if (ctx && imageRef.current) {
          canvas.width = imageRef.current.naturalWidth;
          canvas.height = imageRef.current.naturalHeight;

          ctx.drawImage(imageRef.current, 0, 0);

          const mimeType = `image/${format === 'tiff' ? 'png' : format}`;
          const link = document.createElement('a');
          link.download = `landsat-image.${format}`;
          link.href = canvas.toDataURL(mimeType);
          link.click();

          toast.success(`Image exported as ${format.toUpperCase()}`);
        }
      }
    }
  };

  const getImageSource = () => {
    if (imageData) {
      return `data:image/tiff;base64,${imageData}`;
    }
    return imageUrl || '/placeholder-image.png';
  };

  if (isLoading) {
    return (
      <div className={`flex items-center justify-center bg-secondary-100 rounded-lg ${className}`}>
        <div className="text-center">
          <div className="loading-spinner w-8 h-8 mx-auto mb-2" />
          <p className="text-sm text-secondary-600">Loading image...</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`relative bg-secondary-100 rounded-lg overflow-hidden ${className}`}>
      {/* Toolbar */}
      <div className="absolute top-4 left-4 z-10 flex space-x-2">
        <div className="bg-white/90 backdrop-blur-sm rounded-lg p-2 shadow-lg">
          <div className="flex space-x-1">
            <button
              onClick={handleZoomIn}
              className="p-2 text-secondary-600 hover:text-secondary-900 hover:bg-secondary-100 rounded transition-colors duration-200"
              title="Zoom In"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" />
              </svg>
            </button>

            <button
              onClick={handleZoomOut}
              className="p-2 text-secondary-600 hover:text-secondary-900 hover:bg-secondary-100 rounded transition-colors duration-200"
              title="Zoom Out"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM7 10h6" />
              </svg>
            </button>

            <button
              onClick={handleFitToScreen}
              className="p-2 text-secondary-600 hover:text-secondary-900 hover:bg-secondary-100 rounded transition-colors duration-200"
              title="Fit to Screen"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
              </svg>
            </button>
          </div>
        </div>

        {/* Export Controls */}
        <div className="bg-white/90 backdrop-blur-sm rounded-lg p-2 shadow-lg">
          <div className="flex space-x-1">
            <button
              onClick={() => handleExport('png')}
              className="px-3 py-2 text-xs bg-primary-600 hover:bg-primary-700 text-white rounded transition-colors duration-200"
              title="Export as PNG"
            >
              PNG
            </button>

            <button
              onClick={() => handleExport('jpg')}
              className="px-3 py-2 text-xs bg-secondary-600 hover:bg-secondary-700 text-white rounded transition-colors duration-200"
              title="Export as JPG"
            >
              JPG
            </button>

            <button
              onClick={() => handleExport('tiff')}
              className="px-3 py-2 text-xs bg-success-600 hover:bg-success-700 text-white rounded transition-colors duration-200"
              title="Export as TIFF"
            >
              TIFF
            </button>
          </div>
        </div>
      </div>

      {/* Zoom Info */}
      <div className="absolute top-4 right-4 z-10 bg-white/90 backdrop-blur-sm rounded-lg px-3 py-2 shadow-lg">
        <span className="text-sm text-secondary-700">
          {Math.round(zoomControls.scale * 100)}%
        </span>
      </div>

      {/* Image Container */}
      <div
        ref={containerRef}
        className="relative w-full h-full overflow-hidden cursor-move"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onWheel={handleWheel}
      >
        <img
          ref={imageRef}
          src={getImageSource()}
          alt={alt}
          className="absolute transition-transform duration-200 ease-out"
          style={{
            transform: `translate(${zoomControls.translateX}px, ${zoomControls.translateY}px) scale(${zoomControls.scale})`,
            transformOrigin: '0 0',
            maxWidth: 'none',
            maxHeight: 'none',
          }}
          onLoad={() => setImageLoaded(true)}
          onError={() => toast.error('Failed to load image')}
          draggable={false}
        />

        {!imageLoaded && !isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-secondary-100">
            <div className="text-center">
              <svg className="w-12 h-12 text-secondary-400 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <p className="text-sm text-secondary-600">No image loaded</p>
            </div>
          </div>
        )}
      </div>

      {/* Instructions */}
      <div className="absolute bottom-4 left-4 z-10 bg-white/90 backdrop-blur-sm rounded-lg p-3 shadow-lg">
        <div className="text-xs text-secondary-600 space-y-1">
          <p><strong>Zoom:</strong> Mouse wheel or buttons</p>
          <p><strong>Pan:</strong> Click and drag (when zoomed)</p>
          <p><strong>Export:</strong> Use toolbar buttons</p>
        </div>
      </div>
    </div>
  );
};

export default ImageViewer;
