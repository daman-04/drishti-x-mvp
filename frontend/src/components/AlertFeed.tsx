'use client'

import { useEffect, useRef } from 'react'
import { useStore } from '@/store/useStore'

export default function AlertFeed() {
  const { alerts, addAlert } = useStore()
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    const wsUrl = process.env.NEXT_PUBLIC_API_URL 
      ? process.env.NEXT_PUBLIC_API_URL.replace('http', 'ws') 
      : 'ws://localhost:8000';
      
    wsRef.current = new WebSocket(`${wsUrl}/ws/alerts`)
    
    wsRef.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        addAlert(data)
      } catch (e) {
        console.error("Failed to parse alert", e)
      }
    }

    return () => {
      wsRef.current?.close()
    }
  }, [addAlert])

  return (
    <div className="flex flex-col h-full bg-gray-900 border-l border-gray-800 text-white overflow-hidden">
      <div className="p-4 border-b border-gray-800 flex justify-between items-center bg-gray-900/50 backdrop-blur">
        <h2 className="text-sm font-semibold tracking-wider text-gray-400 uppercase">Threat Intelligence</h2>
        <span className="flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-2 w-2 rounded-full bg-red-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-red-500"></span>
        </span>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {alerts.length === 0 && (
          <div className="text-gray-500 text-sm text-center mt-10">No alerts detected.</div>
        )}
        {alerts.map((alert, idx) => (
          <div 
            key={alert.id || idx} 
            className={`p-3 rounded-lg border bg-gray-800/50 backdrop-blur transition-all ${
              alert.threat_score > 80 ? 'border-red-500/50' : 
              alert.threat_score > 50 ? 'border-yellow-500/50' : 'border-gray-700'
            }`}
          >
            <div className="flex justify-between items-start mb-2">
              <span className={`text-xs font-bold px-2 py-0.5 rounded ${
                alert.threat_score > 80 ? 'bg-red-500/20 text-red-400' : 'bg-yellow-500/20 text-yellow-400'
              }`}>
                {alert.threat_score > 80 ? 'CRITICAL' : 'WARNING'}
              </span>
              <span className="text-xs text-gray-500">
                {new Date(alert.timestamp * 1000).toLocaleTimeString()}
              </span>
            </div>
            
            <h3 className="font-medium text-sm text-gray-200">{alert.event_type}</h3>
            <p className="text-xs text-gray-400 mt-1">{alert.explanation}</p>
            
            <div className="mt-3 flex justify-between items-center text-xs">
              <span className="text-gray-500">Score: <span className="text-white font-mono">{alert.threat_score}</span></span>
              <span className="text-gray-500">Cam: <span className="text-white">{alert.camera_id}</span></span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
