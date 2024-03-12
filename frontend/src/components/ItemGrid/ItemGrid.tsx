import React from 'react';
import {
    Box,
    Button,
    Card,
    CardActions,
    CardContent,
    Chip,
    Divider,
    FormControl,
    InputLabel,
    MenuItem,
    Pagination,
    Select,
    Tooltip,
    Typography,
} from '@mui/material';
import Grid from '@mui/material/Unstable_Grid2';
import { getPipelines, getServices } from '../../utils/api';
import { Link, useSearchParams } from 'react-router-dom';
import "./styles.css";
import { Tags } from '../../enums/tagEnums';
import { Tag } from '../../models/Tag';
import { useDispatch, useSelector } from 'react-redux';
import { setServicePerPage, setPipelinePerPage } from '../../utils/reducers/perPageSlice';
import { toast } from 'react-toastify';
import LoadingGrid from '../LoadingGrid/LoadingGrid';
import { Psychology } from '@mui/icons-material';
import { isSmartphone } from '../../utils/functions';
import ServiceCard from "../ServiceCard/ServiceCard";
import PipelineList from "./PipelineList";

// min width is 100% for mobile, 50% for tablet, 33% for desktop
const minWidth = isSmartphone() ? '100%' : (window.innerWidth < 900) ? '50%' : '33%';

// align center for mobile, left for tablet and desktop
const align = isSmartphone() ? 'center' : 'left';

