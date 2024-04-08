import React from "react";
import { NodeProps, Position } from "reactflow";
import {
    Box, Button, Card, CardActions, CardContent, Divider, Input, LinearProgress, Tooltip, Typography
} from '@mui/material';
import { PlayCircleTwoTone, UploadFileTwoTone, UploadTwoTone } from '@mui/icons-material';
import {
    resetRunState,
    RunState, setCurrentTask,
    setGeneralStatus,
    resetTimer,
    setTaskArray,
} from '../../utils/reducers/runStateSlice';
import { useDispatch, useSelector } from 'react-redux';
import { postToEngine } from '../../utils/api';
import { FieldDescription, FieldDescriptionWithSetAndValue } from '../../models/ExecutionUnit';
import { useFileArray } from '../../utils/hooks/fileArray';
import { useWebSocketConnection } from '../../utils/useWebSocketConnection';
import { toast } from 'react-toastify';
import { grey } from '@mui/material/colors';
import { EntryNodeData } from '../../models/NodeData';
import CustomHandle from './CustomHandle';
import { positionHandle } from '../../utils/functions';

function createAllowedTypesString(allowedTypes: string[]) {
    return allowedTypes.join(', ');
}

function addIsSetToFields(fields: FieldDescription[]): FieldDescriptionWithSetAndValue[] {
    return fields.map(field => {
        return {...field, isSet: false, value: null};
    });
}


const EntryNode = ({data}: NodeProps<EntryNodeData>) => {
    const lightgrey = grey[400];
    const darkgrey = grey[800];
    const colorMode = useSelector((state: any) => state.colorMode.value);
    const dispatch = useDispatch();
    const {fileArray, setFileArray} = useFileArray();
    const generalStatus = useSelector((state: any) => state.runState.generalStatus);
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

    const handleUpload = (field: string, value: any) => {
        setFileArray((prevState: any[]) => prevState.map(item => {
            if (item.name === field) {
                return {...item, value: value[0], isSet: true}
            }
            return item;
        }));
        checkIfAllItemsAreUploaded();
    }

    const isUploading = () => {
        return (generalStatus === RunState.UPLOADING);
    }

    const isIdle = () => {
        return generalStatus === RunState.IDLE ||
            generalStatus === RunState.FINISHED ||
            generalStatus === RunState.ERROR;
    }

    const launchExecution = async (serviceSlug: string) => {
        dispatch(setGeneralStatus(RunState.UPLOADING));
        const response = await postToEngine(serviceSlug, fileArray);
        dispatch(resetTimer());
        if (response.id) {
            if (response.tasks) {
                dispatch(setTaskArray(response.tasks));
                dispatch(setGeneralStatus(response.tasks[0].status));
                dispatch(setCurrentTask(response.tasks[0]));
            } else {
                dispatch(setTaskArray([response]));
                dispatch(setGeneralStatus(response.status));
                dispatch(setCurrentTask(response));
            }
            toast("Execution started", {type: "success"});
            sendJsonMessage({
                linked_id: response.id,
                execution_type: data.executionType,
            });
        } else {
            toast(`Error while launching execution: ${response.error}`, {type: "error"});
        }
    }

    const actionContent = () => {
        return <Box
            sx={{display: "flex", width: "100%", minHeight: 32, flexDirection: "column", justifyContent: "center"}}
        >
            {!isIdle() && !isUploading() ? (
                <LinearProgress
                    sx={{borderRadius: 1, mb: 1, mx: 1}}
                    color={"primary"}
                />
            ) : (
                <Button
                    disabled={!areItemsUploaded || !isIdle() || isUploading()}
                    sx={{flexGrow: 1}}
                    variant={"contained"}
                    color={"primary"}
                    size={"small"}
                    disableElevation
                    endIcon={isUploading() ? <UploadTwoTone/> :
                        <PlayCircleTwoTone sx={{color: (!isIdle()) ? "transparent" : "inherit"}}/>}
                    onClick={() => launchExecution(data.label.replace("-entry", ""))}
                >
                    {isUploading() ? "Uploading..." : "Run"}
                </Button>
            )}
        </Box>
    }

    React.useEffect(() => {
        dispatch(resetRunState());
        dispatch(resetTimer());
        if (data.data_in_fields) {
            setFileArray(addIsSetToFields(data.data_in_fields));
        }
    }, [data, dispatch, setFileArray]);

    React.useEffect(() => {
        checkIfAllItemsAreUploaded();
    }, [checkIfAllItemsAreUploaded]);

    return (
        <>
            <Card
                sx={{
                    height: "100%", display: "flex", flexDirection: "column",
                    borderColor: areItemsUploaded ? "success.main" : (colorMode === "light" ? lightgrey : darkgrey),
                    borderWidth: 2,
                    borderStyle: "solid",
                    borderRadius: 2,
                    boxShadow: "none",
                }}
            >
                <CardContent sx={{flexGrow: 1, mb: -1}}>
                    <Typography variant={"subtitle1"} color={"primary"}
                                sx={{justifyContent: "center", display: "flex"}}
                    >
                        {data.label}
                    </Typography>
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
                                                    sx={{mb: (index !== fileArray.length - 1) ? 1 : 0, mt: 1}}
                                                    color={item.isSet ? "success" : "secondary"}
                                                    endIcon={<UploadFileTwoTone/>}
                                            >
                                                Upload
                                                <label htmlFor={"upload-file-input-" + index}/>
                                                <input
                                                    id={"upload-file-input-" + index}
                                                    accept={createAllowedTypesString(item.type)}
                                                    type={"file"}
                                                    hidden
                                                    onChange={
                                                        (event) => handleUpload(item.name, event.target.files)
                                                    }
                                                />
                                            </Button>
                                        </Tooltip>)}
                                    {(index !== fileArray.length - 1) ? <Divider/> : null}
                                </div>
                            );
                        })
                        :
                        <Typography/>
                    }
                </CardContent>
                <CardActions>{actionContent()}</CardActions>
            </Card>

            <div className="handles sources">
                {data.sourceHandles.map((handle, index) => {
                    // check if sourceHandles has duplicates
                    const sourceHandles = data.sourceHandles;
                    const sourceHandlesIds = sourceHandles.map((handle) => handle.id);
                    const sourceHandlesSet = new Set(sourceHandlesIds);
                    if (sourceHandlesSet.size !== sourceHandlesIds.length) {
                        console.error("sourceHandles has duplicates");
                    }
                    return (
                        <CustomHandle
                            key={handle.id}
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

export default EntryNode;
