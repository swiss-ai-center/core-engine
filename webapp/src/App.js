import React, { useState } from 'react'
import Menu from './menu/Menu';
import ServicesListing from './servicesListing/ServicesListing'
import Board from './board/Board';
import ScriptEditor from './scriptEditor/ScriptEditor';

export default function App() {


  const [service, setService] = useState({});

  return (
    <div>
      <Menu />
      <div className='section'>
        <div className="columns">
          <ServicesListing service={service} setService={setService} />
          <Board service={service} setService={setService} />
          <ScriptEditor service={service} setService={setService} />
        </div>
      </div>
    </div>
  )
}