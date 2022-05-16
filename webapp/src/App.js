import React, { useState } from 'react'
import Menu from './menu/Menu';
import ServicesListing from './servicesListing/ServicesListing'
import Board from './board/Board';
import ScriptEditor from './scriptEditor/ScriptEditor';

export default function App() {

  const [service, setService] = useState({});
  const [dimensions, setDimensions] = useState({
    height: window.innerHeight,
    width: window.innerWidth
  })

  window.onresize = () => setDimensions({
    height: window.innerHeight,
    width: window.innerWidth
  });

  return (
    <div>
      <Menu />
      <div className='section'>
        <div className="columns">
          <ServicesListing service={service} setService={setService} dimensions={dimensions} />
          <Board service={service} setService={setService} dimensions={dimensions} />
          <ScriptEditor service={service} setService={setService} dimensions={dimensions} />
        </div>
      </div>
    </div>
  )
}