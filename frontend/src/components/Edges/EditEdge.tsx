import React from 'react';
import {
    BaseEdge,
    EdgeLabelRenderer,
    EdgeProps,
    getBezierPath,
    useReactFlow,
} from 'reactflow';

import {AddCircle, Close as CloseIcon} from "@mui/icons-material";
import {Box, Button, Icon, IconButton, TextField, Typography} from "@mui/material";



export default function CustomEdge({id, sourceX, sourceY, targetX, targetY, sourcePosition, targetPosition, data,
                                       style = {}, markerEnd,}: EdgeProps) {
    const { setEdges } = useReactFlow();

    const [edgePath, labelX, labelY] = getBezierPath({
        sourceX,
        sourceY,
        sourcePosition,
        targetX,
        targetY,
        targetPosition,
    });

    const [isEditing, setIsEditing] = React.useState(false);
    const onEdgeClick = () => {
        setIsEditing(true);
    };


    const handleConditionInput = (value: string) => {
        if (value.length === 0) return;
        setIsEditing(false);
        data.onAddCondition(id, value);
    };

    const edgeLabel = () => {
        return data.condition !== "" ? (
            <Box sx={{ display: "flex", flexDirection: "row", alignItems: "center" }}>
                <Typography variant={"body2"} align={"justify"}>{data.condition}</Typography>
                <IconButton
                    sx={{width: "fit-content", height: "fit-content", transform: "scale(0.5)"}}
                    aria-label={"close"}
                    onClick={() => {
                        data.onDeleteCondition(id)
                    }}
                >
                    <CloseIcon/>
                </IconButton>
            </Box>
        ) : (
            <IconButton size="small" onClick={onEdgeClick}>
                <AddCircle color="primary" fontSize="small"/>
            </IconButton>
        );
    }

    return (
        <>
            <BaseEdge path={edgePath} markerEnd={markerEnd} style={style} />
            <EdgeLabelRenderer>
                <div
                    style={{
                        position: 'absolute',
                        transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
                        fontSize: 12,
                        pointerEvents: 'all',
                    }}
                    className="nodrag nopan"
                >
                    <Box sx={{display: "flex", flexDirection: "column", alignItems: "center"}}>
                        {isEditing ? (
                            <TextField
                                autoFocus
                                size="small"
                                onBlur={(event) => handleConditionInput(event.target.value)}
                            />
                        ) : (
                            edgeLabel()
                        )
                        }
                    </Box>
                </div>
            </EdgeLabelRenderer>
        </>
    );
}