const ItemGrid: React.FC<{
    filter: string, orderBy: string, tags: Tag[], handleTags: any, ai: boolean, handleAIToggle: any, addService: any
}> = ({filter, orderBy, tags, handleTags, ai, handleAIToggle, addService}) => {
    const dispatch = useDispatch();
    const servicesPerPage = useSelector((state: any) => state.perPage.value.services);
    const pipelinesPerPage = useSelector((state: any) => state.perPage.value.pipelines);
    const [serviceCount, setServiceCount] = React.useState(0);
    const [pipelineCount, setPipelineCount] = React.useState(0);
    const [pageService, setPageService] = React.useState(1);
    const [pagePipeline, setPagePipeline] = React.useState(1);
    const [isReady, setIsReady] = React.useState(false);
    const [searchParams] = useSearchParams();
    const [pipelines, setPipelines] = React.useState([]);
    const [services, setServices] = React.useState([]);

    const setServicesPerPage = (value: number) => {
        setPageService(1);
        dispatch(setServicePerPage(value));
    };

    const setPipelinesPerPage = (value: number) => {
        setPagePipeline(1);
        dispatch(setPipelinePerPage(value));
    }

    const listServices = async (filter: string, orderBy: string, tags: string[]) => {
        const skip = (pageService - 1) * servicesPerPage;
        const servicesList = await getServices(filter, skip, servicesPerPage, orderBy, tags, ai);
        if (servicesList.services) {
            if (servicesList.services.length === 0) {
                setServices([]);
                setServiceCount(0);
                toast("No service found", {type: "info"});
            } else {
                setServices(servicesList.services);
                setServiceCount(servicesList.count);
            }
        } else {
            setServices([]);
            setServiceCount(0);
            toast(`Error while fetching services: ${servicesList.error}`, {type: "error"});
        }
    }

    const listPipelines = async (filter: string, orderBy: string, tags: string[]) => {
        const skip = (pagePipeline - 1) * pipelinesPerPage;
        const pipelinesList = await getPipelines(filter, skip, pipelinesPerPage, orderBy, tags);
        if (pipelinesList.pipelines) {
            if (pipelinesList.pipelines.length === 0) {
                setPipelines([]);
                setPipelineCount(0);
                toast("No pipeline found", {type: "info"});
            } else {
                setPipelines(pipelinesList.pipelines);
                setPipelineCount(pipelinesList.count);
            }
        } else {
            setPipelines([]);
            setPipelineCount(0);
            toast(`Error while fetching pipelines: ${pipelinesList.error}`, {type: "error"});
        }
    }

    const listElements = async (filter: string, orderBy: string, tags: string[]) => {
        await listServices(filter, orderBy, tags);
        await listPipelines(filter, orderBy, tags);
        setIsReady(true);
    }

    const servicePagination = () => {
        return (
            <Grid container sx={{py: 1}} spacing={4} alignItems={"center"} justifyContent={"center"}>
                <Grid xs={12} md={6} lg={4} alignItems={"left"} justifyContent={"left"}>
                    <Box sx={{display: 'flex', alignItems: align, justifyContent: align}}>
                        <Pagination
                            page={pageService}
                            size={"large"}
                            onChange={(event, page) => {
                                setPageService(page);
                            }}
                            sx={{alignItems: 'center', justifyContent: 'center'}}
                            count={Math.ceil(serviceCount / servicesPerPage) || 1}
                            shape={"rounded"}
                            disabled={!isReady || services.length <= 0}
                        />
                    </Box>
                </Grid>
                <Grid xs={12} md={6} lg={4} mdOffset={"auto"} alignItems={"right"} justifyContent={"right"}>
                    <Box sx={{display: 'flex', alignItems: 'right', justifyContent: 'right'}}>
                        <FormControl sx={{minWidth: minWidth}}>
                            <InputLabel id={"services-per-page-label"} htmlFor={"services-per-page"}>Per
                                page</InputLabel>
                            <Select
                                labelId={"services-per-page-label"}
                                id={"services-per-page"}
                                value={servicesPerPage}
                                label={"Per page"}
                                onChange={(event) => {
                                    setServicesPerPage(event.target.value as number);
                                }}
                                disabled={!isReady || services.length <= 0}
                            >
                                <MenuItem value={6}>6</MenuItem>
                                <MenuItem value={15}>15</MenuItem>
                                <MenuItem value={30}>30</MenuItem>
                                <MenuItem value={60}>60</MenuItem>
                            </Select>
                        </FormControl>
                    </Box>
                </Grid>
            </Grid>
        );
    };

    const pipelinePagination = () => {
        return (
            <Grid container sx={{py: 1}} spacing={4} alignItems={"center"} justifyContent={"center"}>
                <Grid xs={12} md={6} lg={4} alignItems={"left"} justifyContent={"left"}>
                    <Box sx={{display: 'flex', alignItems: align, justifyContent: align}}>
                        <Pagination
                            page={pagePipeline}
                            size={"large"}
                            onChange={(event, page) => {
                                setPagePipeline(page);
                            }}
                            sx={{alignItems: 'center', justifyContent: 'center'}}
                            count={Math.ceil(pipelineCount / pipelinesPerPage) || 1}
                            shape={"rounded"}
                            disabled={!isReady || pipelines.length <= 0}
                        />
                    </Box>
                </Grid>
                <Grid xs={12} md={6} lg={4} mdOffset={"auto"} alignItems={"right"} justifyContent={"right"}>
                    <Box sx={{display: 'flex', alignItems: 'right', justifyContent: 'right'}}>
                        <FormControl sx={{minWidth: minWidth}}>
                            <InputLabel id={"pipelines-per-page-label"} htmlFor={"pipelines-per-page"}>Per
                                page</InputLabel>
                            <Select
                                labelId={"pipelines-per-page"}
                                id={"pipelines-per-page"}
                                value={pipelinesPerPage}
                                label={"Per page"}
                                onChange={(event) => {
                                    setPipelinesPerPage(event.target.value as number);
                                }}
                                disabled={!isReady || pipelines.length <= 0}
                            >
                                <MenuItem value={6}>6</MenuItem>
                                <MenuItem value={15}>15</MenuItem>
                                <MenuItem value={30}>30</MenuItem>
                                <MenuItem value={60}>60</MenuItem>
                            </Select>
                        </FormControl>
                    </Box>
                </Grid>
            </Grid>
        );
    };

    React.useEffect(() => {
        setPageService(1);
        setPagePipeline(1);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [servicesPerPage, pipelinesPerPage]);

    React.useEffect(() => {
        setPageService(1);
        setPagePipeline(1);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [filter]);

    React.useEffect(() => {
        // on filter change, use listElements to update the list only if the user stopped typing for 300ms
        const timeout = setTimeout(() => {
            setIsReady(false);
            listElements(filter, orderBy, tags.map(t => t.acronym));
        }, 300);
        return () => clearTimeout(timeout);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [filter, pageService, pagePipeline, orderBy, tags, ai, servicesPerPage, pipelinesPerPage]);

    return (
        <>
            <Typography gutterBottom variant={"h4"} component={"h2"}>
                Services <Chip label={isReady ? serviceCount : 0} variant={"outlined"} color={"secondary"}
                               size={"small"} style={{marginTop: "-2px"}}/>
            </Typography>
            {(isReady && services.length > 0) || !isReady ? servicePagination() : <></>}
            {!isReady ?
                <LoadingGrid/>
                :
                <Grid container spacing={isSmartphone() ? 2 : 3}>
                    {services.length === 0 ? (
                        <Grid xs={6} md={8}>
                            <Typography gutterBottom variant={"h6"} component={"h2"}>
                                No service found
                            </Typography>
                        </Grid>
                    ) : (
                        services.map((item: any, index: number) => (
                            <ServiceCard
                                key={index}
                                index={index}
                                item={item}
                                tags={tags}
                                handleTags={handleTags}
                                ai={ai}
                                handleAIToggle={handleAIToggle}
                                addService={addService}
                            />
                        )))}
                </Grid>
            }
            {!addService && (
                <>
                    {(isReady && services.length > 0) || !isReady ? servicePagination() : <></>}
                    <Divider sx={{mt: 2, mb: 2}}>
                        ○
                    </Divider>
                    <PipelineList pipelineCount={pipelineCount} isReady={isReady} tags={tags} handleTags={handleTags}
                                  pipelinePagination={pipelinePagination} pipelines={pipelines}
                                  searchParams={searchParams}/>
                </>
            )}
        </>
    );
}

export default ItemGrid;
