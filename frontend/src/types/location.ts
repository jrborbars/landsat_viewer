export interface Image {
  id: string;
  location_id: string;
  scene_id: string;
  acquisition_date: string;
  status: 'pending' | 'downloading' | 'processing' | 'completed' | 'failed';
  bounds?: {
    minLat: number;
    maxLat: number;
    minLng: number;
    maxLng: number;
  };
  file_url?: string;
  processing_results?: any;
  error_message?: string;
  created_at: string;
  updated_at: string;
}

export interface Location {
  id: string;  // UUIDv7 as string
  user_id: string;  // UUIDv7 as string
  name: string;
  description?: string;
  coordinates: {
    type: string;
    coordinates: any;
  };
  center_point: {
    lat: number;
    lng: number;
  };
  bounds?: any;
  area_hectares?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  images?: Image[];
}

export interface LocationCreate {
  name: string;
  description?: string;
  coordinates: {
    type: string;
    coordinates: number[];
  };
  center_point: {
    lat: number;
    lng: number;
  };
  bounds?: any;
  area_hectares?: string;
}

export interface LocationUpdate {
  name?: string;
  description?: string;
  coordinates?: any;
  center_point?: {
    lat: number;
    lng: number;
  };
  bounds?: any;
  area_hectares?: string;
  is_active?: boolean;
}

export interface LocationListResponse {
  locations: Location[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface LandsatImageRequest {
  location_id: string;  // UUIDv7 as string
  date: string;
  bands?: number[];
}

export interface ImageJobStatus {
  job_id: string;
  status: 'pending' | 'downloading' | 'processing' | 'completed' | 'failed';
  progress: number;
  message?: string;
  result?: any;
  error?: string;
  created_at: string;
  updated_at: string;
}
