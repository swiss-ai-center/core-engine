import ReactJson from 'react-json-view';
import React from 'react';
import { useSelector } from 'react-redux';

function PipelineConfiguration(description: any, show?: boolean) {
    const colorMode = useSelector((state: any) => state.colorMode.value);
    return (
        <div style={{display: show ? "block": "none"}}>
            <ReactJson
                theme={colorMode === "light" ? "bright:inverted" : "colors"}
                indentWidth={2}
                collapsed={3}
                src={description}
            />
        </div>
    )
}

export default PipelineConfiguration;
