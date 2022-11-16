import ReactJson from 'react-json-view';
import React from 'react';

function PipelineConfiguration(service: any, show?: boolean) {

    return (
        <div style={{display: show ? "block": "none"}}>
            <ReactJson
                indentWidth={2}
                src={service}
            />
        </div>
    )
}

export default PipelineConfiguration;
