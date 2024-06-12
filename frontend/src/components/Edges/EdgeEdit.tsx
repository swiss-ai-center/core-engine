import { Add, CancelRounded as CloseIcon } from '@mui/icons-material';
import { Box, Fab, IconButton, Paper, TextField, Tooltip, Typography } from '@mui/material';
import { grey } from '@mui/material/colors';
import React from 'react';
import { useSelector } from 'react-redux';
import { BaseEdge, EdgeLabelRenderer, EdgeProps, getBezierPath, } from 'reactflow';


export default function EdgeEdit({
                                     id, sourceX, sourceY, targetX, targetY, sourcePosition, targetPosition, data,
                                     style = {}, markerEnd,
                                 }: EdgeProps) {
    const [edgePath, labelX, labelY] = getBezierPath({
        sourceX,
        sourceY,
        sourcePosition,
        targetX,
        targetY,
        targetPosition,
    });
    const lightgrey = grey[400];
    const darkgrey = grey[800];
    const colorMode = useSelector((state: any) => state.colorMode.value);

    const [isEditing, setIsEditing] = React.useState(false);

    const onEdgeClick = () => {
        setIsEditing(true);
    };


    const handleConditionInput = (value: string) => {
        console.log(value);
        if (value.length === 0) {
            setIsEditing(false);
            return;
        }
        setIsEditing(false);
        data.onAddCondition(id, value);
    };

    const edgeLabel = () => {
        return data.condition !== "" ? (
            <Box sx={{display: "flex", flexDirection: "row", alignItems: "center"}}>
                <Paper
                    elevation={0}
                    sx={{
                        paddingBlock: 1,
                        paddingLeft: 2,
                        display: "flex",
                        alignItems: "center",
                        borderColor: colorMode === "light" ? lightgrey : darkgrey,
                        borderRadius: 2,
                        borderWidth: 1,
                        borderStyle: "solid",
                    }}>
                    <Typography variant={"body2"} align={"justify"}>{data.condition}</Typography>
                    <Tooltip title={"Delete condition"}>
                        <IconButton
                            sx={{width: "fit-content", height: "fit-content", transform: "scale(0.75)"}}
                            color={"error"}
                            onClick={() => {
                                data.onDeleteCondition(id)
                            }}
                        >
                            <CloseIcon/>
                        </IconButton>
                    </Tooltip>
                </Paper>
            </Box>
        ) : (
            <Tooltip title={"Add condition"}>
                <Fab color={"primary"} aria-label={"delete"} size={"small"} onClick={onEdgeClick}
                     sx={{boxShadow: 0, p: 0}}>
                    <Add/>
                </Fab>
            </Tooltip>
        );
    }

    return (
        <>
            <BaseEdge path={edgePath} markerEnd={markerEnd} style={style}/>
            <EdgeLabelRenderer>
                <div
                    style={{
                        position: 'absolute',
                        transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
                        fontSize: 12,
                        pointerEvents: 'all',
                        borderColor: colorMode === "light" ? lightgrey : darkgrey,
                        borderWidth: isEditing ? 2 : 0,
                        borderStyle: isEditing ? "solid" : "none",
                        borderRadius: 6,
                        zIndex: 10,
                    }}
                    className="nodrag nopan"
                >
                    <Box sx={{display: "flex", flexDirection: "column", alignItems: "center", boxShadow: "none"}}>
                        {isEditing ?
                            (
                                <TextField
                                    autoFocus
                                    sx={{borderRadius: 1, backgroundColor: colorMode === "light" ? "white" : darkgrey}}
                                    variant={"outlined"}
                                    size={"small"}
                                    onBlur={(event) => handleConditionInput(event.target.value)}
                                    onKeyDown={(event) => {
                                        if (event.key === 'Enter') {
                                            handleConditionInput((event.target as HTMLInputElement).value);
                                        }
                                    }}
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
