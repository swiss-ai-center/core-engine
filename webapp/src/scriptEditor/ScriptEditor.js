import { useEffect } from 'react';
import ReactJson from 'react-json-view';

export default function ScriptEditor({service, setService, dimensions}) {

  return (
    <div className="column is-3" style={{height: dimensions.height}}>
      <ReactJson
        indentWidth={2}
        collapsed={3}
        src={service}
      />
    </div>
  )
}
