// import React, { useState, useEffect } from "react";
// import {
//   Camera,
//   AlertTriangle,
//   Car,
//   Clock,
//   MapPin,
//   FileText,
//   Activity,
//   TrendingUp,
//   Bell,
// } from "lucide-react";

// export default function TrafficViolationUI() {
//   const violations = useViolationsSocket();

//   const [activeTab, setActiveTab] = useState("live");
//   const [currentTime, setCurrentTime] = useState(new Date());
//   const [violations, setViolations] = useState([
//     {
//       id: "V001",
//       type: "Triple riding",
//       vehicle: "GJ-01-AB-1234",
//       time: "10:45 AM",
//       location: "SG Highway",
//       status: "Pending",
//     },
//     {
//       id: "V002",
//       type: "Red Light",
//       vehicle: "GJ-05-CD-5678",
//       time: "10:42 AM",
//       location: "CG Road",
//       status: "Processed",
//     },
//     {
//       id: "V003",
//       type: "No Helmet",
//       vehicle: "GJ-27-EF-9012",
//       time: "10:40 AM",
//       location: "Ashram Road",
//       status: "Pending",
//     },
//     {
//       id: "V004",
//       type: "Lane violation",
//       vehicle: "GJ-18-GH-3456",
//       time: "10:38 AM",
//       location: "Ring Road",
//       status: "Pending",
//     },
//   ]);

//   const [stats, setStats] = useState({
//     totalViolations: 47,
//     activeCameras: 12,
//     vehiclesMonitored: 2348,
//     finesGenerated: 94000,
//   });

//   const [detectionCounts, setDetectionCounts] = useState({
//     detected: 8,
//     tracked: 3,
//     violations: 1,
//   });

//   const [newViolationAlert, setNewViolationAlert] = useState(false);

//   // Update current time every second
//   useEffect(() => {
//     const timer = setInterval(() => {
//       setCurrentTime(new Date());
//     }, 1000);
//     return () => clearInterval(timer);
//   }, []);

//   // Simulate real-time violation detection
//   useEffect(() => {
//     const violationTimer = setInterval(() => {
//       const violationTypes = [
//         "Speed Violation",
//         "Red Light",
//         "No Helmet",
//         "Wrong Way",
//         "No Parking",
//       ];
//       const locations = [
//         "SG Highway",
//         "CG Road",
//         "Ashram Road",
//         "Ring Road",
//         "Paldi",
//         "Satellite",
//       ];
//       const vehicleNumbers = [
//         "GJ-01-AB-" + Math.floor(Math.random() * 9000 + 1000),
//         "GJ-05-CD-" + Math.floor(Math.random() * 9000 + 1000),
//         "GJ-27-EF-" + Math.floor(Math.random() * 9000 + 1000),
//       ];

//       const newViolation = {
//         id: "V" + String(violations.length + 1).padStart(3, "0"),
//         type: violationTypes[Math.floor(Math.random() * violationTypes.length)],
//         vehicle:
//           vehicleNumbers[Math.floor(Math.random() * vehicleNumbers.length)],
//         speed:
//           Math.random() > 0.5
//             ? Math.floor(Math.random() * 30) + 70 + " km/h"
//             : "-",
//         time: currentTime.toLocaleTimeString("en-US", {
//           hour: "2-digit",
//           minute: "2-digit",
//         }),
//         location: locations[Math.floor(Math.random() * locations.length)],
//         status: "Pending",
//       };

//       setViolations((prev) => [newViolation, ...prev]);
//       setStats((prev) => ({
//         ...prev,
//         totalViolations: prev.totalViolations + 1,
//         finesGenerated: prev.finesGenerated + 2000,
//       }));

//       // Show notification
//       setNewViolationAlert(true);
//       setTimeout(() => setNewViolationAlert(false), 3000);
//     }, 8000); // Add new violation every 8 seconds

//     return () => clearInterval(violationTimer);
//   }, [violations.length, currentTime]);

//   // Simulate vehicle detection changes
//   useEffect(() => {
//     const detectionTimer = setInterval(() => {
//       setDetectionCounts({
//         detected: Math.floor(Math.random() * 5) + 6,
//         tracked: Math.floor(Math.random() * 3) + 2,
//         violations: Math.floor(Math.random() * 2),
//       });
//     }, 3000);

//     return () => clearInterval(detectionTimer);
//   }, []);

//   // Simulate vehicles monitored increase
//   useEffect(() => {
//     const monitorTimer = setInterval(() => {
//       setStats((prev) => ({
//         ...prev,
//         vehiclesMonitored:
//           prev.vehiclesMonitored + Math.floor(Math.random() * 3),
//       }));
//     }, 5000);

//     return () => clearInterval(monitorTimer);
//   }, []);

