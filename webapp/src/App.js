import React, { useState } from 'react'
import Menu from './menu/Menu';
import ServicesListing from './servicesListing/ServicesListing'
import Board from './board/Board';
import ScriptEditor from './scriptEditor/ScriptEditor';
import EngineStatus from './engineStatus/EngineStatus';
import Jobs from './jobs/Jobs';

export default function App() {

  const CONFIGURATION = "CONFIGURATION";
  const ENGINE_STATUS = "ENGINE_STATUS";
  const JOBS = "JOBS";

  const [service, setService] = useState({});
  const [activeTab, setActiveTab] = useState(CONFIGURATION);
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
          <div className="column is-3">
            <div className="tabs is-centered">
              <ul>
                <li className={activeTab === CONFIGURATION ? "is-active" : ""} onClick={() => setActiveTab(CONFIGURATION)}><a>Configuration</a></li>
                <li className={activeTab === ENGINE_STATUS ? "is-active" : ""} onClick={() => setActiveTab(ENGINE_STATUS)}><a>Engine Status</a></li>
                <li className={activeTab === JOBS ? "is-active" : ""} onClick={() => setActiveTab(JOBS)}><a>Jobs</a></li>
              </ul>
            </div>
            <ScriptEditor service={service} setService={setService} dimensions={dimensions} show={activeTab === CONFIGURATION} />
            <EngineStatus show={activeTab === ENGINE_STATUS} />
            <Jobs show={activeTab === JOBS} />

          </div>
        </div>
      </div>
    </div>
  )
}