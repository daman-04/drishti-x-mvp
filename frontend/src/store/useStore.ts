import { create } from 'zustand'

export interface Alert {
  id?: string;
  camera_id: string;
  track_id: string;
  class_name: string;
  threat_score: number;
  event_type: string;
  explanation: string;
  timestamp: number;
}

interface AppState {
  alerts: Alert[];
  addAlert: (alert: Alert) => void;
  xrayMode: boolean;
  toggleXray: () => void;
}

export const useStore = create<AppState>((set) => ({
  alerts: [],
  addAlert: (alert) => set((state) => ({ 
    alerts: [alert, ...state.alerts].slice(0, 50) 
  })),
  xrayMode: false,
  toggleXray: () => set((state) => ({ xrayMode: !state.xrayMode })),
}))
