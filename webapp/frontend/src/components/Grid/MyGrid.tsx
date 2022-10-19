import React from 'react';
import { Button, Card, CardActions, CardContent, CardMedia, Grid, Typography } from '@mui/material';
import { getPipelines, getServices } from '../../utils/api';

class MyGrid extends React.Component<any, any> {

    constructor(props: any) {
        super(props);
        this.state = {services: [], pipelines: []};
    }

    componentDidMount() {
        this.listServices();
        this.listPipelines();
    }

    listServices = async () => {
        getServices().then((response: any) => {
            this.setState({services: response});
            console.log(this.state);
        });
    }

    listPipelines = async () => {
        getPipelines().then((response: any) => {
            this.setState({pipelines: response});
            console.log(this.state);
        });
    }

    render() {
        return (
            <>
                <Typography gutterBottom variant="h4" component="h2" marginBottom={2}>
                    Services
                </Typography>
                <Grid container spacing={4}>
                    {this.state.services.map((item: any, index: number) => {
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
                                            <Button size="small">View</Button>
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
                    {this.state.pipelines.map((item: any, index: number) => {
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
                                            <Button size="small">View</Button>
                                        </CardActions>
                                    </Card>
                                </Grid>
                            );
                        }
                    )}
                </Grid></>
        );
    }
}

export default MyGrid;