//   const statsData = [
//     {
//       label: "Total Violations Today",
//       value: stats.totalViolations,
//       icon: AlertTriangle,
//       color: "bg-red-500",
//     },
//     {
//       label: " Manual Camera feed",
//       value: stats.activeCameras,
//       icon: Camera,
//       color: "bg-blue-500",
//     },
//     {
//       label: "Vehicles Monitored",
//       value: stats.vehiclesMonitored.toLocaleString(),
//       icon: Car,
//       color: "bg-green-500",
//     },
//     {
//       label: "Fines Generated",
//       value: "₹" + stats.finesGenerated.toLocaleString(),
//       icon: TrendingUp,
//       color: "bg-yellow-500",
//     },
//   ];

//   return (
//     <div className="min-h-screen bg-gray-50">
//       {/* New Violation Alert */}
//       {newViolationAlert && (
//         <div className="fixed top-4 right-4 z-50 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg flex items-center gap-3 animate-pulse">
//           <Bell className="w-5 h-5" />
//           <span className="font-semibold">New Violation Detected!</span>
//         </div>
//       )}

//       {/* Header */}
//       <div className="bg-linear-to-r from-blue-600 to-blue-800 text-white p-6 shadow-lg">
//         <div className="max-w-7xl mx-auto">
//           <div className="flex items-center justify-between">
//             <div className="flex items-center gap-3">
//               <Activity className="w-8 h-8" />
//               <div>
//                 <h1 className="text-2xl font-bold">
//                   AI Traffic Violation Detection System
//                 </h1>
//                 <p className="text-blue-100 text-sm">
//                   Real-time Traffic Monitoring Dashboard
//                 </p>
//               </div>
//             </div>
//             <div className="text-right">
//               <div className="text-sm text-blue-100">Current Time</div>
//               <div className="text-xl font-semibold">
//                 {currentTime.toLocaleTimeString("en-US", {
//                   hour: "2-digit",
//                   minute: "2-digit",
//                   second: "2-digit",
//                 })}
//               </div>
//             </div>
//           </div>
//         </div>
//       </div>

//       <div className="max-w-7xl mx-auto p-6">
//         {/* Statistics Cards */}
//         <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
//           {statsData.map((stat, idx) => (
//             <div
//               key={idx}
//               className="bg-white rounded-lg shadow p-5 transform transition-all hover:scale-105"
//             >
//               <div className="flex items-center justify-between mb-2">
//                 <div className={`${stat.color} p-3 rounded-lg`}>
//                   <stat.icon className="w-6 h-6 text-white" />
//                 </div>
//               </div>
//               <div className="text-2xl font-bold text-gray-800">
//                 {stat.value}
//               </div>
//               <div className="text-sm text-gray-500">{stat.label}</div>
//             </div>
//           ))}
//         </div>

//         {/* Main Content Area */}
//         <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
//           {/* Live Camera Feed */}
//           <div className="lg:col-span-2 bg-white rounded-lg shadow">
//             <div className="p-4 border-b border-gray-200">
//               <div className="flex items-center justify-between">
//                 <h2 className="text-lg font-semibold flex items-center gap-2">
//                   <Camera className="w-5 h-5 text-blue-600" />
//                   Live Camera Feed
//                 </h2>
//                 <div className="flex gap-2">
//                   <button
//                     onClick={() => setActiveTab("live")}
//                     className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
//                       activeTab === "live"
//                         ? "bg-blue-600 text-white"
//                         : "bg-gray-100 text-gray-600 hover:bg-gray-200"
//                     }`}
//                   >
//                     Live Feed
//                   </button>
//                   <button
//                     onClick={() => setActiveTab("detected")}
//                     className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
//                       activeTab === "detected"
//                         ? "bg-blue-600 text-white"
//                         : "bg-gray-100 text-gray-600 hover:bg-gray-200"
//                     }`}
//                   >
//                     Detected
//                   </button>
//                 </div>
//               </div>
//             </div>
//             <div className="p-4">
//               {activeTab === "live" ? (
//                 <div className="bg-gray-900 rounded-lg aspect-video flex items-center justify-center relative overflow-hidden">
//                   <div className="absolute inset-0 bg-linear-to-br from-blue-900/20 to-purple-900/20"></div>
//                   <div className="relative z-10 text-center">
//                     <Camera className="w-16 h-16 text-gray-600 mx-auto mb-3" />
//                     <p className="text-gray-400">
//                       Camera Feed: SG Highway Junction
//                     </p>
//                     <div className="mt-3 flex items-center justify-center gap-2">
//                       <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
//                       <span className="text-sm text-gray-400">Recording</span>
//                     </div>
//                   </div>
//                   {/* Animated detection boxes */}
//                   <div className="absolute top-20 left-12 w-32 h-24 border-2 border-green-500 rounded animate-pulse"></div>
//                   <div className="absolute top-32 right-16 w-28 h-20 border-2 border-green-500 rounded animate-pulse"></div>
//                   <div className="absolute bottom-24 left-24 w-36 h-28 border-2 border-red-500 rounded animate-pulse">
//                     <div className="bg-red-500 text-white text-xs px-2 py-1 absolute -top-6 left-0 animate-bounce">
//                       Triple Riding{" "}
//                     </div>
//                   </div>
//                 </div>
//               ) : (
//                 <div className="bg-gray-100 rounded-lg aspect-video flex items-center justify-center">
//                   <div className="text-center">
//                     <AlertTriangle className="w-16 h-16 text-red-500 mx-auto mb-3 animate-pulse" />
//                     <p className="text-gray-600 font-medium">
//                       Last Detected Violation
//                     </p>
//                     <p className="text-sm text-gray-500 mt-2">
//                       {violations[0]?.type} - {violations[0]?.vehicle}
//                     </p>
//                     <p className="text-xs text-gray-400 mt-1">
//                       {violations[0]?.time} - {violations[0]?.location}
//                     </p>
//                   </div>
//                 </div>
//               )}

