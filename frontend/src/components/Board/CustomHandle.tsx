import { Handle, HandleType, Position } from 'reactflow';
import { Tooltip } from '@mui/material';

const CustomHandle: React.FC<{ id: string, type: HandleType, position: Position, label: string }> = (
    {
        id,
        type,
        position,
        label
    }) => {

    return (
        <Tooltip title={label}>
            <Handle type={type} position={position} id={id}/>
        </Tooltip>
    );
};

export default CustomHandle;
