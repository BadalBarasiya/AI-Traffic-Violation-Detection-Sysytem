import './App.css'
import Header from './components/dashboard/Header'
import TrafficViolationUI from './components/TrafficViolationUI'
import { useClock } from './components/hooks/useClock';


function App() {
    const time = useClock();


  return (
    <div className="min-h-screen">
      <Header time={time} />
      <TrafficViolationUI />
    </div>
  )
} 

export default App
