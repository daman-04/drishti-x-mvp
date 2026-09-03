'use client'

import { useEffect, useRef, useState } from 'react'
import { useStore } from '@/store/useStore'

export default function CameraGrid() {
  const { xrayMode, toggleXray } = useStore()
  const [frameSrc, setFrameSrc] = useState<string>('')
  const [detections, setDetections] = useState<any[]>([])
  const wsRef = useRef<WebSocket | null>(null)
  
  useEffect(() => {
    const wsUrl = process.env.NEXT_PUBLIC_API_URL 
      ? process.env.NEXT_PUBLIC_API_URL.replace('http', 'ws') 
      : 'ws://localhost:8000';
      
    wsRef.current = new WebSocket(`${wsUrl}/ws/stream`)
    
    wsRef.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.frame) {
          setFrameSrc(`data:image/jpeg;base64,${data.frame}`)
        }
        if (data.detections) {
          setDetections(data.detections)
        }
      } catch (e) {
        console.error("Failed to parse stream data", e)
      }
    }

    return () => {
      wsRef.current?.close()
    }
  }, [])

  return (
    <div className="flex flex-col h-full bg-black relative">
      {/* Top Bar */}
      <div className="absolute top-0 left-0 right-0 z-10 p-4 flex justify-between items-center bg-gradient-to-b from-black/80 to-transparent">
        <h1 className="text-xl font-bold text-white tracking-widest uppercase">DRISHTI-X</h1>
        
        <div className="flex items-center space-x-4">
          <button 
            onClick={toggleXray}
            className={`px-3 py-1 rounded text-xs font-bold transition-all ${
              xrayMode ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/50' : 'bg-gray-800 text-gray-400 border border-gray-700'
            }`}
          >
            X-RAY MODE: {xrayMode ? 'ON' : 'OFF'}
          </button>
        </div>
      </div>
      
      {/* Camera Grid (MVP uses single feed to simulate 1 camera for now) */}
      <div className="flex-1 p-4 pt-16 grid grid-cols-1 md:grid-cols-2 gap-4 auto-rows-fr">
        
        {/* Camera 1 Container */}
        <div className="relative rounded-xl overflow-hidden border border-gray-800 bg-gray-900 flex items-center justify-center group">
          
          {/* Video Frame */}
          {frameSrc ? (
            <img 
              src={frameSrc} 
              alt="Cam 1" 
              className="absolute inset-0 w-full h-full object-contain"
            />
          ) : (
            <div className="text-gray-600 animate-pulse font-mono text-sm">CONNECTING STREAM...</div>
          )}
          
          {/* SVG Overlay */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none" preserveAspectRatio="none" viewBox="0 0 640 480">
            {/* Draw dummy geofence for UI visual context based on backend zone_data */}
            <polygon points="300,200 600,200 600,500 300,500" fill="rgba(255,0,0,0.1)" stroke="red" strokeWidth="2" strokeDasharray="5,5" />
            <line x1="100" y1="100" x2="700" y2="700" stroke="yellow" strokeWidth="2" strokeDasharray="10,5" />
            
            {/* Draw bounding boxes */}
            {detections.map((det, i) => {
              // Hide low threat if not in xray mode
              if (!xrayMode && (!det.threat_score || det.threat_score <= 50)) return null;
              
              const [x1, y1, x2, y2] = det.bbox
              const isHighThreat = det.threat_score > 80
              const color = isHighThreat ? '#ef4444' : (det.threat_score > 50 ? '#eab308' : '#3b82f6')
              
              return (
                <g key={i}>
                  <rect 
                    x={x1} y={y1} width={x2 - x1} height={y2 - y1} 
                    fill="none" 
                    stroke={color} 
                    strokeWidth="2"
                  />
                  <rect x={x1} y={y1 - 20} width={100} height={20} fill={color} />
                  <text x={x1 + 4} y={y1 - 5} fill="white" fontSize="12" fontWeight="bold" fontFamily="monospace">
                    {det.class_name} ({Math.round(det.threat_score || 0)})
                  </text>
                  
                  {/* Motion Vector (simple line from center pointing right for visual effect, ideally we'd send velocity from backend) */}
                  {det.threat_score > 50 && (
                     <line 
                      x1={(x1+x2)/2} y1={(y1+y2)/2} 
                      x2={(x1+x2)/2 + 40} y2={(y1+y2)/2} 
                      stroke={color} strokeWidth="2" markerEnd="url(#arrow)" 
                    />
                  )}
                </g>
              )
            })}
            <defs>
              <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="context-stroke" />
              </marker>
            </defs>
          </svg>
          
          {/* Camera Info Overlay */}
          <div className="absolute bottom-4 left-4 bg-black/60 backdrop-blur px-3 py-1 rounded text-xs text-white font-mono border border-white/10">
            CAM 01: MAIN GATE
          </div>
        </div>

        {/* Dummy blank cameras for UI completeness */}
        <div className="rounded-xl overflow-hidden border border-gray-900 bg-gray-950 flex items-center justify-center">
            <span className="text-gray-800 font-mono text-xs">OFFLINE</span>
        </div>
        <div className="rounded-xl overflow-hidden border border-gray-900 bg-gray-950 flex items-center justify-center">
            <span className="text-gray-800 font-mono text-xs">OFFLINE</span>
        </div>
        <div className="rounded-xl overflow-hidden border border-gray-900 bg-gray-950 flex items-center justify-center">
            <span className="text-gray-800 font-mono text-xs">OFFLINE</span>
        </div>

      </div>
    </div>
  )
}
