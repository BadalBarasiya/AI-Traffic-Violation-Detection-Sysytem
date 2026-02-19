import { Activity } from 'lucide-react';



export default function Header({ time }) {
  return (
    <div className="bg-blue-700 text-white p-4 flex justify-between">
      <div className="flex gap-2 items-center">
        {/* <Activity /> */}
        <h1 className="font-bold">AI Traffic Dashboard</h1>
      </div>
      <div>{time != null ? time.toLocaleTimeString() : '--'}</div>
    </div>
  );
}
