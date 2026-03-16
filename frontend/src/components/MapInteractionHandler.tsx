import { useMapEvents } from 'react-leaflet';
import { LatLngTuple } from 'leaflet';

interface MapInteractionHandlerProps {
  onMapClick: (latlng: LatLngTuple) => void;
}

const MapInteractionHandler: React.FC<MapInteractionHandlerProps> = ({ onMapClick }) => {
  useMapEvents({
    click: (e) => {
      const { lat, lng } = e.latlng;
      onMapClick([lat, lng]);
    },
  });

  return null;
};

export default MapInteractionHandler;
