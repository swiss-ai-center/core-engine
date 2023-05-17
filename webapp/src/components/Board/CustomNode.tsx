import React, { useCallback, useState } from "react";
import { Handle, Position } from "react-flow-renderer";
import {
    Box, Button, Card, CardActions, CardContent, CircularProgress, Divider, Input, Tooltip, Typography
} from '@mui/material';
import { Download, PlayArrow } from '@mui/icons-material';
import { RunState, setTaskId, setRunState, setResultIdList } from '../../utils/reducers/runStateSlice';
import { useDispatch, useSelector } from 'react-redux';
import { getResult, getTask, postToEngine } from '../../utils/api';
import { useNotification } from '../../utils/useNotification';
import { FieldDescription, FieldDescriptionWithSetAndValue } from '../../models/ExecutionUnit';

function createAllowedTypesString(allowedTypes: string[]) {
    return allowedTypes.join(', ');
}

function addIsSetToFields(fields: FieldDescription[]): FieldDescriptionWithSetAndValue[] {
    return fields.map(field => {
        return {...field, isSet: false, value: null};
    });
}

const CustomNode = ({data, styles}: any) => {
    const dispatch = useDispatch();
    const run = useSelector((state: any) => state.runState.value);
    useSelector((state: any) => state.runState.taskId);
    const resultIdList = useSelector((state: any) => state.runState.resultIdList);
    const {displayNotification} = useNotification();

    const [array, setArray] = useState<FieldDescriptionWithSetAndValue[]>([]);
    const [areItemsUploaded, setAreItemsUploaded] = React.useState(false);

    const checkIfAllItemsAreUploaded = useCallback(() => {
        let allItemsAreUploaded = true;
        array.forEach((item: any) => {
            if (!item.isSet) {
                allItemsAreUploaded = false;
            }
        });
        setAreItemsUploaded(allItemsAreUploaded);
    }, [array]);

    const checkTaskStatus = async (id: string) => {
        const task = await getTask(id);
        if (task.status === 'finished') {
            dispatch(setResultIdList(task.data_out));
            dispatch(setRunState(RunState.ENDED));
        } else if (task.status === 'error') {
            displayNotification({
                message: "The pipeline ended with an error",
                type: "error",
                open: true,
                timeout: 2000
            });
            dispatch(setRunState(RunState.ERROR));
        } else {
            setTimeout(() => checkTaskStatus(id), 1000);
        }
    }

    const handleUpload = (field: string, value: any) => {
        setArray(prevState => prevState.map(item => {
            if (item.name === field) {
                return {...item, value: value[0], isSet: true}
            }
            return item;
        }));
        checkIfAllItemsAreUploaded();
    }

    const runPipeline = async () => {
        const response = await postToEngine(data.label.replace("-entry", ""), array);
        if (response.id) {
            dispatch(setRunState(RunState.RUNNING));
            dispatch(setTaskId(response.id));
            displayNotification({message: "Pipeline started", type: "success", open: true, timeout: 2000});
            checkTaskStatus(response.id);
        } else {
            displayNotification({
                message: `Error while running pipeline: ${response.detail}`,
                type: "error",
                open: true,
                timeout: 2000
            });
        }
    }

    const downloadResult = async () => {
        for (const id of resultIdList) {
            const file = await getResult(id);
            if (file) {
                const link = document.createElement('a');
                link.href = window.URL.createObjectURL(file);
                link.setAttribute('download', 'result.' + id.split('.')[1]);
                document.body.appendChild(link);
                link.click();
            } else {
                displayNotification({
                    message: "Error downloading file" + id,
                    type: "error",
                    open: true,
                    timeout: 2000
                });
            }
        }
    }

    const actionContent = () => {
        return <Box sx={{display: "flex", width: "100%"}}>
            <Button disabled={!areItemsUploaded || run === RunState.RUNNING} sx={{flexGrow: 1}} variant={"contained"}
                    color={"success"} size={"small"}
                    endIcon={<PlayArrow sx={{color: (run === RunState.RUNNING) ? "transparent" : "inherit"}}/>}
                    onClick={() => runPipeline()}>
                {run === RunState.RUNNING ? (
                    <CircularProgress size={24} color={"primary"}
                                      sx={{position: "absolute", alignSelf: "center",}}
                    />
                ) : (<>Run</>)}
            </Button>
        </Box>
    }

    React.useEffect(() => {
        dispatch(setRunState(RunState.STOPPED));
        dispatch(setResultIdList([]));
        if (data.data_in_fields) {
            setArray(addIsSetToFields(data.data_in_fields));
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [data]);

    React.useEffect(() => {
        checkIfAllItemsAreUploaded();
    }, [checkIfAllItemsAreUploaded]);

    return (
        <>
            <Card
                sx={{height: "100%", display: "flex", flexDirection: "column"}}
            >
                <CardContent sx={{flexGrow: 1}}>
                    <Typography variant={"subtitle1"} color={"primary"}>{data.label}</Typography>
                    {(data.data_in_fields) ?
                        array.map((item: any, index: number) => {
                            return (
                                <div key={`div-${index}`}>
                                    <Typography variant={"body2"} key={`field-${index}`} sx={{mt: 1}}>
                                        {item.name}
                                    </Typography>
                                    {(item.type === "text/plain") ?
                                        (<Input key={`input-${index}`} placeholder={"Enter text"}/>)
                                        :
                                        (<Tooltip title={"type(s): " + item.type} placement={"right"}>
                                            <Button key={`btn-${index}`} variant={"outlined"} component={"label"}
                                                    size={"small"} sx={{mb: 1, mt: 1}}
                                                    color={item.isSet ? "success" : "secondary"}>
                                                Upload
                                                <input
                                                    accept={createAllowedTypesString(item.type)}
                                                    type={"file"}
                                                    hidden
                                                    onChange={
                                                        (event) => handleUpload(item.name, event.target.files)
                                                    }
                                                />
                                            </Button>
                                        </Tooltip>)}
                                    <Divider/>
                                </div>
                            );
                        })
                        :
                        <Typography></Typography>
                    }
                </CardContent>
                {(data.label.includes("entry")) ?
                    (
                        <CardActions>
                            {actionContent()}
                        </CardActions>)
                    :
                    (<></>)}
                {(data.label.includes("exit")) ?
                    (
                        <CardActions>
                            <Button disabled={!(run === RunState.ENDED)} sx={{flexGrow: 1}} variant={"contained"}
                                    color={"info"} size={"small"} endIcon={<Download/>}
                                    onClick={downloadResult}>Download</Button>
                        </CardActions>)
                    :
                    (<></>)}
            </Card>

            {(data.label && !data.label.includes("entry")) ?
                <Handle
                    type={"target"}
                    position={Position.Left}
                /> : <></>}
            {(data.label && !data.label.includes("exit")) ?
                <Handle
                    type={"source"}
                    position={Position.Right}
                /> : <></>}
        </>
    );
};

export default CustomNode;
