import React, { useState, useEffect } from "react";

export default function ServicesListing({ service, setService, dimensions }) {

  const [services, setServices] = useState([])

  useEffect(() => {
    fetch(`${process.env.REACT_APP_ENGINE_URL}/services`)
      .then((resp) => resp.json().then((value) => {
          setServices(value);
        })
      )
      .catch((err) => {
        console.log("Unable to get the services : ", err);
      })
  }, [])

  return (
    <div className="column is-1">
      <h5 className="title is-5">Services</h5>
      <div className="buttons">
        {
          services.map(s => <button
            className="button is-small is-info is-fullwidth"
            title={s.nodes[0].api.summary}
            onClick={() => setService(s)}
          >
            {s.nodes[0].api.route}
          </button>)
        }
      </div>
    </div>
  );
}