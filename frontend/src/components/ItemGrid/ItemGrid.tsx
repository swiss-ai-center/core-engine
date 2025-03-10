import {
    Box,
    Button,
    Chip,
    Divider,
    FormControl,
    InputLabel,
    MenuItem,
    Pagination,
    Select,
    Typography,
    Grid
} from '@mui/material';
import { Tag } from 'models/Tag';
import React, { ReactNode } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate, useSearchParams } from 'react-router-dom';
import "./styles.css";
import { toast } from 'react-toastify';
import { getPipelines, getServices } from 'utils/api';
import { isSmartphone } from 'utils/functions';
import { setPipelinePerPage, setServicePipelineEditorPerPage, setServicePerPage } from 'utils/reducers/perPageSlice';
import LoadingGrid from 'components/LoadingGrid/LoadingGrid';

// min width is 100% for mobile, 50% for tablet, 33% for desktop
const minWidth = isSmartphone() ? '100%' : (window.innerWidth < 900) ? '82%' : '66%';

// align center for mobile, left for tablet and desktop
const align = isSmartphone() ? 'center' : 'left';

const distance = isSmartphone() ? 2 : 3;

const ItemGrid: React.FC<{
    filter: string, orderBy: string, tags: Tag[], handleTags: any, ai: boolean, handleAIToggle: any,
    items: any, itemFunctions: any, paginationOptions: number[], paginationPositions: string[], displayedPage: string
}> = ({
          filter,
          orderBy,
          tags,
          handleTags,
          ai,
          handleAIToggle,
          items,
          itemFunctions,
          paginationOptions,
          paginationPositions,
          displayedPage,
      }) => {
    const dispatch = useDispatch();
    const servicesPerPage = useSelector((state: any) => state.perPage.value.services);
    const servicesPipelineEditorPerPage = useSelector((state: any) => state.perPage.value.servicesPipelineEditor);
    const pipelinesPerPage = useSelector((state: any) => state.perPage.value.pipelines);
    const [serviceCount, setServiceCount] = React.useState(0);
    const [pipelineCount, setPipelineCount] = React.useState(0);
    const [pageService, setPageService] = React.useState(1);
    const [pagePipeline, setPagePipeline] = React.useState(1);
    const [isReady, setIsReady] = React.useState(false);
    const [searchParams] = useSearchParams();
    const [pipelines, setPipelines] = React.useState([]);
    const [services, setServices] = React.useState([]);
    const navigate = useNavigate();

    const navigateToPipelineEditor = () => {
        navigate("/pipeline-editor");
    }

    const setServicesPerPage = (value: number) => {
        setPageService(1);
        if (displayedPage === "home") {
            dispatch(setServicePerPage(value));
        } else if (displayedPage === "pipeline-editor") {
            dispatch(setServicePipelineEditorPerPage(value));
        }
    };

    const setPipelinesPerPage = (value: number) => {
        setPagePipeline(1);
        dispatch(setPipelinePerPage(value));
    }

    const servicePagination = () => {
        return (
            <Grid container sx={{py: distance}} spacing={4} alignItems={"center"} justifyContent={"center"}>
                <Grid xs={12} sm={9} alignItems={"left"} justifyContent={"left"} item>
                    <Box sx={{display: 'flex', alignItems: align, justifyContent: align}}>
                        <Pagination
                            page={pageService}
                            size={"large"}
                            onChange={(_, page) => {
                                setPageService(page);
                            }}
                            sx={{alignItems: 'center', justifyContent: 'center'}}
                            count={
                                displayedPage === "home" ?
                                    Math.ceil(serviceCount / servicesPerPage) || 1 :
                                    Math.ceil(serviceCount / servicesPipelineEditorPerPage) || 1
                            }
                            shape={"rounded"}
                            disabled={!isReady || services.length <= 0}
                            siblingCount={0}
                        />
                    </Box>
                </Grid>
                <Grid xs={12} sm={3} alignItems={"right"} justifyContent={"right"} item>
                    <Box sx={{display: 'flex', alignItems: 'right', justifyContent: 'right'}}>
                        <FormControl sx={{minWidth: minWidth}}>
                            <InputLabel id={"services-per-page-label"} htmlFor={"services-per-page"}>Per
                                page</InputLabel>
                            <Select
                                labelId={"services-per-page-label"}
                                id={"services-per-page"}
                                value={
                                    displayedPage === "home" && paginationOptions.includes(servicesPerPage) ?
                                        servicesPerPage :
                                        displayedPage === "pipeline-editor" && paginationOptions.includes(servicesPipelineEditorPerPage) ?
                                            servicesPipelineEditorPerPage :
                                            paginationOptions[0]
                                }
                                label={"Per page"}
                                onChange={(event) => {
                                    setServicesPerPage(event.target.value as number);
                                }}
                                disabled={!isReady || services.length <= 0}
                            >
                                {paginationOptions.map((option: number) => {
                                    return (
                                        <MenuItem key={option} value={option}>{option}</MenuItem>
                                    );
                                })}
                            </Select>
                        </FormControl>
                    </Box>
                </Grid>
            </Grid>
        );
    };

    const pipelinePagination = () => {
        return (
            <Grid container sx={{py: distance}} spacing={4} alignItems={"center"} justifyContent={"center"}>
                <Grid xs={12} sm={9} alignItems={"left"} justifyContent={"left"} item>
                    <Box sx={{display: 'flex', alignItems: align, justifyContent: align}}>
                        <Pagination
                            page={pagePipeline}
                            size={"large"}
                            onChange={(_, page) => {
                                setPagePipeline(page);
                            }}
                            sx={{alignItems: 'center', justifyContent: 'center'}}
                            count={Math.ceil(pipelineCount / pipelinesPerPage) || 1}
                            shape={"rounded"}
                            disabled={!isReady || pipelines.length <= 0}
                            siblingCount={0}
                        />
                    </Box>
                </Grid>
                <Grid xs={12} sm={3} alignItems={"right"} justifyContent={"right"} item>
                    <Box sx={{display: 'flex', alignItems: 'right', justifyContent: 'right'}}>
                        <FormControl sx={{minWidth: minWidth}}>
                            <InputLabel id={"pipelines-per-page-label"} htmlFor={"pipelines-per-page"}>Per
                                page</InputLabel>
                            <Select
                                labelId={"pipelines-per-page"}
                                id={"pipelines-per-page"}
                                value={paginationOptions.includes(pipelinesPerPage) ? pipelinesPerPage : paginationOptions[0]}
                                label={"Per page"}
                                onChange={(event) => {
                                    setPipelinesPerPage(event.target.value as number);
                                }}
                                disabled={!isReady || pipelines.length <= 0}
                            >
                                {paginationOptions.map((option: number) => {
                                    return (
                                        <MenuItem key={option} value={option}>{option}</MenuItem>
                                    );
                                })}
                            </Select>
                        </FormControl>
                    </Box>
                </Grid>
            </Grid>
        );
    };

    const serviceCard = (item: any, index: number): ReactNode => {
        const ServiceCard = items?.service
        return (
            <ServiceCard index={index} item={item} tags={tags} handleTags={handleTags} ai={ai}
                         handleAIToggle={handleAIToggle}
                         functions={itemFunctions}></ServiceCard>
        )
    }


    const pipelineCard = (item: any, index: number): ReactNode => {
        const PipelineCard = items?.pipeline;
        return (
            <PipelineCard index={index} item={item} tags={tags} handleTags={handleTags} searchParams={searchParams}
                          functions={itemFunctions}></PipelineCard>
        )
    }

    React.useEffect(() => {
        setPageService(1);
        setServicePipelineEditorPerPage(1);
        setPagePipeline(1);
    }, [servicesPerPage, servicesPipelineEditorPerPage, pipelinesPerPage]);

    React.useEffect(() => {
        setPageService(1);
        setPagePipeline(1);
    }, [filter]);

    React.useEffect(() => {
        const listServices = async (filter: string, orderBy: string, tags: string[]) => {
            let servicesList, skip;
            if (displayedPage === "pipeline-editor") {
                skip = (pageService - 1) * servicesPipelineEditorPerPage;
                servicesList = await getServices(filter, skip, servicesPipelineEditorPerPage, orderBy, tags, ai);
            } else {
                skip = (pageService - 1) * servicesPerPage;
                servicesList = await getServices(filter, skip, servicesPerPage, orderBy, tags, ai);
            }
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
            if (items?.service) await listServices(filter, orderBy, tags);
            if (items?.pipeline) await listPipelines(filter, orderBy, tags);
            setIsReady(true);
        }

        // on filter change, use listElements to update the list only if the user stopped typing for 300ms
        const timeout = setTimeout(() => {
            setIsReady(false);
            listElements(filter, orderBy, tags.map(t => t.acronym));
        }, 300);
        return () => clearTimeout(timeout);
    }, [filter, pageService, pagePipeline, orderBy, tags, ai, servicesPerPage, servicesPipelineEditorPerPage, pipelinesPerPage, items]);

    return (
        <Box>
            {items?.service &&
                <Box>
                    <Typography gutterBottom variant={"h4"} component={"h2"}>
                        Services <Chip label={isReady ? serviceCount : 0} variant={"outlined"} color={"secondary"}
                                       size={"small"} style={{marginTop: "-2px"}}/>
                    </Typography>
                    {((isReady && services.length > 0) || !isReady) && paginationPositions.includes("top") ? servicePagination() : <></>}
                    {!isReady ?
                        <LoadingGrid/>
                        :
                        <Grid container spacing={distance}>
                            {services.length === 0 ? (
                                <Grid xs={6} md={8} item>
                                    <Typography gutterBottom variant={"h6"} component={"h2"}>
                                        No service found
                                    </Typography>
                                </Grid>
                            ) : (
                                services.map((item: any, index: number) => {
                                    return (
                                        <Grid xs={12} sm={6} lg={4} xl={3} key={index} item
                                              sx={{height: 'auto', minHeight: '250px'}}>
                                            {serviceCard(item, index)}
                                        </Grid>

                                    );
                                }))}
                        </Grid>
                    }
                    {((isReady && services.length > 0) || !isReady) && paginationPositions.includes("bottom") ? servicePagination() : <></>}
                </Box>
            }
            {items?.service && items?.pipeline ?
                <Divider sx={{mt: 2, mb: 2}}>
                    ○
                </Divider>
                : false
            }
            {items?.pipeline &&
                <Box>
                    <Box sx={{display: "flex", justifyContent: "space-between", alignItems: "center", mb: "5px"}}>
                        <Typography gutterBottom variant={"h4"} component={"h2"}>
                            Pipelines <Chip label={isReady ? pipelineCount : 0} variant={"outlined"} color={"secondary"}
                                            size={"small"} style={{marginTop: "-2px"}}/>
                        </Typography>
                        <Button
                            variant={"contained"}
                            disableElevation
                            color={"secondary"}
                            onClick={navigateToPipelineEditor}
                            hidden={isSmartphone()}
                        >
                            Create Pipeline
                        </Button>
                    </Box>
                    {((isReady && pipelines.length > 0) || !isReady) && paginationPositions.includes("top") ? pipelinePagination() : <></>}
                    {!isReady ?
                        <LoadingGrid/>
                        :
                        <Grid container spacing={distance}>
                            {pipelines.length === 0 ? (
                                <Grid xs={6} md={8} item>
                                    <Typography gutterBottom variant={"h6"} component={"h2"}>
                                        No pipeline found
                                    </Typography>
                                </Grid>
                            ) : (
                                pipelines.map((item: any, index: number) => {
                                    return (

                                        <Grid xs={12} sm={6} lg={4} xl={3} key={index} item
                                              sx={{height: 'auto', minHeight: '250px'}}>
                                            {pipelineCard(item, index)}
                                        </Grid>
                                    );
                                }))}
                        </Grid>
                    }
                    {((isReady && pipelines.length > 0) || !isReady) && paginationPositions.includes("bottom") ? pipelinePagination() : <></>}
                </Box>
            }

        </Box>
    );
}

export default ItemGrid;
