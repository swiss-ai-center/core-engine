import { Tooltip } from '@mui/material';
import React from 'react';
import './styles.css';
import { useSelector } from 'react-redux';
import { Handle, HandleType, Position } from 'reactflow';

const CustomHandle: React.FC<{ id: string, type: HandleType, position: Position, label: string, style: any }> = (
    {
        id,
        type,
        position,
        label,
        style
    }) => {

    const colorMode = useSelector((state: any) => state.colorMode.value);

    return (
        <Tooltip title={label}>
            <Handle type={type} position={position} id={id} style={style} className={"custom-handle"}
                    about={colorMode}/>
        </Tooltip>
    );
};

export default CustomHandle;
