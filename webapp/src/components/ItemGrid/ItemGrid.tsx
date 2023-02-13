import React from 'react';
import { Button, Card, CardActions, CardContent, Grid, Typography } from '@mui/material';
import { getPipelines, getServices } from '../../utils/api';
import { Link, useSearchParams } from 'react-router-dom';
import { useNotification } from '../../utils/useNotification';
import "./styles.css";


const ItemGrid: React.FC<{ filter: string, orderBy: string }> = ({filter, orderBy}) => {
    const [searchParams] = useSearchParams();
    const [pipelines, setPipelines] = React.useState([]);
    const [services, setServices] = React.useState([]);
    const {displayNotification} = useNotification();

    const listServices = async (filter: string, orderBy: string) => {
        const servicesList = await getServices(filter, orderBy);
        if (servicesList) {
            setServices(servicesList);
        } else {
            setServices([]);
            displayNotification({message: "No services found", type: "info"});
        }
    }

    const listPipelines = async (filter: string, orderBy: string) => {
        const pipelinesList = await getPipelines(filter, orderBy);
        if (pipelinesList) {
            setPipelines(pipelinesList);
        } else {
            setPipelines([]);
            displayNotification({message: "No pipelines found", type: "info"});
        }
    }

    React.useEffect(() => {
        listServices(filter, orderBy);
        listPipelines(filter, orderBy);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [filter, orderBy]);

    return (
        <>
            <Typography gutterBottom variant="h4" component="h2" marginBottom={2}>
                Services
            </Typography>
            <Grid container spacing={4}>
                {services.length === 0 ? (
                    <Grid item xs={6} md={8}>
                        <Typography gutterBottom variant="h6" component="h2" marginBottom={2}>
                            No service found
                        </Typography>
                    </Grid>
                ) : (
                    services.map((item: any, index: number) => {
                            return (
                                <Grid item xs={12} sm={6} md={4} key={index}>
                                    <Card
                                        sx={{height: '100%', display: 'flex', flexDirection: 'column'}}
                                    >
                                        <CardContent sx={{flexGrow: 1}}>
                                            <Typography gutterBottom variant="h5" component="h2">
                                                {item.name}
                                            </Typography>
                                            <Typography>
                                                {item.summary}
                                            </Typography>
                                        </CardContent>
                                        <CardActions>
                                            <Link
                                                to={"/showcase/service/"+item.id}>
                                                <Button size="small">View</Button>
                                            </Link>
                                        </CardActions>
                                    </Card>
                                </Grid>
                            );
                        }
                    ))}
            </Grid>
            <Typography gutterBottom variant="h4" component="h2" marginBottom={2} marginTop={4}>
                Pipelines
            </Typography>
            <Grid container spacing={4}>
                {pipelines.length === 0 ? (
                    <Grid item xs={6} md={8}>
                        <Typography gutterBottom variant="h6" component="h2" marginBottom={2}>
                            No pipeline found
                        </Typography>
                    </Grid>
                ) : (
                    pipelines.map((item: any, index: number) => {
                            return (
                                <Grid item xs={6} md={8} key={index}>
                                    <Card
                                        sx={{height: '100%', display: 'flex', flexDirection: 'column'}}
                                    >
                                        <CardContent sx={{flexGrow: 1}}>
                                            <Typography gutterBottom variant="h5" component="h2">
                                                {item.name}
                                            </Typography>
                                            <Typography>
                                                {item.summary}
                                            </Typography>
                                        </CardContent>
                                        <CardActions>
                                            <Link
                                                to={"/showcase/pipeline/"+item.id}
                                                state={{back: searchParams.toString()}}
                                            >
                                                <Button size="small">View</Button>
                                            </Link>
                                        </CardActions>
                                    </Card>
                                </Grid>
                            );
                        }
                    ))}
            </Grid></>
    );
}

export default ItemGrid;
