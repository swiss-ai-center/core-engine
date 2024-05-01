import React from "react";
import { NodeProps, Position } from "reactflow";
import { Box, Button, Card, CardActions, CardContent, Link as URLLink, Tooltip, Typography } from '@mui/material';
import { DownloadForOfflineTwoTone, ErrorTwoTone } from '@mui/icons-material';
import { RunState } from '../../utils/reducers/runStateSlice';
import { useSelector } from 'react-redux';
import { grey } from '@mui/material/colors';
import { displayTimer, download, positionHandle } from '../../utils/functions';
import "./styles.css";
import { ProgressNodeData } from '../../models/NodeData';
import CustomHandle from './CustomHandle';


const ProgressNode = ({data}: NodeProps<ProgressNodeData>) => {
    const lightgrey = grey[400];
    const mediumgrey = grey[500];
    const darkgrey = grey[800];
    const colorMode = useSelector((state: any) => state.colorMode.value);
    const currentTask = useSelector((state: any) => state.runState.task);
    const taskArray = useSelector((state: any) => state.runState.taskArray);
    const timer = useSelector((state: any) => state.runState.timer);
    const [selfTimer, setSelfTimer] = React.useState(0.0);

    const getStatus = () => {
        if (currentTask && currentTask.service_id === data.service_id) {
            return currentTask.status;
        } else {
            const tasks = taskArray.filter((task: any) => task.service_id === data.service_id);
            if (tasks.length > 0) {
                return tasks[0].status;
            }
            return RunState.IDLE;
        }
    }

    const isExecuting = () => {
        return (getStatus() === RunState.PENDING ||
            getStatus() === RunState.PROCESSING ||
            getStatus() === RunState.SAVING ||
            getStatus() === RunState.FETCHING);
    }

    const downloadIntermediateResult = async () => {
        const resultIdList = taskArray.filter((task: any) => task.service_id === data.service_id)[0].data_out;
        await download(resultIdList);
    }

    // Timer increments when the task is being executed and then fixed to last value after execution
    React.useEffect(() => {
        if (isExecuting()) {
            setSelfTimer(selfTimer + 0.1);
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [timer]);

    React.useEffect(() => {
        if (timer === 0.0) {
            setSelfTimer(0.0);
        }
    }, [timer]);

    return (
        <>
            <Card
                sx={{
                    height: "100%", display: "flex", flexDirection: "column",
                    border: !isExecuting() ? ("2px solid") : "none", alignItems: "left",
                    borderColor: !isExecuting() ? (
                        getStatus() === RunState.FINISHED ? "success.main" :
                            getStatus() === RunState.ERROR ? "error.main" :
                                getStatus() === RunState.SKIPPED ? "warning.main" :
                                    (colorMode === "light" ? lightgrey : darkgrey)
                    ) : "none",
                    borderRadius: 2,
                    boxShadow: "none",
                }}
                className={isExecuting() ? "rotating-border" : ""}
            >
                <Box className={"timer timer-step"} zIndex={99} marginBottom={1}>
                    <Typography variant={"caption"} color={colorMode === 'dark' ? lightgrey : mediumgrey}>
                        {displayTimer(selfTimer)}
                    </Typography>
                </Box>
                <CardContent sx={{flexGrow: 1, width: "100%"}}>
                    {data.type === "pipeline" ? (
                        <URLLink href={`/showcase/service/${data.service_slug}`} sx={{textDecoration: "none"}}>
                            <Tooltip title={"Service's page"} placement={"top"}>
                                <Typography variant={"subtitle1"} color={"primary"}
                                            sx={{justifyContent: "center", display: "flex"}}
                                >
                                    {data.label}
                                </Typography>
                            </Tooltip>
                        </URLLink>
                    ) : (
                        <Typography variant={"subtitle1"} color={"primary"}
                                    sx={{justifyContent: "center", display: "flex"}}
                        >
                            {data.label}
                        </Typography>
                    )}
                </CardContent>
                <CardActions
                    // if type is service, hide download button
                    sx={{display: data.type === "service" ? "none" : "flex", width: "100%", justifyContent: "center"}}
                >
                    {getStatus() === RunState.SKIPPED ? (
                        <Tooltip title={"Step was skipped"} placement={"bottom"}>
                        <span>
                            <Button
                                disabled={getStatus() !== RunState.FINISHED}
                                sx={{
                                    display: "flex",
                                    width: "100%",
                                    minHeight: 32,
                                }}
                                variant={"outlined"}
                                color={"success"}
                                size={"small"}
                                endIcon={<ErrorTwoTone/>}
                            >
                                Skipped
                            </Button>
                        </span>
                        </Tooltip>) : (
                        <Tooltip title={"Download intermediate result"} placement={"bottom"}>
                            <span>
                                <Button
                                    disabled={getStatus() !== RunState.FINISHED}
                                    sx={{
                                        display: "flex",
                                        width: "100%",
                                        minHeight: 32,
                                    }}
                                    variant={"outlined"}
                                    color={"success"}
                                    size={"small"}
                                    endIcon={<DownloadForOfflineTwoTone/>}
                                    onClick={downloadIntermediateResult}
                                >
                                    Download
                                </Button>
                            </span>
                        </Tooltip>
                    )}
                </CardActions>
            </Card>
            <div className="handles targets">
                {data.targetHandles.map((handle, index) => {
                    return (
                        <CustomHandle
                            key={index}
                            id={handle.id}
                            label={handle.label}
                            type={"target"}
                            style={{top: positionHandle(data.targetHandles.length, index + 1)}}
                            position={Position.Left}
                        />
                    );
                })}
            </div>
            <div className="handles sources">
                {data.sourceHandles.map((handle, index) => {
                    return (
                        <CustomHandle
                            key={index}
                            id={handle.id}
                            label={handle.label}
                            type={"source"}
                            style={{top: positionHandle(data.sourceHandles.length, index + 1)}}
                            position={Position.Right}
                        />
                    );
                })}
            </div>
        </>
    );
};

export default ProgressNode;
