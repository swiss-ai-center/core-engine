import React from 'react';
import { Button, Card, CardActions, CardContent, Grid, Typography } from '@mui/material';
import { getServices } from '../../utils/api';
import { Link } from 'react-router-dom';

import "./styles.css";

const MyGrid: React.FC = () => {
    const [pipelines, setPipelines] = React.useState([]);
    const [services, setServices] = React.useState([]);

    const listServices = async () => {
        const services = await getServices();
        if (services) {
            setServices(services);
        } else {
            setServices([]);
            console.log("No services found");
        }
    }

    const listPipelines = async () => {
        const pipes = await getServices('pipeline');
        if (pipes) {
            console.log(pipes);
            setPipelines(pipes);
        } else {
            setPipelines([]);
            console.log("No pipelines found");
        }
    }

    React.useEffect(() => {
        listServices();
        listPipelines();
    }, []);

    return (
        <>
            <Typography gutterBottom variant="h4" component="h2" marginBottom={2}>
                Services
            </Typography>
            <Grid container spacing={4}>
                {services.map((item: any, index: number) => {
                        return (
                            <Grid item xs={12} sm={6} md={4} key={index}>
                                <Card
                                    sx={{height: '100%', display: 'flex', flexDirection: 'column'}}
                                >
                                    <CardContent sx={{flexGrow: 1}}>
                                        <Typography gutterBottom variant="h5" component="h2">
                                            {item.nodes[0].api.route}
                                        </Typography>
                                        <Typography>
                                            {item.nodes[0].api.summary}
                                        </Typography>
                                    </CardContent>
                                    <CardActions>
                                        <a href={"/showcase?name=" + item.nodes[0].api.route + "&summary=" + item.nodes[0].api.summary}>
                                            <Button size="small">View</Button>
                                        </a>
                                    </CardActions>
                                </Card>
                            </Grid>
                        );
                    }
                )}
            </Grid>
            <Typography gutterBottom variant="h4" component="h2" marginBottom={2} marginTop={4}>
                Pipelines
            </Typography>
            <Grid container spacing={4}>
                {pipelines.map((item: any, index: number) => {
                        return (
                            <Grid item xs={6} md={8} key={index}>
                                <Card
                                    sx={{height: '100%', display: 'flex', flexDirection: 'column'}}
                                >
                                    <CardContent sx={{flexGrow: 1}}>
                                        <Typography gutterBottom variant="h5" component="h2">
                                            {item.nodes[0].api.route}
                                        </Typography>
                                        <Typography>
                                            {item.nodes[0].api.summary}
                                        </Typography>
                                    </CardContent>
                                    <CardActions>
                                        <Link to={"/showcase?name=" + item.nodes[0].api.route}>
                                            <Button size="small">View</Button>
                                        </Link>
                                    </CardActions>
                                </Card>
                            </Grid>
                        );
                    }
                )}
            </Grid></>
    );
}

export default MyGrid;
