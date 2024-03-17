import React, {useState} from "react";
import { Connection, Handle, Position} from "react-flow-renderer";
import {Autocomplete, Box, Card, CardActions, CardContent, TextField, Typography} from '@mui/material';
import {useSelector} from 'react-redux';
import {grey} from '@mui/material/colors';
import {FieldDescription} from "../../models/ExecutionUnit";


const ServiceNode: React.FC<{ data: any }> = (
    {data}) => {
    const lightgrey = grey[400];
    const darkgrey = grey[800];
    const colorMode = useSelector((state: any) => state.colorMode.value);
    const [selectedDataIn, setSelectedDataIn] = useState<string[]>([]);
    const [inputValue, setInputValue]  = React.useState<string>('')
    const [linked, setLinked]  = React.useState<boolean>(false)


    const options: string[] = [];
    data.dataInOptions.forEach((option: FieldDescription) => {
        options.push(option.name)
    })

    const listDataIn = data.dataIn.map((inputField: { name: string ; type: string[]; }, index: number) =>
            <Box sx={{display: "flex"}} key={index}>
                <Box sx={{display: "flex", flexDirection: "column", justifyContent: "center"}} key={index}>
                    <Typography variant={"body1"}>{inputField.name} : </Typography>
                    <Box sx={{display:"flex"}}>
                        {inputField.type.map((type: string) => <Typography variant={"body2"}>{type} &nbsp;</Typography>)}
                    </Box>
                </Box>
                <Autocomplete
                    sx={{mb: 2}}
                    value={inputValue}
                    blurOnSelect={false}
                    options={options}
                    autoHighlight={false}
                    isOptionEqualToValue={(option, value) => value === "" || option === value}
                    renderOption={(props, option, {selected}) => (
                        <li {...props}>
                            {option}
                        </li>
                    )}
                    renderInput={(params) => (
                        <TextField {...params} label={"Data-In"} placeholder="Select"/>
                    )}
                />
            </Box>
    );

    const onConnect = (connection: Connection) => {
        setLinked(true);
    }

    return (
        <>
            <Handle
                type={"target"}
                position={Position.Left}
                onConnect={(param) => onConnect(param)}
            />
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
                <CardContent sx={{flexGrow: 1, mb: -1, minWidth: "20em"}}>
                    <Typography variant={"h5"} color={"primary"}
                                sx={{justifyContent: "center", display: "flex"}}
                    >
                        {data.label}
                    </Typography>
                    {listDataIn}
                </CardContent>
                <CardActions>{}</CardActions>
            </Card>
            <Handle
                type={"source"}
                position={Position.Right}
            />
        </>
    );
};

export default ServiceNode;
