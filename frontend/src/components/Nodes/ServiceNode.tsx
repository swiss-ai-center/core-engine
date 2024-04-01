import React, {useState} from "react";
import { Connection, Handle, Position} from "reactflow";
import {Autocomplete, Box, Card, CardActions, CardContent, IconButton, TextField, Typography} from '@mui/material';
import {useSelector} from 'react-redux';
import {grey} from '@mui/material/colors';
import {Close as CloseIcon} from "@mui/icons-material";
import CustomHandle from "../Board/CustomHandle";
import {positionHandle} from "../../utils/functions";
import {FieldDescription} from "../../models/ExecutionUnit";


const ServiceNode: React.FC<{ id: string, data: any }> = (
    {id, data}) => {
    const lightgrey = grey[400];
    const darkgrey = grey[800];
    const colorMode = useSelector((state: any) => state.colorMode.value);

    const listDataIn = () => {
        return data.dataIn.map((inputField: { name: string ; type: string[]; }, index: number) =>
            <Box sx={{display: "flex", width: "100%"}} key={index}>
                <Box sx={{display: "flex", flexDirection: "column", justifyContent: "center", width: "40%"}} key={index}>
                    <Typography variant={"body2"}>{inputField.name} : </Typography>
                    <Box sx={{display:"flex"}}>
                        {inputField.type.map((type: string) => <Typography variant={"body2"}>{type} &nbsp;</Typography>)}
                    </Box>
                </Box>
            </Box>
        );
    }

    return (
        <>
            {data.dataIn.map((input: FieldDescription, index: number) => {
                return (
                    <CustomHandle
                        key={index}
                        id={input.name === "Input Name" ?  `${input.name}${index}` : input.name}
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
                <CardContent sx={{flexGrow: 1, mb: -1, minWidth: "15em"}}>
                    <Typography variant={"subtitle1"} color={"primary"}
                                sx={{justifyContent: "center", display: "flex", mb: 2 }}
                    >
                        {data.label}
                    </Typography>
                    <Box sx={{display: "flex", width: "100%"}}>
                        <Box sx={{display: "flex", flexDirection: "column", alignItems: "center"}}>
                            <Typography variant={"body1"}>RIEN </Typography>
                        </Box>
                    </Box>
                    {listDataIn()}
                </CardContent>
                <CardActions>{}</CardActions>
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
