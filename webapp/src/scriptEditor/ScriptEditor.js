import { useEffect } from 'react';
import ReactJson from 'react-json-view';

export default function ScriptEditor({ service, setService, dimensions, show }) {

  return (
    <div style={{display: show ? "block": "none"}}>
      <ReactJson
        indentWidth={2}
        collapsed={3}
        src={service}
        style={{ height: dimensions.height }}
      />
    </div>
  )
}
