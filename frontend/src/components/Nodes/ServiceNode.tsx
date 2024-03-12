import React, {useState} from "react";
import {Handle, Position} from "react-flow-renderer";
import {Autocomplete, Card, CardActions, CardContent, TextField, Typography} from '@mui/material';
import {useSelector} from 'react-redux';
import {grey} from '@mui/material/colors';
import {DataTypeOptions} from "../../enums/dataTypeEnum";


const ServiceNode: React.FC<{ data: any }> = (
    {
        data,
    }) => {
    const lightgrey = grey[400];
    const darkgrey = grey[800];
    const colorMode = useSelector((state: any) => state.colorMode.value);
    const [selectedDataIn, setSelectedDataIn] = useState<string[]>([]);
    const [inputValue, setInputValue]  = React.useState<string>('')
    const [linked, setLinked]  = React.useState<boolean>(false)


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
                <CardContent sx={{flexGrow: 1, mb: -1, minWidth: "20em"}}>
                    <Typography variant={"subtitle1"} color={"primary"}
                                sx={{justifyContent: "center", display: "flex"}}
                    >
                        {data.label}
                    </Typography>

                    {selectedDataIn.map((dataType, index) => (
                        <Typography sx={{py: 0.3}} key={index}>{dataType}</Typography>
                    ))}

                    {linked ? (
                        <Autocomplete
                        sx={{mb: 2}}
                        value={inputValue}
                        blurOnSelect={false}
                        options={DataTypeOptions}
                        autoHighlight={false}
                        isOptionEqualToValue={(option, value) => value === "" || option === value}
                        renderOption={(props, option, {selected}) => (
                            <li {...props}>
                                {option}
                            </li>
                        )}
                        renderInput={(params) => (
                            <TextField {...params} label={"Data-In"} placeholder="Data-In" />
                        )}
                    />)
                        :
                        false
                    }
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