//               {/* Detection Info - Dynamic */}
//               <div className="mt-4 grid grid-cols-3 gap-3">
//                 <div className="bg-green-50 p-3 rounded-lg transition-all">
//                   <div className="text-xs text-green-600 font-medium">
//                     Vehicles Detected
//                   </div>
//                   <div className="text-xl font-bold text-green-700">
//                     {detectionCounts.detected}
//                   </div>
//                 </div>
//                 <div className="bg-yellow-50 p-3 rounded-lg transition-all">
//                   <div className="text-xs text-yellow-600 font-medium">
//                     Being Tracked
//                   </div>
//                   <div className="text-xl font-bold text-yellow-700">
//                     {detectionCounts.tracked}
//                   </div>
//                 </div>
//                 <div className="bg-red-50 p-3 rounded-lg transition-all">
//                   <div className="text-xs text-red-600 font-medium">
//                     Violations
//                   </div>
//                   <div className="text-xl font-bold text-red-700">
//                     {detectionCounts.violations}
//                   </div>
//                 </div>
//               </div>
//             </div>
//           </div>

//           {/* Recent Violations */}
//           <div className="bg-white rounded-lg shadow">
//             <div className="p-4 border-b border-gray-200">
//               <h2 className="text-lg font-semibold flex items-center gap-2">
//                 <FileText className="w-5 h-5 text-blue-600" />
//                 Recent Violations
//                 <span className="ml-auto text-xs bg-red-500 text-white px-2 py-1 rounded-full">
//                   {violations.filter((v) => v.status === "Pending").length} New
//                 </span>
//               </h2>
//             </div>
//             <div className="p-4 space-y-3 max-h-96 overflow-y-auto">
//               {violations.slice(0, 6).map((violation, index) => (
//                 <div
//                   key={violation.id}
//                   className={`border border-gray-200 rounded-lg p-3 hover:bg-gray-50 transition-all ${
//                     index === 0 ? "animate-pulse bg-red-50" : ""
//                   }`}
//                 >
//                   <div className="flex items-start justify-between mb-2">
//                     <div className="flex items-center gap-2">
//                       <AlertTriangle className="w-4 h-4 text-red-500" />
//                       <span className="text-sm font-semibold text-gray-800">
//                         {violation.type}
//                       </span>
//                     </div>
//                     <span
//                       className={`text-xs px-2 py-1 rounded-full ${
//                         violation.status === "Pending"
//                           ? "bg-yellow-100 text-yellow-700"
//                           : "bg-green-100 text-green-700"
//                       }`}
//                     >
//                       {violation.status}
//                     </span>
//                   </div>
//                   <div className="space-y-1 text-xs text-gray-600">
//                     <div className="flex items-center gap-1">
//                       <Car className="w-3 h-3" />
//                       <span>{violation.vehicle}</span>
//                     </div>
//                     <div className="flex items-center gap-1">
//                       <Clock className="w-3 h-3" />
//                       <span>{violation.time}</span>
//                     </div>
//                     <div className="flex items-center gap-1">
//                       <MapPin className="w-3 h-3" />
//                       <span>{violation.location}</span>
//                     </div>
//                   </div>
//                   <button className="mt-2 w-full bg-blue-50 text-blue-600 text-xs py-1 rounded hover:bg-blue-100 transition-colors">
//                     View Details
//                   </button>
//                 </div>
//               ))}
//             </div>
//           </div>
//         </div>

