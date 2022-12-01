import ReactJson from 'react-json-view';
import React from 'react';

function PipelineConfiguration(description: any, show?: boolean) {

    return (
        <div style={{display: show ? "block": "none"}}>
            <ReactJson
                indentWidth={2}
                collapsed={3}
                src={description}
            />
        </div>
    )
}

export default PipelineConfiguration;
