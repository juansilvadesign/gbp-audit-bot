/**
 * GBP Audit Bot - API Client
 * 
 * Client for communicating with the FastAPI backend.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

// Types matching backend schemas (jsonfinal.md format)
export interface GridPoint {
  id: number;
  lat: number;
  lng: number;
  rank: number | null;
  status: 'success' | 'warning' | 'danger';
  color: string;
}

export interface ScanSummary {
  average_rank: number | null;
  visibility_score: number;
  top3_count: number;
  top10_count: number;
  trend?: string;
}

export interface ScanHistory {
  date: string;
  avg_rank: number;
}

export interface ScanResponse {
  id: string;
  project_id: string;
  keyword: string;
  business_name?: string;
  scan_date: string;
  grid_size: number;
  summary: ScanSummary;
  grid_data: GridPoint[];
  history?: ScanHistory[];
}

export interface Project {
  id: string;
  business_name: string;
  target_keyword: string;
  central_lat: number;
  central_lng: number;
  default_radius_km: number;
  default_grid_size: number;
  weekly_actions?: string;
}

export interface CreditEstimate {
  grid_size: number;
  total_points: number;
  credits_required: number;
  user_balance: number;
  has_sufficient_credits: boolean;
  message: string;
}

export interface User {
  id: string;
  email: string;
  name: string;
  credits_balance: number;
}

// Auth token management
let authToken: string | null = null;

export function setAuthToken(token: string) {
  authToken = token;
  if (typeof window !== 'undefined') {
    localStorage.setItem('gbp_token', token);
  }
}

export function getAuthToken(): string | null {
  if (authToken) return authToken;
  if (typeof window !== 'undefined') {
    return localStorage.getItem('gbp_token');
  }
  return null;
}

export function clearAuthToken() {
  authToken = null;
  if (typeof window !== 'undefined') {
    localStorage.removeItem('gbp_token');
  }
}

// API request helper
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getAuthToken();

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (token) {
    (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

// Auth endpoints
export async function login(email: string, password: string): Promise<{ access_token: string }> {
  const result = await apiRequest<{ access_token: string }>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
  setAuthToken(result.access_token);
  return result;
}

export async function register(email: string, name: string, password: string): Promise<User> {
  return apiRequest<User>('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ email, name, password }),
  });
}

export async function getCurrentUser(): Promise<User> {
  return apiRequest<User>('/auth/me');
}

// Project endpoints
export async function getProjects(): Promise<Project[]> {
  return apiRequest<Project[]>('/projects/');
}

export async function getProject(id: string): Promise<Project> {
  return apiRequest<Project>(`/projects/${id}`);
}

export async function createProject(data: Omit<Project, 'id'>): Promise<Project> {
  return apiRequest<Project>('/projects/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

// Grid endpoints
export async function estimateCredits(gridSize: number): Promise<CreditEstimate> {
  return apiRequest<CreditEstimate>('/grid/estimate', {
    method: 'POST',
    body: JSON.stringify({ grid_size: gridSize }),
  });
}

export async function generateGridPreview(
  lat: number,
  lng: number,
  radiusKm: number,
  gridSize: number
) {
  return apiRequest<{ points: GridPoint[]; total_points: number; estimated_credits: number }>(
    '/grid/generate',
    {
      method: 'POST',
      body: JSON.stringify({
        lat,
        lng,
        radius_km: radiusKm,
        grid_size: gridSize,
      }),
    }
  );
}

// Search endpoints
export async function executeSearch(projectId: string, gridSize?: number): Promise<ScanResponse> {
  return apiRequest<ScanResponse>('/search/execute', {
    method: 'POST',
    body: JSON.stringify({
      project_id: projectId,
      grid_size: gridSize,
    }),
  });
}

export async function getScanHistory(projectId: string): Promise<ScanResponse[]> {
  return apiRequest<ScanResponse[]>(`/search/history/${projectId}`);
}

export async function getScanDetails(scanId: string): Promise<ScanResponse> {
  return apiRequest<ScanResponse>(`/search/${scanId}`);
}

// Helper to convert backend response to jsonfinal.md format
export function formatScanForMap(scan: ScanResponse): ScanResponse {
  // Map backend status to frontend format
  const grid_data = scan.grid_data?.map((point, idx) => ({
    id: idx + 1,
    lat: point.lat,
    lng: point.lng,
    rank: point.rank,
    status: getStatus(point.rank),
    color: getColor(point.rank),
  })) || [];

  return {
    ...scan,
    grid_data,
  };
}

function getStatus(rank: number | null): 'success' | 'warning' | 'danger' {
  if (rank === null || rank > 10) return 'danger';
  if (rank <= 3) return 'success';
  return 'warning';
}

function getColor(rank: number | null): string {
  if (rank === null || rank > 10) return '#ef4444';
  if (rank <= 3) return '#22c55e';
  return '#eab308';
}
