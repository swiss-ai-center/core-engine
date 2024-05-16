import React, {useCallback} from "react";
import {Position, useReactFlow} from "reactflow";
import {Box, Card, CardActions, CardContent, IconButton, Typography} from '@mui/material';
import {useSelector} from 'react-redux';
import {grey} from '@mui/material/colors';
import CustomHandle from "../Handles/CustomHandle";
import {positionHandle} from "../../utils/functions";
import {FieldDescription} from "../../models/ExecutionUnit";
import {Close as CloseIcon} from "@mui/icons-material";


const ServiceNode: React.FC<{ id: string, data: any }> = (
    {id, data}) => {
    const lightgrey = grey[400];
    const darkgrey = grey[800];
    const colorMode = useSelector((state: any) => state.colorMode.value);
    const { deleteElements } = useReactFlow();

    const onDelete = useCallback(() => {
        deleteElements({ nodes: [{ id }] });
    }, [id, deleteElements]);


    const listDataIn = () => {
        return data.dataIn.map((inputField: { name: string; type: string[]; }, index: number) =>
            <div key={inputField.name} style={{marginBottom: 4}}>
                <Box sx={{display: "flex", width: "100%"}}>
                    <Box sx={{display: "flex", flexDirection: "column", justifyContent: "center"}} key={inputField.name}>
                        <Typography variant={"body2"}>{inputField.name} : </Typography>
                        <Box sx={{display: "flex"}}>
                            {inputField.type.map((type: string) => <Typography
                                variant={"body2"} key={`${inputField.name}${type}`}>{type} &nbsp;</Typography>)}
                        </Box>
                    </Box>
                </Box>
            </div>
        );
    }

    return (
        <>
            {data.dataIn.map((input: FieldDescription, index: number) => {
                return (
                    <CustomHandle
                        key={index}
                        id={input.name === "Input Name" ? `${input.name}${index}` : input.name}
                        label={input.name}
                        type={"target"}
                        style={{top: positionHandle(data.dataIn.length, index + 1)}}
                        position={Position.Left}
                    />
                );
            })}
            <Card
                sx={{
                    height: "100%", display: "flex", flexDirection: "column",
                    borderColor: colorMode === "light" ? lightgrey : darkgrey,
                    borderWidth: 2,
                    borderStyle: "solid",
                    borderRadius: 2,
                    boxShadow: "none",
                }}

            >
                <CardContent sx={{flexGrow: 1, mb: -1, minWidth: "17em", mt: -2}}>
                    <Box sx={{display: "flex", flexDirection: "row", alignItems: "center"}}>
                        <Typography variant={"subtitle1"} color={"primary"} sx={{flexGrow: 1, textAlign: "center",width: "80%"}}>
                            {data.label}
                        </Typography>
                        <IconButton
                            sx={{width: "10%", height: "fit-content", transform: "scale(0.7)"}}
                            aria-label={"close"}
                            onClick={onDelete}
                        >
                            <CloseIcon/>
                        </IconButton>
                    </Box>
                    {listDataIn()}
                </CardContent>
                <CardActions></CardActions>
            </Card>
            {data.dataOut.map((output: FieldDescription, index: number) => {
                return (
                    <CustomHandle
                        key={index}
                        id={output.name}
                        label={output.name}
                        type={"source"}
                        style={{top: positionHandle(data.dataOut.length, index + 1)}}
                        position={Position.Right}
                    />
                );
            })}
        </>
    );
};

export default ServiceNode;
