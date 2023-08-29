import React from "react";
import { Handle, Position } from "react-flow-renderer";
import {
    Box, Button, Card, CardActions, CardContent, CircularProgress, Divider, Input, Tooltip, Typography
} from '@mui/material';
import { Download, PlayArrow } from '@mui/icons-material';
import {
    RunState,
    setRunState,
    setResultIdList,
} from '../../utils/reducers/runStateSlice';
import { useDispatch, useSelector } from 'react-redux';
import { getResult, postToEngine } from '../../utils/api';
import { FieldDescription, FieldDescriptionWithSetAndValue } from '../../models/ExecutionUnit';
import { useFileArray } from '../../utils/hooks/fileArray';
import { useWebSocketConnection } from '../../utils/useWebSocketConnection';
import { toast } from 'react-toastify';

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
    const {fileArray, setFileArray} = useFileArray();
    const run = useSelector((state: any) => state.runState.value);
    const resultIdList = useSelector((state: any) => state.runState.resultIdList);
    const {sendJsonMessage} = useWebSocketConnection();

    const [areItemsUploaded, setAreItemsUploaded] = React.useState(false);

    const checkIfAllItemsAreUploaded = React.useCallback(() => {
        let allItemsAreUploaded = true;
        fileArray.forEach((item: any) => {
            if (!item.isSet) {
                allItemsAreUploaded = false;
            }
        });
        setAreItemsUploaded(allItemsAreUploaded);
    }, [fileArray]);

    const isExecuting = () => {
        return (
            run === RunState.PROCESSING ||
            run === RunState.SAVING ||
            run === RunState.FETCHING ||
            run === RunState.SCHEDULED);
    }

    const handleUpload = (field: string, value: any) => {
        setFileArray((prevState: any[]) => prevState.map(item => {
            if (item.name === field) {
                return {...item, value: value[0], isSet: true}
            }
            return item;
        }));
        checkIfAllItemsAreUploaded();
    }

    const downloadResult = async () => {
        for (const id of resultIdList) {
            const file: any = await getResult(id);
            if (file.file) {
                const link = document.createElement('a');
                link.href = window.URL.createObjectURL(file.file);
                link.setAttribute('download', 'result.' + id.split('.')[1]);
                document.body.appendChild(link);
                link.click();
            } else {
                toast(`Error downloading file ${id}: ${file.error}`, {type: "error"});
            }
        }
    }

    const launchExecution = async (serviceSlug: string) => {
        const response = await postToEngine(serviceSlug, fileArray);
        if (response.id) {
            dispatch(setRunState(RunState.PROCESSING));
            toast(`Execution started`, {type: "success"});
            sendJsonMessage({
                linked_id: response.id,
                execution_type: data.executionType,
            });
        } else {
            toast(`Error while launching execution: ${response.error}`, {type: "error"});
        }
    }

    const actionContent = () => {
        return <Box sx={{display: "flex", width: "100%"}}>
            <Button
                disabled={!areItemsUploaded || isExecuting()}
                sx={{flexGrow: 1}}
                variant={"contained"}
                color={"success"}
                size={"small"}
                endIcon={<PlayArrow sx={{color: (isExecuting()) ? "transparent" : "inherit"}}/>}
                onClick={() => launchExecution(data.label.replace("-entry", ""))}>
                {isExecuting() ? (
                    <CircularProgress
                        size={24}
                        color={"primary"}
                        sx={{position: "absolute", alignSelf: "center",}}
                    />
                ) : (<>Run</>)}
            </Button>
        </Box>
    }

    React.useEffect(() => {
        dispatch(setRunState(RunState.PENDING));
        dispatch(setResultIdList([]));
        if (data.data_in_fields) {
            setFileArray(addIsSetToFields(data.data_in_fields));
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
                        fileArray.map((item: any, index: number) => {
                            return (
                                <div key={`div-${index}`}>
                                    <Typography variant={"body2"} key={`field-${index}`} sx={{mt: 1}}>
                                        {item.name}
                                    </Typography>
                                    {(item.type === "text/plain") ?
                                        (<Input key={`input-${index}`} placeholder={"Enter text"}/>)
                                        :
                                        (<Tooltip title={"type(s): " + item.type} placement={"right"}>
                                            <Button key={`btn-${index}`}
                                                    variant={"outlined"}
                                                    component={"label"}
                                                    size={"small"}
                                                    sx={{mb: 1, mt: 1}}
                                                    color={item.isSet ? "success" : "secondary"}
                                            >
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
                        <Typography/>
                    }
                </CardContent>
                {(data.label.includes("entry")) ? (<CardActions>{actionContent()}</CardActions>) : (<></>)}
                {(data.label.includes("exit")) ?
                    (
                        <CardActions>
                            <Button
                                disabled={!(run === RunState.FINISHED)}
                                sx={{flexGrow: 1}}
                                variant={"contained"}
                                color={"info"}
                                size={"small"}
                                endIcon={<Download/>}
                                onClick={downloadResult}
                            >
                                Download
                            </Button>
                        </CardActions>
                    ) : (<></>)
                }
            </Card>

            {(data.label && !data.label.includes("entry")) ?
                <Handle
                    type={"target"}
                    position={Position.Left}
                /> : <></>
            }
            {(data.label && !data.label.includes("exit")) ?
                <Handle
                    type={"source"}
                    position={Position.Right}
                /> : <></>
            }
        </>
    );
};

export default CustomNode;
