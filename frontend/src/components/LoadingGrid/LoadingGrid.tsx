import React from 'react';
import { Skeleton, Card, CardContent, CardActions } from "@mui/material";
import Grid from '@mui/material/Unstable_Grid2';
import { isSmartphone } from '../../utils/functions';


const LoadingGrid: React.FC = () => {

    return (
        <Grid container spacing={isSmartphone() ? 2 : 3}>
            {Array.from(new Array(4)).map((_, index) => (
                <Grid xs={12} sm={6} lg={4} xl={3} sx={{height: 'auto', minHeight: '250px'}} key={index}>
                    <Card sx={{height: '100%', display: 'flex', flexDirection: 'column'}} variant={"outlined"}>
                        <CardContent sx={{flexGrow: 1}}>
                            <Skeleton variant={"rounded"} width={"60%"} height={32}/>
                            <Skeleton variant={"rounded"} width={"10%"} height={28} sx={{my: 2}}/>
                            <Skeleton variant={"text"} width={"80%"}/>
                            <Skeleton variant={"text"} width={"50%"}/>
                        </CardContent>
                        <CardActions sx={{p: 2}}>
                            <Skeleton variant={"rounded"} width={"20%"} height={32}/>
                        </CardActions>
                    </Card>
                </Grid>
            ))}
        </Grid>
    );
};

export default LoadingGrid;
