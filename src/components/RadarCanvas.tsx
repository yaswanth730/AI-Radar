import React from 'react';
import { motion } from 'framer-motion';

interface RadarCanvasProps {
  sourcesCount: number;
  lastScanText: string;
  signalPoints: number;
}

export const RadarCanvas: React.FC<RadarCanvasProps> = ({
  sourcesCount,
  lastScanText,
  signalPoints,
}) => {
  return (
    <div className="relative w-full max-w-sm mx-auto flex flex-col items-center justify-center p-3 mb-3">
      {/* Radar Circular Visualization */}
      <div className="relative w-40 h-40 sm:w-48 sm:h-48 rounded-full border border-radar-cyan/20 flex items-center justify-center overflow-hidden bg-radar-surface/40 shadow-[0_0_40px_-10px_rgba(0,255,163,0.15)]">
        {/* Concentric distance rings */}
        <div className="absolute w-3/4 h-3/4 rounded-full border border-radar-cyan/15 pointer-events-none" />
        <div className="absolute w-1/2 h-1/2 rounded-full border border-radar-cyan/10 pointer-events-none" />
        <div className="absolute w-1/4 h-1/4 rounded-full border border-radar-cyan/10 pointer-events-none" />
        
        {/* Crosshair grid lines */}
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="w-full h-[1px] bg-radar-cyan/15" />
          <div className="h-full w-[1px] bg-radar-cyan/15 absolute" />
        </div>

        {/* Dynamic sweeping beam */}
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ repeat: Infinity, duration: 4, ease: 'linear' }}
          className="absolute inset-0 origin-center pointer-events-none"
          style={{
            background: 'conic-gradient(from 0deg at 50% 50%, rgba(0, 255, 163, 0.25) 0deg, rgba(0, 255, 163, 0) 60deg)',
          }}
        />

        {/* Center radar origin point */}
        <div className="relative z-10 w-2.5 h-2.5 rounded-full bg-radar-cyan shadow-[0_0_10px_#00FFA3]" />

        {/* Random subtle blips */}
        <motion.div
          animate={{ opacity: [0.2, 1, 0.2] }}
          transition={{ repeat: Infinity, duration: 2.2, ease: 'easeInOut' }}
          className="absolute top-1/4 right-1/3 w-1.5 h-1.5 rounded-full bg-radar-lime shadow-[0_0_8px_#CCFF00]"
        />
        <motion.div
          animate={{ opacity: [0.3, 0.9, 0.3] }}
          transition={{ repeat: Infinity, duration: 3.1, delay: 0.8, ease: 'easeInOut' }}
          className="absolute bottom-1/3 left-1/4 w-1.5 h-1.5 rounded-full bg-radar-cyan shadow-[0_0_8px_#00FFA3]"
        />
      </div>

      {/* Radar Telemetry Metrics */}
      <div className="mt-3 text-center font-mono">
        <div className="text-xs font-bold tracking-widest text-radar-cyan uppercase mb-1">
          RADAR ACTIVE
        </div>
        <div className="flex items-center justify-center gap-4 text-[11px] text-gray-400">
          <span>Sources: <strong className="text-gray-200">{sourcesCount}</strong></span>
          <span>•</span>
          <span>Last scan: <strong className="text-gray-200">{lastScanText}</strong></span>
          <span>•</span>
          <span>Signal points: <strong className="text-radar-lime">{signalPoints}</strong></span>
        </div>
      </div>
    </div>
  );
};
