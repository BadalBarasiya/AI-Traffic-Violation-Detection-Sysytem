import { useEffect, useState } from 'react';
import { VIOLATION_TYPES, LOCATIONS, VEHICLES } from '../data/constants';

export function useViolationSimulator(onNewViolation) {
  const [violations, setViolations] = useState([]);

  useEffect(() => {
    const timer = setInterval(() => {
      const violation = {
        id: `V${Date.now()}`,
        type: VIOLATION_TYPES[Math.floor(Math.random() * VIOLATION_TYPES.length)],
        vehicle: VEHICLES[Math.floor(Math.random() * VEHICLES.length)],
        speed: Math.random() > 0.5 ? `${Math.floor(Math.random() * 30 + 70)} km/h` : '-',
        time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        location: LOCATIONS[Math.floor(Math.random() * LOCATIONS.length)],
        status: 'Pending'
      };

      setViolations(prev => [violation, ...prev]);
      onNewViolation?.();
    }, 8000);

    return () => clearInterval(timer);
  }, [onNewViolation]);

  return { violations };
}
