import React, { useState, useEffect } from "react";

export default function ServicesListing({ service, setService }) {

  const [services, setServices] = useState([])

  useEffect(() => {
    fetch("https://pi-engine.kube.isc.heia-fr.ch/services")
      .then((resp) => {
        resp.json().then((value) => {
          console.log(value);
          setServices(value);
        })
      })
      .catch((err) => {
        console.log("Unable to get the services : ", err);
      })
  }, [])

  return (
    <div className="column is-1">
      <div className="buttons">
        {
          services.map(s => <button
            className="button is-small is-info is-fullwidth"
            title={s.nodes[0].api.summary}
            onClick={() => setService(s.nodes)}
            >
              {s.nodes[0].id}
            </button>)
        }
      </div>
    </div>
  );
}