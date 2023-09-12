import React from "react";
import { Handle, Position } from "react-flow-renderer";
import {
    Box, Button, Card, CardActions, CardContent, Divider, Input, LinearProgress, Tooltip, Typography
} from '@mui/material';
import { PlayCircleTwoTone, UploadFileTwoTone } from '@mui/icons-material';
import { RunState, setRunState, setResultIdList } from '../../utils/reducers/runStateSlice';
import { useDispatch, useSelector } from 'react-redux';
import { postToEngine } from '../../utils/api';
import { FieldDescription, FieldDescriptionWithSetAndValue } from '../../models/ExecutionUnit';
import { useFileArray } from '../../utils/hooks/fileArray';
import { useWebSocketConnection } from '../../utils/useWebSocketConnection';
import { toast } from 'react-toastify';
import { grey } from '@mui/material/colors';

function createAllowedTypesString(allowedTypes: string[]) {
    return allowedTypes.join(', ');
}

function addIsSetToFields(fields: FieldDescription[]): FieldDescriptionWithSetAndValue[] {
    return fields.map(field => {
        return {...field, isSet: false, value: null};
    });
}


const EntryNode = ({data}: any) => {
    const lightgrey = grey[400];
    const darkgrey = grey[800];
    const colorMode = useSelector((state: any) => state.colorMode.value);
    const dispatch = useDispatch();
    const {fileArray, setFileArray} = useFileArray();
    const run = useSelector((state: any) => state.runState.value);
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
            run === RunState.PENDING ||
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

    const launchExecution = async (serviceSlug: string) => {
        const response = await postToEngine(serviceSlug, fileArray);
        if (response.id) {
            dispatch(setRunState(RunState.PROCESSING));
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
            {isExecuting() ? (
                <LinearProgress
                    sx={{borderRadius: 1, mb: 1, mx: 1}}
                    color={"primary"}
                />
            ) : (
                <Button
                    disabled={!areItemsUploaded || isExecuting()}
                    sx={{flexGrow: 1}}
                    variant={"contained"}
                    color={"primary"}
                    size={"small"}
                    endIcon={<PlayCircleTwoTone sx={{color: (isExecuting()) ? "transparent" : "inherit"}}/>}
                    onClick={() => launchExecution(data.label.replace("-entry", ""))}
                >
                    Run
                </Button>
            )}
        </Box>
    }

    React.useEffect(() => {
        dispatch(setRunState(RunState.IDLE));
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
            <Handle
                type={"source"}
                position={Position.Right}
            />
        </>
    );
};

export default EntryNode;