import { useState, useEffect } from "react"

export default function EngineStatus({ show }) {

  const [engineStatus, setEngineStatus] = useState({})

  useEffect(() => {
    fetch(`${process.env.REACT_APP_ENGINE_URL}/stats`)
      .then((resp) => resp.json().then((value) => {
        setEngineStatus(value);
      })
      )
      .catch((err) => {
        console.log("Unable to get the status of the engine : ", err);
      })
  }, [])

  return (
    <div style={{display: show ? "block": "none"}} >
      <div className="content">

        <dl>
          <dt>Statistics of the engine</dt>
          {Object.keys(engineStatus).length > 0
            ? Object.keys(engineStatus["jobs"]).map((k) => {
                return (<dd>{k.charAt(0).toUpperCase()}{k.slice(1)} : {engineStatus.jobs[k]}</dd>)
              })
            : "No statistics on jobs found"}

          <dt>Statistics per services</dt>
          {Object.keys(engineStatus).length > 0
            ? Object.keys(engineStatus.services).map((k) => {
              return (<dd>{k.charAt(0).toUpperCase()}{k.slice(1)} : {engineStatus.services[k]}</dd>)
            })
            : "No statistics on jobs found"}
        </dl>
      </div>
    </div>
  )

}