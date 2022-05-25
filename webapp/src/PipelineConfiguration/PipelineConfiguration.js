import ReactJson from 'react-json-view';

export default function PipelineConfiguration({ service, show }) {

  return (
    <div style={{display: show ? "block": "none"}}>
      <ReactJson
        indentWidth={2}
        collapsed={3}
        src={service}
      />
    </div>
  )
}
