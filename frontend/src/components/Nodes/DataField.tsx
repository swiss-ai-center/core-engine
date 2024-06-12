import { Box, Card, CardActions, CardContent, Chip, Typography } from '@mui/material';
import React from 'react';

const DataField: React.FC<{
    inputField: { name: string; type: string[] }, index: number, data: any
}> = ({
          inputField,
          index,
          data
      }) => {

    return (
        <Box
            sx={{
                display: "flex",
                width: "100%",
                alignItems: "center",
                mb: index === data.length - 1 ? 0 : 1
            }}
            key={inputField.name}
        >
            <Card sx={{display: "flex", flexDirection: "column", justifyContent: "center", width: "100%"}}
                  key={index} variant={"outlined"}>
                <CardContent
                    sx={{justifyContent: "start", py: 0, paddingLeft: "10px", paddingTop: "3px"}}>
                    <Typography variant={"subtitle1"} alignContent={"start"}>
                        <b>{inputField.name}</b>
                    </Typography>
                </CardContent>
                <CardActions sx={{display: "flex", pt: 0}}>
                    {inputField.type.map((type: string) =>
                        <Chip key={`${inputField.name}${type}`}
                              size={"small"}
                              label={
                                  <Typography variant={"body2"}>{type}</Typography>
                              }/>)}
                </CardActions>
            </Card>
        </Box>
    );
}

export default DataField;
