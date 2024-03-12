import React, {useState} from "react";
import { Handle, Position } from "react-flow-renderer";
import {
    Autocomplete, AutocompleteChangeDetails, AutocompleteChangeReason,
    Card,
    CardActions,
    CardContent,
    TextField,
    Typography
} from '@mui/material';
import { useDispatch, useSelector } from 'react-redux';
import { grey } from '@mui/material/colors';
import {DataType, DataTypeOptions} from "../../enums/dataTypeEnum";
import {NodeProps} from "reactflow";


export type EntryNodeData = {
    dataIn: DataType[];
};
export default function EntryNodeEdit(props: NodeProps<EntryNodeData>) {
    const lightgrey = grey[400];
    const darkgrey = grey[800];
    const colorMode = useSelector((state: any) => state.colorMode.value);
    const [dataIn, setDataIn] = useState<DataType[]>([]);
    const [inputValue, setInputValue]  = React.useState<string>('')

    const handleDataInSelect = (event: React.SyntheticEvent<Element, Event>, value: string | null, reason: string) => {
        if (!value) return;
        setDataIn(dataIn.concat(value as DataType));
    };

    const handleResetInput = (event: React.SyntheticEvent<Element, Event>, value: string | null, reason: string) => {
        if(reason === 'reset') setInputValue("");
    };

    return (
        <>
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
                                sx={{justifyContent: "center", display: "flex"}}>
                        Entry Node
                    </Typography>

                    {dataIn.map((dataType, index) => (
                        <Typography sx={{py: 0.3}} key={index}>{dataType}</Typography>
                    ))}

                    <Autocomplete
                        sx={{mb: 2}}
                        value={inputValue}
                        options={DataTypeOptions}
                        autoHighlight={false}
                        isOptionEqualToValue={(option, value) => value === "" || option === value}
                        renderOption={(props, option, {selected}) => (
                            <li {...props}>
                                {option}
                            </li>
                        )}
                        onChange={handleDataInSelect}
                        onInputChange={handleResetInput}
                        renderInput={(params) => (
                            <TextField {...params} label={"Data-In"} placeholder="Data-In" />
                        )}
                    />
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
