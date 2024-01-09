import React from 'react';
import { Skeleton, Card, Grid, CardContent, CardActions } from "@mui/material";


const LoadingGrid: React.FC = () => {

    return (
        <Grid container spacing={4}>
            {Array.from(new Array(3)).map((_, index) => (
                <Grid item xs={12} sm={6} xl={4} sx={{height: 'auto', minHeight: '200px'}} key={index}>
                    <Card sx={{height: '100%', display: 'flex', flexDirection: 'column'}}>
                        <CardContent>
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
