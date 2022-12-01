import React from 'react';
import { Button, Card, CardActions, CardContent, Grid, Typography } from '@mui/material';
import { getPipelines, getServices } from '../../utils/api';
import { Link } from 'react-router-dom';

import "./styles.css";
import { useNotification } from '../../utils/useNotification';

const ItemGrid: React.FC = () => {
    const [pipelines, setPipelines] = React.useState([]);
    const [services, setServices] = React.useState([]);
    const {displayNotification} = useNotification();

    const listServices = async () => {
        const services = await getServices();
        if (services) {
            console.log(services);
            setServices(services);
        } else {
            setServices([]);
            displayNotification({message: "No services found", type: "info"});
        }
    }

    const listPipelines = async () => {
        const pipes = await getPipelines();
        if (pipes) {
            setPipelines(pipes);
        } else {
            setPipelines([]);
            displayNotification({message: "No pipelines found", type: "info"});
        }
    }

    React.useEffect(() => {
        listServices();
        listPipelines();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    return (
        <>
            <Typography gutterBottom variant="h4" component="h2" marginBottom={2}>
                Services
            </Typography>
            <Grid container spacing={4}>
                {services.length === 0 ? (
                    <Grid item xs={6} md={8}>
                        <Typography gutterBottom variant="h6" component="h2" marginBottom={2}>
                            No services found
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
                                            <a href={"/showcase?id=" + item.id + "&summary=" + item.summary + "&type=service"}>
                                                <Button size="small">View</Button>
                                            </a>
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
                            No pipelines found
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
                                            <Link to={"/showcase?id=" + item.id + "&summary=" + item.summary + "&type=pipeline"}>
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
