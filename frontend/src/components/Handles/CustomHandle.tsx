import { Handle, HandleType, Position } from 'reactflow';
import { Tooltip } from '@mui/material';
import React from 'react';

const CustomHandle: React.FC<{ id: string, type: HandleType, position: Position, label: string, style: any }> = (
    {
        id,
        type,
        position,
        label,
        style
    }) => {

    return (
        <Tooltip title={label}>
            <Handle type={type} position={position} id={id} style={style}/>
        </Tooltip>
    );
};

export default CustomHandle;
