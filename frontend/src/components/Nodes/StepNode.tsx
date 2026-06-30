import { DownloadForOfflineTwoTone, ErrorTwoTone, NotificationsPausedTwoTone } from '@mui/icons-material';
import { Box, Button, Card, CardActions, CardContent, Link as URLLink, Tooltip, Typography } from '@mui/material';
import { grey } from '@mui/material/colors';
import { ProgressNodeData } from 'models/NodeData';
import React from "react";
import { useSelector } from 'react-redux';
import { NodeProps, Position, useReactFlow } from "reactflow";
import { displayTimer, download, positionHandle } from 'utils/functions';
import "components/Board/styles.css";
import { RunState } from 'utils/reducers/runStateSlice';
import CustomHandle from 'components/Handles/CustomHandle';
import { wakeUp } from 'utils/api';
import { ServiceStatus } from '../../enums/serviceStatusEnum';
import { toast } from 'react-toastify';


const StepNode = ({data}: NodeProps<ProgressNodeData>) => {
    const lightgrey = grey[400];
    const mediumgrey = grey[500];
    const darkgrey = grey[800];
    const colorMode = useSelector((state: any) => state.colorMode.value);
    const currentTask = useSelector((state: any) => state.runState.task);
    const taskArray = useSelector((state: any) => state.runState.taskArray);
    const timer = useSelector((state: any) => state.runState.timer);
    const {setNodes} = useReactFlow();
    const [selfTimer, setSelfTimer] = React.useState(0.0);
    const [sleeping, setSleeping] = React.useState(false);
    const [serviceStatus, setServiceStatus] = React.useState<ServiceStatus>(data.status);
    const groupedServiceIds = data.service_ids ?? [data.service_id];

    const refreshNodeStatus = React.useCallback((nextStatus: ServiceStatus) => {
        setNodes((nodes: any[]) => nodes.map((node: any) => {
            if (node.id === data.label) {
                return {
                    ...node,
                    data: {
                        ...node.data,
                        status: nextStatus,
                    },
                };
            }

            if (data.type === "service" && node.id === `${data.label}-entry`) {
                return {
                    ...node,
                    data: {
                        ...node.data,
                        status: nextStatus,
                    },
                };
            }

            return node;
        }));
    }, [data.label, data.type, setNodes]);

    const getStatus = () => {
        if (data.type === "subpipeline") {
            // Pair tasks to this group's steps by pipeline_step_id (stable, unique per step),
            // falling back to service_id for tasks that predate that column. We can't use list
            // position: taskArray (execution response) and the rendered steps come from separate
            // requests whose orderings are not guaranteed to match.
            const groupedStepIdSet = new Set(data.step_ids ?? []);
            const groupedServiceIdSet = new Set(groupedServiceIds);
            const taskInGroup = (task: any) => task?.pipeline_step_id
                ? groupedStepIdSet.has(task.pipeline_step_id)
                : groupedServiceIdSet.has(task?.service_id);

            if (currentTask && taskInGroup(currentTask)) return currentTask.status;

            const groupedTasks = taskArray.filter(taskInGroup);
            const priority = [RunState.PROCESSING, RunState.PENDING, RunState.SAVING, RunState.FETCHING, RunState.ERROR, RunState.SKIPPED];
            for (const status of priority) {
                if (groupedTasks.some((task: any) => task.status === status)) return status;
            }
            if (groupedTasks.length > 0 && groupedTasks.every((task: any) => task.status === RunState.FINISHED)) {
                return RunState.FINISHED;
            }
            return RunState.IDLE;
        }

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
        if (data.type === "subpipeline") {
            const resultIdList = data.sourceHandles.flatMap((handle) => {
                const outputSource = data.output_sources?.[handle.id];
                if (!outputSource) return [];
                const task = taskArray.find((t: any) => t.pipeline_step_id
                    ? t.pipeline_step_id === outputSource.stepId
                    : t.service_id === outputSource.serviceId);
                const fileKey = task?.data_out?.[outputSource.outputIndex];
                return fileKey ? [fileKey] : [];
            });

            if (resultIdList.length === 0) {
                toast("No sub-pipeline output available to download", {type: "warning"});
                return;
            }

            await download(resultIdList);
            return;
        }

        const resultIdList = taskArray.filter((task: any) => task.service_id === data.service_id)[0].data_out;
        await download(resultIdList);
    }

    const wakeUpService = async () => {
        try {
            toast(data.type === "subpipeline" ? "Sending wake up requests..." : "Sending wake up request...", {type: "info"});
            setSleeping(true);

            const responses = await Promise.all(Array.from(new Set(groupedServiceIds)).map((serviceId) => wakeUp(serviceId)));
            const successCount = responses.filter((response: any) => response.status === 204).length;
            const failCount = responses.length - successCount;

            if (failCount === 0) {
                toast(
                    data.type === "subpipeline"
                        ? `All ${successCount} services woken up successfully`
                        : responses[0].message,
                    {type: "success"}
                );
                setServiceStatus(ServiceStatus.AVAILABLE);
                refreshNodeStatus(ServiceStatus.AVAILABLE);
            } else if (successCount === 0) {
                toast("Failed to wake up service(s)", {type: "error"});
            } else {
                toast(`${successCount} services woken up, ${failCount} failed`, {type: "warning"});
            }
        } catch (e: any) {
            toast("Error while sending wake up request: " + e.message, {type: "error"});
        } finally {
            setSleeping(false);
        }
    };

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
                    {data.type === "pipeline" || data.type === "subpipeline" ? (
                        <URLLink
                            href={data.type === "subpipeline"
                                ? `/showcase/pipeline/${data.service_slug}`
                                : `/showcase/service/${data.service_slug}`}
                            sx={{textDecoration: "none"}}>
                            <Tooltip title={data.type === "subpipeline" ? "Pipeline's page" : "Service's page"}
                                     placement={"top"}>
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
                    sx={{width: "100%", justifyContent: "center"}}
                >
                    {serviceStatus === ServiceStatus.SLEEPING ? (
                        <Tooltip title={"Wake up service"} placement={"bottom"}>
                            <span style={{width: "100%"}}>
                                <Button
                                    disabled={sleeping}
                                    sx={{
                                        width: "100%",
                                        minHeight: 32,
                                    }}
                                    variant={"outlined"}
                                    color={"secondary"}
                                    size={"small"}
                                    startIcon={<NotificationsPausedTwoTone/>}
                                    onClick={wakeUpService}
                                >
                                    Wake up
                                </Button>
                            </span>
                        </Tooltip>
                    ) : getStatus() === RunState.SKIPPED ? (
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
                        (data.type === "pipeline" || data.type === "subpipeline") && (
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
                        ))}
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

export default StepNode;
