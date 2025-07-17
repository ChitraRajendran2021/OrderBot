import { useState } from 'react'
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom'

import './App.css'
import OrderBotUI from './components/OrderBot/OrderBotUI'

function App() {
  const [count, setCount] = useState(0)

  return (
    <Router>
      <Routes>
        <Route path="/order-bot" element={<OrderBotUI />} />
      </Routes>
    </Router>
  )
}

export default App
