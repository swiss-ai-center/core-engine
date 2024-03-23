import React, {useState} from "react";
import { Connection, Handle, Position} from "react-flow-renderer";
import {Autocomplete, Box, Card, CardActions, CardContent, TextField, Typography} from '@mui/material';
import {useSelector} from 'react-redux';
import {grey} from '@mui/material/colors';


const ServiceNode: React.FC<{ id: string, data: any }> = (
    {id, data}) => {
    const lightgrey = grey[400];
    const darkgrey = grey[800];
    const colorMode = useSelector((state: any) => state.colorMode.value);
    const [dataInList, setDataInList]  = React.useState<any>()

    const listDataIn = () => data.dataIn.map((inputField: { name: string ; type: string[]; }, index: number) =>
            <Box sx={{display: "flex", width: "100%"}} key={index}>
                <Box sx={{display: "flex", flexDirection: "column", justifyContent: "center", width: "40%"}} key={index}>
                    <Typography variant={"body1"}>{inputField.name} : </Typography>
                    <Box sx={{display:"flex"}}>
                        {inputField.type.map((type: string) => <Typography variant={"body2"}>{type} &nbsp;</Typography>)}
                    </Box>
                </Box>
                <Autocomplete
                    fullWidth
                    sx={{mb: 2, minWidth: "10em", width: "60%"}}
                    value={data.selectedDataIn[index]}
                    options={data.dataInOptions}
                    autoHighlight={false}
                    renderOption={(props, option: string, {selected}) => (
                        <li {...props}>
                            {option}
                        </li>
                    )}
                    onChange={(event,value) => {
                        if (value) data.onSelectInput(id,index,value);
                    }}
                    renderInput={(params) => (
                        <TextField {...params} label={"Input source"}/>
                    )}
                />
            </Box>
    );

    React.useEffect(() =>  {
        setDataInList(listDataIn())
    }, [data])


    return (
        <>
            <Handle
                type={"target"}
                position={Position.Left}
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
                <CardContent sx={{flexGrow: 1, mb: -1, minWidth: "30em"}}>
                    <Typography variant={"h5"} color={"primary"}
                                sx={{justifyContent: "center", display: "flex", mb: 2 }}
                    >
                        {data.label}
                    </Typography>
                    <Box sx={{display: "flex", width: "100%"}}>
                        <Box sx={{display: "flex", flexDirection: "column", alignItems: "center", width: "40%"}}>
                            <Typography variant={"body1"}>Input </Typography>
                        </Box>
                    </Box>
                    {dataInList}
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
