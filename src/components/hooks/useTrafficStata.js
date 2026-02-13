import { useState } from 'react';

export function useTrafficStats() {
  const [stats, setStats] = useState({
    totalViolations: 47,
    activeCameras: 12,
    vehiclesMonitored: 2348,
    finesGenerated: 94000
  });

  const incrementViolation = () => {
    setStats(prev => ({
      ...prev,
      totalViolations: prev.totalViolations + 1,
      finesGenerated: prev.finesGenerated + 2000
    }));
  };

  const incrementVehicles = (count = 1) => {
    setStats(prev => ({
      ...prev,
      vehiclesMonitored: prev.vehiclesMonitored + count
    }));
  };

  return { stats, incrementViolation, incrementVehicles };
}
