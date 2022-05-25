import React, { useState } from 'react'
import './App.css'
import Menu from './menu/Menu';
import ServicesListing from './servicesListing/ServicesListing'
import Board from './board/Board';
import PipelineConfiguration from './PipelineConfiguration/PipelineConfiguration';
import EngineStatus from './engineStatus/EngineStatus';
import Tasks from './tasks/Tasks';

export default function App() {

  const SERVICES = "SERVICES";
  const CONFIGURATION = "CONFIGURATION";
  const ENGINE_STATUS = "ENGINE_STATUS";
  const TASKS = "TASKS";

  const [service, setService] = useState({});
  const [activeTab, setActiveTab] = useState(SERVICES);

  return (
    <div>
      <Menu />
      <div className="columns">
        <div className="column is-3">
          <div className="tabs is-centered">
            <ul>
              <li className={activeTab === SERVICES ? "is-active" : ""} onClick={() => setActiveTab(SERVICES)}><a>Services</a></li>
              <li className={activeTab === CONFIGURATION ? "is-active" : ""} onClick={() => setActiveTab(CONFIGURATION)}><a>Configuration</a></li>
              <li className={activeTab === ENGINE_STATUS ? "is-active" : ""} onClick={() => setActiveTab(ENGINE_STATUS)}><a>Engine Status</a></li>
              <li className={activeTab === TASKS ? "is-active" : ""} onClick={() => setActiveTab(TASKS)}><a>Tasks</a></li>
            </ul>
          </div>
          <div className='content-tab' style={{ height: "70vh" }}>
            <ServicesListing setService={setService} setActiveTab={() => setActiveTab(CONFIGURATION)} show={activeTab === SERVICES} />
            <PipelineConfiguration service={service} show={activeTab === CONFIGURATION} />
            <EngineStatus show={activeTab === ENGINE_STATUS} />
            <Tasks show={activeTab === TASKS} />
          </div>
        </div>
        <Board service={service} />

      </div>
    </div>
  )
}