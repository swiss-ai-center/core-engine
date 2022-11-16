import React, { useCallback, useState } from "react";

import { Handle, Position } from "react-flow-renderer";
import {
    Box,
    Button,
    Card,
    CardActions,
    CardContent, CircularProgress,
    Divider,
    Input,
    Tooltip,
    Typography
} from '@mui/material';
import { Download, PlayArrow } from '@mui/icons-material';
import { RunState, setJobId, setRunState } from '../../utils/reducers/runStateSlice';
import { useDispatch, useSelector } from 'react-redux';
import { getResult, getTaskStatus, postToService } from '../../utils/api';
import { useNotification } from '../../utils/useNotification';

function mergeBody(body: any, bodyType: any) {
    let array: any = [];
    if (body) {
        if (typeof body === 'string') {
            array.push({field: body, type: "*", isSet: false, value: null});
        } else {
            for (let i = 0; i < body.length; i++) {
                array.push({
                    field: body[i],
                    type: bodyType[i].replace("[", "").replace("]", ""),
                    isSet: false,
                    value: null
                });
            }
        }
    }
    return array;
}

const CustomNode = ({data, styles}: any) => {
    const dispatch = useDispatch();
    const run = useSelector((state: any) => state.runState.value);
    const jobId = useSelector((state: any) => state.runState.jobId);
    const { displayNotification } = useNotification();

    const [array, setArray] = useState<{ field: string; value: string | Blob }[]>([]);
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

    const checkTaskStatus = async (jobId: string) => {
        const task = await getTaskStatus(jobId);
        if (task.status === 'finished') {
            dispatch(setRunState(RunState.ENDED));
        } else if (task.status === 'failed') {
            displayNotification({message: "The pipeline ended with an error", type: "error", open: true, timeout: 2000});
            dispatch(setRunState(RunState.ERROR));
        } else {
            setTimeout(() => checkTaskStatus(jobId), 1000);
        }
    }

    const handleUpload = (field: string, value: any) => {
        setArray(prevState => prevState.map(item => {
            if (item.field === field) {
                return {...item, value: value[0], isSet: true}
            }
            return item;
        }));
        checkIfAllItemsAreUploaded();
    }

    const runPipeline = async () => {
        const response = await postToService(data.label.replace("-entry", ""), array);
        if (response.jobId) {
            dispatch(setRunState(RunState.RUNNING));
            dispatch(setJobId(response.jobId));
            displayNotification({message: "Pipeline started", type: "success", open: true, timeout: 2000});
            checkTaskStatus(response.jobId);
        } else {
            displayNotification({message: `Error while running pipeline: ${response.detail}`, type: "error", open: true, timeout: 2000});
        }
    }

    const downloadResult = async () => {
        const file = await getResult(jobId);
        if (file) {
            const link = document.createElement('a');
            link.href = window.URL.createObjectURL(file);
            link.setAttribute('download', 'result.json');
            document.body.appendChild(link);
            link.click();
        } else {
            displayNotification({message: "Error downloading file", type: "error", open: true, timeout: 2000});
        }
    }

    const actionContent = () => {
        return <Box sx={{display: 'flex', width: '100%'}}>
            <Button disabled={!areItemsUploaded || run === RunState.RUNNING}
                    sx={{flexGrow: 1}} color={"success"} variant={"contained"}
                    size={"small"}
                    endIcon={<PlayArrow sx={{color: (run === RunState.RUNNING) ? 'transparent' : 'inherit'}}/>}
                    onClick={() => runPipeline()}>
                {run === RunState.RUNNING ? (
                    <CircularProgress size={24}
                                      sx={{position: 'absolute', alignSelf: 'center', color: 'white'}}
                    />
                ) : (<>Run</>)}
            </Button>
        </Box>
    }

    React.useEffect(() => {
        setArray(mergeBody(data.body, data.bodyType));
    }, [data]);

    React.useEffect(() => {
        checkIfAllItemsAreUploaded();
    }, [checkIfAllItemsAreUploaded]);

    return (
        <>
            <Card
                sx={{height: '100%', display: 'flex', flexDirection: 'column'}}
            >
                <CardContent sx={{flexGrow: 1}}>
                    <Typography variant={"subtitle1"} color={"secondary"}>{data.label}</Typography>
                    {(data.body) ?
                        array.map((item: any, index: number) => {
                            return (
                                <div key={`div-${index}`}>
                                    <Typography variant={"body2"} key={`field-${index}`} sx={{mt: 1}}>
                                        {item.field}
                                    </Typography>
                                    {(item.type === "text/plain") ?
                                        (<Input key={`input-${index}`} placeholder={"Enter text"}/>)
                                        :
                                        (<Tooltip title={"type(s): " + item.type} placement={"right"}>
                                            <Button key={`btn-${index}`} variant={"outlined"} component={"label"}
                                                    size={"small"} sx={{mb: 1, mt: 1}}
                                                    color={item.isSet ? 'success' : 'primary'}>
                                                Upload
                                                <input
                                                    accept={item.type}
                                                    type={"file"}
                                                    hidden
                                                    onChange={(event) => handleUpload(item.field, event.target.files)}
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
                {(data.label.includes("end")) ?
                    (
                        <CardActions>
                            <Button disabled={!(run === RunState.ENDED)} sx={{flexGrow: 1}} variant={"contained"}
                                    color={"info"} size={"small"} endIcon={<Download/>}
                                    onClick={downloadResult}>Download</Button>
                        </CardActions>)
                    :
                    (<></>)}
            </Card>

            {(!data.label.includes("entry")) ?
                <Handle
                    type="target"
                    position={Position.Left}
                /> : <></>}
            {(!data.label.includes("end")) ?
                <Handle
                    type="source"
                    position={Position.Right}
                /> : <></>}
        </>
    );
};

export default CustomNode;
