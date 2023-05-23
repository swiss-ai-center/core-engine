import React from 'react';
import { Button, Card, CardActions, CardContent, Chip, Grid, Tooltip, Typography } from '@mui/material';
import { getPipelines, getServices } from '../../utils/api';
import { Link, useSearchParams } from 'react-router-dom';
import { useNotification } from '../../utils/useNotification';
import "./styles.css";
import { Tags } from '../../enums/tagEnums';
import { Tag } from '../../models/Tag';


const ItemGrid: React.FC<{
    filter: string, skip: number, limit: number, orderBy: string, tags: Tag[]
}> = ({filter, skip, limit, orderBy, tags}) => {
    const [searchParams] = useSearchParams();
    const [pipelines, setPipelines] = React.useState([]);
    const [services, setServices] = React.useState([]);
    const {displayNotification} = useNotification();

    const listServices = async (filter: string, orderBy: string, tags: string[]) => {
        const servicesList = await getServices(filter, skip, limit, orderBy, tags);
        if (servicesList) {
            setServices(servicesList);
        } else {
            setServices([]);
            displayNotification({message: "No services found", type: "info"});
        }
    }

    const listPipelines = async (filter: string, orderBy: string, tags: string[]) => {
        const pipelinesList = await getPipelines(filter, skip, limit, orderBy, tags);
        if (pipelinesList) {
            setPipelines(pipelinesList);
        } else {
            setPipelines([]);
            displayNotification({message: "No pipelines found", type: "info"});
        }
    }

    React.useEffect(() => {
        listServices(filter, orderBy, tags.map(t => t.acronym));
        listPipelines(filter, orderBy, tags.map(t => t.acronym));
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [filter, orderBy, tags]);

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
                                <Grid item xs={12} sm={6} xl={4} key={index} sx={{height: 'auto', minHeight: '200px'}}>
                                    <Card
                                        sx={{height: '100%', display: 'flex', flexDirection: 'column'}}
                                    >
                                        <CardContent sx={{flexGrow: 1}}>
                                            <Typography variant="h5" component="h2" gutterBottom>
                                                {item.name}
                                            </Typography>
                                            <Grid container spacing={1} sx={{mb: 2}}>
                                                {item.tags ? item.tags.map((tag: any, index: number) => {
                                                    return (
                                                        <Grid item key={`service-tag-${index}`}>
                                                            <Tooltip title={tag.name}>
                                                                <Chip
                                                                    className={"acronym-chip"}
                                                                    label={tag.acronym}
                                                                    style={
                                                                        Tags.filter((t) =>
                                                                            t.acronym === tag.acronym)[0].colors
                                                                    }
                                                                    variant="outlined"
                                                                    size={"small"}
                                                                />
                                                            </Tooltip>
                                                        </Grid>
                                                    )
                                                }) : ''}
                                            </Grid>
                                            <Typography>
                                                {
                                                    item.summary.length > 80 ?
                                                        item.summary.substring(0, 75) + "..." :
                                                        item.summary
                                                }
                                            </Typography>
                                        </CardContent>
                                        <CardActions sx={{p: 2}}>
                                            <Link
                                                to={"/showcase/service/" + item.id}>
                                                <Button size={"small"} variant={"contained"}>View</Button>
                                            </Link>
                                        </CardActions>
                                    </Card>
                                </Grid>
                            )
                                ;
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
                                <Grid item xs={12} sm={6} xl={4} key={index}
                                      sx={{height: 'auto', minHeight: '200px'}}>
                                    <Card
                                        sx={{height: '100%', display: 'flex', flexDirection: 'column'}}
                                    >
                                        <CardContent sx={{flexGrow: 1}}>
                                            <Typography gutterBottom variant="h5" component="h2">
                                                {item.name}
                                            </Typography>
                                            <Grid container spacing={1} sx={{mb: 2}}>
                                                {item.tags ? item.tags.map((tag: any, index: number) => {
                                                    return (
                                                        <Grid item key={`pipeline-tag-${index}`}>
                                                            <Tooltip title={tag.name}>
                                                                <Chip
                                                                    className={"acronym-chip"}
                                                                    label={tag.acronym}
                                                                    style={
                                                                        Tags.filter((t) =>
                                                                            t.acronym === tag.acronym)[0].colors
                                                                    }
                                                                    variant="outlined"
                                                                    size={"small"}
                                                                />
                                                            </Tooltip>
                                                        </Grid>
                                                    )
                                                }) : ''}
                                            </Grid>
                                            <Typography>
                                                {item.summary}
                                            </Typography>
                                        </CardContent>
                                        <CardActions sx={{p: 2}}>
                                            <Link
                                                to={"/showcase/pipeline/" + item.id}
                                                state={{back: searchParams.toString()}}
                                            >
                                                <Button size={"small"} variant={"contained"}>View</Button>
                                            </Link>
                                        </CardActions>
                                    </Card>
                                </Grid>
                            );
                        }
                    ))}
            </Grid>
        </>
    );
}

export default ItemGrid;
