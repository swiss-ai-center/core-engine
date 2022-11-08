import React, { useCallback, useState } from "react";

import { Handle, Position } from "react-flow-renderer";
import {
    Button,
    Card,
    CardActions,
    CardContent,
    Divider,
    Input,
    Tooltip,
    Typography
} from '@mui/material';
import { Download, PlayArrow } from '@mui/icons-material';
import { RunState, setRunState } from '../../utils/reducers/runStateSlice';
import { useDispatch, useSelector } from 'react-redux';
import { postService } from '../../utils/api';

function mergeBody(body: any, bodyType: any) {
    let array: any = [];
    if (body) {
        if (typeof body === 'string') {
            array.push({field: body, type: "*", isSet: false, value: null});
        } else {
            for (let i = 0; i < body.length; i++) {
                array.push({field: body[i], type: bodyType[i].replace("[", "").replace("]", ""), isSet: false, value: null});
            }
        }
    }
    return array;
}


const fileToBase64 = (file: File) => {
    return new Promise(resolve => {
        const reader = new FileReader();
        // Read file content on file loaded event
        reader.onload = function(event) {
            resolve(event.target?.result);
        };

        // Convert data to base64
        reader.readAsDataURL(file);
    });
};

const CustomNode = ({data, styles}: any) => {
    const dispatch = useDispatch();
    const run = useSelector((state: any) => state.runState.value);

    const [array, setArray] = useState<any[]>([]);
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
        let body: any = {};
        for (const item of array) {
            body[item.field] = await fileToBase64(item.value);
        }
        const response = await postService(data.label.replace("-entry", ""), body);
        console.log(response);
        if (response) {
            dispatch(setRunState(RunState.RUNNING));
        } else {
            console.log("Error");
        }
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
                                        <Divider />
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
                            <Button disabled={!areItemsUploaded} sx={{flexGrow: 1}} variant={"contained"}
                                    color={"success"} size={"small"} endIcon={<PlayArrow/>} onClick={() => runPipeline()}>
                                Run
                            </Button>
                        </CardActions>)
                    :
                    (<></>)}
                {(data.label.includes("end")) ?
                    (
                        <CardActions>
                            <Button disabled={!(run === RunState.ENDED)} sx={{flexGrow: 1}} variant={"contained"}
                                    color={"info"} size={"small"} endIcon={<Download/>}>Download</Button>
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
