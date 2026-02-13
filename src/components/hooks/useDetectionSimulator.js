import { useEffect, useState } from 'react';

export function useDetectionSimulator() {
  const [counts, setCounts] = useState({
    detected: 8,
    tracked: 3,
    violations: 1
  });

  useEffect(() => {
    const timer = setInterval(() => {
      setCounts({
        detected: Math.floor(Math.random() * 5) + 6,
        tracked: Math.floor(Math.random() * 3) + 2,
        violations: Math.floor(Math.random() * 2)
      });
    }, 3000);

    return () => clearInterval(timer);
  }, []);

  return counts;
}
