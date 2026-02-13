import Header from '../components/dashboard/Header';
import { useClock } from '../hooks/useClock';

export default function TrafficDashboard() {
  const time = useClock();
  return (
    <div className="min-h-screen bg-gray-50">
      <Header time={time} />
      <div className="p-6 text-gray-600">Dashboard Content Here</div>
    </div>
  );
}
