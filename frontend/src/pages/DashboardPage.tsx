import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, Polygon as LeafletPolygon, ImageOverlay, useMap } from 'react-leaflet';
import L, { LatLngTuple, LatLngBoundsExpression } from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { useLocationStore } from '../store/locationStore';
import type { Location } from '../types/location';
import toast from 'react-hot-toast';
import LocationList from '../components/LocationList';
import LocationForm from '../components/LocationForm';
import MapInteractionHandler from '../components/MapInteractionHandler';

// Fix Leaflet icons
import icon from 'leaflet/dist/images/marker-icon.png';
import iconRetina from 'leaflet/dist/images/marker-icon-2x.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

const MapFocusHandler: React.FC<{ bounds: LatLngBoundsExpression | null }> = ({ bounds }) => {
  const map = useMap();
  useEffect(() => {
    if (bounds) {
      map.fitBounds(bounds, { animate: true, padding: [20, 20] });
    }
  }, [bounds, map]);
  return null;
};

const DashboardPage: React.FC = () => {
  const [mapCenter] = useState<LatLngTuple>([-23.5505, -46.6333]); // São Paulo as default

  // Set up Leaflet icon fix in a useEffect to avoid top-level crashes
  useEffect(() => {
    const DefaultIcon = L.icon({
      iconUrl: icon,
      iconRetinaUrl: iconRetina,
      shadowUrl: iconShadow,
      iconSize: [25, 41],
      iconAnchor: [12, 41],
      popupAnchor: [1, -34],
      shadowSize: [41, 41]
    });

    if (L.Marker.prototype.options) {
      L.Marker.prototype.options.icon = DefaultIcon;
    }
  }, []);
  const [isDrawing, setIsDrawing] = useState(false);
  const [polygonPoints, setPolygonPoints] = useState<LatLngTuple[]>([]);
  const [showLocationForm, setShowLocationForm] = useState(false);
  const [isCreatingLocation, setIsCreatingLocation] = useState(false);
  const [calculatedData, setCalculatedData] = useState<{
    coordinates: any;
    center_point: { lat: number; lng: number };
    bounds: any;
    area_hectares: string;
  } | null>(null);

  const [selectedLocationForImages, setSelectedLocationForImages] = useState<Location | null>(null);
  const [isImagesModalOpen, setIsImagesModalOpen] = useState(false);
  const [activeImage, setActiveImage] = useState<any | null>(null);
  const [isSubDrawing, setIsSubDrawing] = useState(false);
  const [subPolygonPoints, setSubPolygonPoints] = useState<LatLngTuple[]>([]);
  const [mapBoundsToFit, setMapBoundsToFit] = useState<LatLngBoundsExpression | null>(null);

  const {
    locations,
    isLoading,
    loadLocations,
    createLocation,
  } = useLocationStore();

  useEffect(() => {
    loadLocations();
  }, [loadLocations]);

  // Automatically fit map to all locations when they are loaded
  useEffect(() => {
    if (locations.length > 0 && !activeImage) {
      const allLats: number[] = [];
      const allLngs: number[] = [];
      
      locations.forEach(loc => {
        if (loc.bounds) {
          allLats.push(loc.bounds.minLat, loc.bounds.maxLat);
          allLngs.push(loc.bounds.minLng, loc.bounds.maxLng);
        } else if (loc.center_point) {
          allLats.push(loc.center_point.lat);
          allLngs.push(loc.center_point.lng);
        }
      });

      if (allLats.length > 0 && allLngs.length > 0) {
        const bounds: LatLngBoundsExpression = [
          [Math.min(...allLats), Math.min(...allLngs)],
          [Math.max(...allLats), Math.max(...allLngs)]
        ];
        setMapBoundsToFit(bounds);
      }
    }
    // Only re-run when the number of locations changes (e.g., first load or new creation)
    // or when we're no longer focusing on an active image.
  }, [locations.length, activeImage === null]);

  const handleViewImages = (location: Location) => {
    setSelectedLocationForImages(location);
    setIsImagesModalOpen(true);
  };

  const handleMapClick = (latlng: LatLngTuple) => {
    if (isDrawing) {
      setPolygonPoints([...polygonPoints, latlng]);
    } else if (isSubDrawing) {
      setSubPolygonPoints([...subPolygonPoints, latlng]);
    } else {
      // Prevent the old point-click behavior from opening the form
      // unless we are in drawing mode and finish.
      // setSelectedLocation(latlng); // This was from the old version
      // setShowLocationForm(true);   // This was from the old version
    }
  };

  const handleFocusImage = (image: any) => {
    if (image.bounds) {
      const bounds: LatLngBoundsExpression = [
        [image.bounds.minLat, image.bounds.minLng],
        [image.bounds.maxLat, image.bounds.maxLng]
      ];
      setMapBoundsToFit(bounds);
      setActiveImage(image);
    }
  };

  const startDrawing = () => {
    setIsDrawing(true);
    setPolygonPoints([]);
    setCalculatedData(null);
    setShowLocationForm(false);
  };

  const finishDrawing = () => {
    if (polygonPoints.length < 3) {
      toast.error('Please add at least 3 points to create a polygon');
      return;
    }

    // Close the polygon by adding the first point at the end
    const closedPoints = [...polygonPoints, polygonPoints[0]];
    
    // Calculate Centroid (simplified)
    const latSum = polygonPoints.reduce((sum, p) => sum + p[0], 0);
    const lngSum = polygonPoints.reduce((sum, p) => sum + p[1], 0);
    const center_point = {
      lat: latSum / polygonPoints.length,
      lng: lngSum / polygonPoints.length,
    };

    // Calculate Bounds
    const lats = polygonPoints.map(p => p[0]);
    const lngs = polygonPoints.map(p => p[1]);
    const bounds = {
      minLat: Math.min(...lats),
      maxLat: Math.max(...lats),
      minLng: Math.min(...lngs),
      maxLng: Math.max(...lngs),
    };

    // Calculate Area in Hectares (Spherical Polygon Area approximation)
    const calculateArea = (points: LatLngTuple[]) => {
      const radius = 6378137; // Earth radius in meters
      let area = 0;
      if (points.length > 2) {
        for (let i = 0; i < points.length; i++) {
          const p1 = points[i];
          const p2 = points[(i + 1) % points.length];
          area += (p2[1] - p1[1]) * (2 + Math.sin(p1[0] * Math.PI / 180) + Math.sin(p2[0] * Math.PI / 180));
        }
        area = area * radius * radius / 2;
      }
      return Math.abs(area) / 10000; // Convert m2 to hectares
    };

    const area_hectares = calculateArea(polygonPoints).toFixed(2);

    const geojsonCoordinates = [closedPoints.map(p => [p[1], p[0]])]; // [[lng, lat], ...]

    setCalculatedData({
      coordinates: {
        type: 'Polygon',
        coordinates: geojsonCoordinates,
      },
      center_point,
      bounds,
      area_hectares,
    });

    setIsDrawing(false);
    setShowLocationForm(true);
  };

  const handleLocationSubmit = async (locationData: any) => {
    if (!calculatedData) return;

    try {
      setIsCreatingLocation(true);

      const payload = {
        ...locationData,
        coordinates: calculatedData.coordinates,
        center_point: calculatedData.center_point,
        bounds: calculatedData.bounds,
        area_hectares: calculatedData.area_hectares,
      };

      await createLocation(payload);
      toast.success('Location created successfully!');
      setShowLocationForm(false);
      setPolygonPoints([]);
      setCalculatedData(null);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to create location');
    } finally {
      setIsCreatingLocation(false);
    }
  };

  return (
    <div className="flex flex-col h-screen">
      {/* Header */}
      <div className="bg-white shadow-md border-b border-secondary-300 p-6 z-20">
        <div className="flex justify-between items-center max-w-[1600px] mx-auto w-full">
          <div className="flex items-center space-x-8">
            <div>
              <h1 className="text-3xl font-extrabold text-secondary-900 tracking-tight">Dashboard</h1>
              <p className="text-secondary-500 text-sm font-medium">Manage your locations and view Landsat imagery</p>
            </div>
            
            {/* Draw Polygon Button - Extreme visibility mode */}
            <div className="flex items-center space-x-4 border-l-2 border-secondary-200 pl-8">
              {!isDrawing ? (
                <button 
                  onClick={startDrawing}
                  className="bg-primary-600 hover:bg-primary-700 text-white font-bold py-3 px-6 rounded-xl shadow-lg transform transition-all active:scale-95 flex items-center text-lg"
                  style={{ minWidth: '200px', display: 'flex !important' }}
                >
                  <svg className="w-6 h-6 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                  DRAW POLYGON
                </button>
              ) : (
                <div className="flex items-center space-x-3 bg-primary-50 p-2 rounded-xl border border-primary-200">
                  <span className="text-base font-bold text-primary-700 px-4 py-2 animate-pulse">
                    POINTS: {polygonPoints.length}
                  </span>
                  <button 
                    onClick={finishDrawing}
                    className="bg-success-600 hover:bg-success-700 text-white font-bold py-3 px-6 rounded-lg shadow-md flex items-center transition-all active:scale-95"
                  >
                    <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                    </svg>
                    FINISH
                  </button>
                  <button 
                    onClick={() => {setIsDrawing(false); setPolygonPoints([]);}}
                    className="bg-secondary-200 hover:bg-secondary-300 text-secondary-800 font-bold py-3 px-6 rounded-lg transition-all"
                  >
                    CANCEL
                  </button>
                </div>
              )}
            </div>
          </div>

          <div className="text-sm font-bold text-secondary-600 bg-secondary-100 px-4 py-2 rounded-full border border-secondary-200">
            {locations.length} LOCATIONS
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Map Section */}
        <div className="flex-1 relative bg-secondary-100">
          <MapContainer
            center={mapCenter}
            zoom={10}
            style={{ height: '100%', width: '100%' }}
            className="z-10"
          >
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            />

            {/* Handle map clicks */}
            <MapInteractionHandler onMapClick={handleMapClick} />
            <MapFocusHandler bounds={mapBoundsToFit} />

            {/* Display active satellite image */}
            {activeImage && activeImage.file_url && activeImage.bounds && (
              <ImageOverlay
                url={activeImage.file_url}
                bounds={[
                  [activeImage.bounds.minLat, activeImage.bounds.minLng],
                  [activeImage.bounds.maxLat, activeImage.bounds.maxLng]
                ]}
                opacity={0.8}
                zIndex={5}
              />
            )}

            {/* Display temporary drawing points and lines */}
            {polygonPoints.map((point, idx) => (
              <Marker key={`point-${idx}`} position={point} />
            ))}
            {polygonPoints.length > 1 && (
              <Polyline positions={isDrawing ? [...polygonPoints, polygonPoints[0]] : polygonPoints} color="red" dashArray="5, 10" />
            )}

            {/* Sub-polygon drawing */}
            {subPolygonPoints.map((point, idx) => (
              <Marker key={`sub-point-${idx}`} position={point} />
            ))}
            {subPolygonPoints.length > 1 && (
              <Polyline positions={isSubDrawing ? [...subPolygonPoints, subPolygonPoints[0]] : subPolygonPoints} color="orange" weight={3} />
            )}

            {/* Display existing locations as Polygons */}
            {locations.map((location) => {
              const coords = (location.coordinates.coordinates[0] as unknown) as [number, number][];
              return (
                <LeafletPolygon
                  key={location.id}
                  positions={coords.map((p) => [p[1], p[0]] as LatLngTuple)}
                  color="blue"
                >
                  <Popup>
                    <div className="p-2">
                      <h3 className="font-semibold">{location.name}</h3>
                      {location.description && (
                        <p className="text-sm text-secondary-600 mt-1">
                          {location.description}
                        </p>
                      )}
                      <p className="text-xs text-secondary-500 mt-2">
                        Area: {location.area_hectares} ha
                      </p>
                    </div>
                  </Popup>
                </LeafletPolygon>
              );
            })}

            {/* Show currently calculated polygon */}
            {calculatedData && (
              <LeafletPolygon 
                positions={((calculatedData.coordinates.coordinates[0] as unknown) as [number, number][]).map((p) => [p[1], p[0]] as LatLngTuple)}
                color="green"
              />
            )}
          </MapContainer>

          {/* Location Form Overlay */}
          {showLocationForm && calculatedData && (
            <div className="absolute top-4 right-4 w-80 z-10">
              <LocationForm
                coordinates={[calculatedData.center_point.lat, calculatedData.center_point.lng]}
                onSubmit={handleLocationSubmit}
                onCancel={() => {
                  setShowLocationForm(false);
                  setCalculatedData(null);
                  setPolygonPoints([]);
                }}
                isLoading={isCreatingLocation}
              />
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="w-80 bg-white border-l border-secondary-200 flex flex-col">
          {selectedLocationForImages ? (
            <div className="flex flex-col h-full">
              <div className="p-4 border-b border-secondary-200 bg-primary-50 flex justify-between items-center">
                <div>
                  <h2 className="text-lg font-bold text-primary-900">{selectedLocationForImages.name}</h2>
                  <p className="text-xs text-primary-700">Image Gallery</p>
                </div>
                <button 
                  onClick={() => {
                    setSelectedLocationForImages(null);
                    setActiveImage(null);
                    setIsSubDrawing(false);
                  }}
                  className="p-2 hover:bg-primary-100 rounded-full text-primary-600"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {selectedLocationForImages.images?.length === 0 ? (
                  <div className="text-center py-10">
                    <p className="text-secondary-500 italic">No images requested yet.</p>
                    <button className="mt-4 btn-primary text-sm">Request Imagery</button>
                  </div>
                ) : (
                  selectedLocationForImages.images?.map((image) => (
                    <div 
                      key={image.id}
                      className={`p-4 rounded-2xl border-2 transition-all cursor-pointer ${
                        activeImage?.id === image.id ? 'border-primary-500 bg-primary-50 shadow-md' : 'border-secondary-100 hover:border-primary-200'
                      }`}
                      onClick={() => setActiveImage(image)}
                    >
                      <div className="flex justify-between items-start mb-3">
                        <span className="text-xs font-bold text-secondary-400">SCENE: {image.scene_id.substring(0, 15)}...</span>
                        <div className={`w-3 h-3 rounded-full ${
                          image.status === 'completed' ? 'bg-success-500' : 
                          image.status === 'failed' ? 'bg-error-500' : 'bg-primary-500 animate-pulse'
                        }`} />
                      </div>
                      
                      <div className="flex items-center space-x-2 mt-4">
                        <button 
                          onClick={(e) => { e.stopPropagation(); handleFocusImage(image); }}
                          className="flex-1 text-[10px] font-bold bg-white border border-secondary-200 py-2 rounded-lg hover:bg-secondary-50 flex items-center justify-center space-x-1"
                        >
                          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" />
                          </svg>
                          <span>PAN & ZOOM</span>
                        </button>
                        
                        {activeImage?.id === image.id && (
                          <button 
                            onClick={(e) => { e.stopPropagation(); setIsSubDrawing(!isSubDrawing); setSubPolygonPoints([]); }}
                            className={`flex-1 text-[10px] font-bold py-2 rounded-lg flex items-center justify-center space-x-1 ${
                              isSubDrawing ? 'bg-orange-500 text-white' : 'bg-orange-50 border border-orange-200 text-orange-600 hover:bg-orange-100'
                            }`}
                          >
                            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                            </svg>
                            <span>{isSubDrawing ? 'CANCEL DRAW' : 'DRAW AREA'}</span>
                          </button>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          ) : (
            <>
              <div className="p-4 border-b border-secondary-200">
                <h2 className="text-lg font-semibold text-secondary-900">Your Locations</h2>
              </div>

              <div className="flex-1 overflow-y-auto">
                {isLoading ? (
                  <div className="flex items-center justify-center h-32">
                    <div className="loading-spinner w-6 h-6" />
                  </div>
                ) : locations.length > 0 ? (
                  <LocationList 
                    locations={locations} 
                    onViewImages={handleViewImages}
                  />
                ) : (
                  <div className="p-4 text-center text-secondary-600">
                    <p className="mb-4">No locations yet</p>
                    <p className="text-sm">Use the "Draw Polygon" button to create your first location</p>
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