//         {/* Violations Table */}
//         <div className="mt-6 bg-white rounded-lg shadow">
//           <div className="p-4 border-b border-gray-200">
//             <h2 className="text-lg font-semibold">All Violations Today</h2>
//           </div>
//           <div className="overflow-x-auto">
//             <table className="w-full">
//               <thead className="bg-gray-50">
//                 <tr>
//                   <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
//                     ID
//                   </th>
//                   <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
//                     Type
//                   </th>
//                   <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
//                     Vehicle
//                   </th>
//                   <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase"></th>
//                   <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
//                     Time
//                   </th>
//                   <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
//                     Location
//                   </th>
//                   <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
//                     Status
//                   </th>
//                   <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
//                     Action
//                   </th>
//                 </tr>
//               </thead>
//               <tbody className="divide-y divide-gray-200">
//                 {violations.map((violation, index) => (
//                   <tr
//                     key={violation.id}
//                     className={`hover:bg-gray-50 transition-colors ${
//                       index === 0 ? "bg-yellow-50" : ""
//                     }`}
//                   >
//                     <td className="px-4 py-3 text-sm text-gray-900">
//                       {violation.id}
//                     </td>
//                     <td className="px-4 py-3 text-sm text-gray-900">
//                       {violation.type}
//                     </td>
//                     <td className="px-4 py-3 text-sm font-medium text-gray-900">
//                       {violation.vehicle}
//                     </td>
//                     <td className="px-4 py-3 text-sm text-gray-600">
//                       {violation.speed}
//                     </td>
//                     <td className="px-4 py-3 text-sm text-gray-600">
//                       {violation.time}
//                     </td>
//                     <td className="px-4 py-3 text-sm text-gray-600">
//                       {violation.location}
//                     </td>
//                     <td className="px-4 py-3 text-sm">
//                       <span
//                         className={`px-2 py-1 rounded-full text-xs ${
//                           violation.status === "Pending"
//                             ? "bg-yellow-100 text-yellow-700"
//                             : "bg-green-100 text-green-700"
//                         }`}
//                       >
//                         {violation.status}
//                       </span>
//                     </td>
//                     <td className="px-4 py-3 text-sm">
//                       <button className="text-blue-600 hover:text-blue-800 font-medium">
//                         View
//                       </button>
//                     </td>
//                   </tr>
//                 ))}
//               </tbody>
//             </table>
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// }
import React, { useState, useEffect } from "react";
import {
  Camera,
  AlertTriangle,
  Car,
  Clock,
  MapPin,
  FileText,
  Activity,
  TrendingUp,
  Bell,
} from "lucide-react";
import { useViolationsSocket } from "../hooks/useViolationsSocket";

export default function TrafficViolationUI() {
  const violations = useViolationsSocket();

  const [currentTime, setCurrentTime] = useState(new Date());
  const [newViolationAlert, setNewViolationAlert] = useState(false);

  const [stats, setStats] = useState({
    totalViolations: 0,
    activeCameras: 1,
    vehiclesMonitored: 0,
    finesGenerated: 0,
  });

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    if (violations.length > 0) {
      setStats(prev => ({
        ...prev,
        totalViolations: violations.length,
        finesGenerated: violations.length * 1000
      }));

      setNewViolationAlert(true);
      setTimeout(() => setNewViolationAlert(false), 3000);
    }
  }, [violations]);

  return (
    <div className="min-h-screen bg-gray-50">

      {newViolationAlert && (
        <div className="fixed top-4 right-4 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg">
          <Bell className="w-5 h-5 inline mr-2" />
          New Violation Detected!
        </div>
      )}

      <div className="bg-blue-700 text-white p-6">
        <h1 className="text-2xl font-bold">
          AI Traffic Violation Detection System
        </h1>
        <p>{currentTime.toLocaleTimeString()}</p>
      </div>

      <div className="p-6">

        <div className="grid grid-cols-4 gap-4 mb-6">
          <StatCard icon={AlertTriangle} value={stats.totalViolations} label="Total Violations" />
          <StatCard icon={Camera} value={stats.activeCameras} label="Active Cameras" />
          <StatCard icon={Car} value={stats.vehiclesMonitored} label="Vehicles Monitored" />
          <StatCard icon={TrendingUp} value={`₹${stats.finesGenerated}`} label="Fines Generated" />
        </div>

        <div className="bg-white rounded shadow p-4">
          <h2 className="text-lg font-semibold mb-4">Recent Violations</h2>

          {violations.map(v => (
            <div key={v.id} className="border-b py-2">
              <div className="font-semibold">{v.type}</div>
              <div className="text-sm text-gray-600">
                {v.vehicle} • {v.time} • {v.location}
              </div>
            </div>
          ))}
        </div>

      </div>
    </div>
  );
}

function StatCard({ icon: Icon, value, label }) {
  return (
    <div className="bg-white p-4 rounded shadow">
      <Icon className="w-6 h-6 mb-2 text-blue-600" />
      <div className="text-xl font-bold">{value}</div>
      <div className="text-sm text-gray-500">{label}</div>
    </div>
  );
}

