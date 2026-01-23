import {
    ApiRounded,
    ArrowBack,
    ArrowUpward,
    DescriptionTwoTone,
    NotificationsPausedTwoTone,
} from '@mui/icons-material';
import { Box, Button, CircularProgress, Container, Grid, Link as URLLink, Toolbar, Tooltip, } from '@mui/material';
import Board from 'components/Board/Board';
import Copyright from 'components/Copyright/Copyright';
import { InformationDrawer } from 'components/InformationDrawer/InformationDrawer';
import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Link, useNavigate, useParams } from 'react-router-dom';
import ScrollToTop from 'react-scroll-to-top';
import { toast } from 'react-toastify';
import { ReactFlowProvider } from 'reactflow';
import { getPipelineDescription, getServiceDescription, getServiceDescriptionById, wakeUp } from 'utils/api';
import { isSmartphone } from 'utils/functions';
import { setMenuIcon } from 'utils/reducers/menuIconSlice';
import { ServiceStatus } from '../../enums/serviceStatusEnum';


const Showcase: React.FC<{ mobileOpen: boolean }> = ({mobileOpen}) => {
    const dispatch = useDispatch();
    const params = useParams();
    const navigate = useNavigate();
    const colorMode = useSelector((state: any) => state.colorMode.value);
    const [isReady, setIsReady] = React.useState(false);
    const [wakingUp, setWakingUp] = React.useState(false);

    const [description, setDescription] = React.useState<any>(null);

    React.useEffect(() => {
        dispatch(setMenuIcon(true));
    });

    React.useEffect(() => {
        const navigateHome = () => {
            navigate("/home");
        }

        const getDescription = async (slug: string, type: string) => {
            setIsReady(false);
            if (!slug || !type) {
                toast("No slug or type provided", {type: "warning"});
                navigateHome();
            }
            let desc: any = {};
            try {
                if (type === 'service') {
                    desc = await getServiceDescription(slug);
                } else {
                    desc = await getPipelineDescription(slug);
                }
                if (desc) {
                    if (type !== 'service') {
                        const steps = desc.steps
                        const stepsDescriptions = await Promise.all(steps.map((step: any) => getServiceDescriptionById(step.service_id)));
                        for (let i = 0; i < steps.length; i++) {
                            steps[i].service = stepsDescriptions[i];
                        }
                        desc.steps = steps;
                    }
                    if ((desc as any).status === ServiceStatus.AVAILABLE) {
                        setDescription(desc);
                    } else {
                        toast("This service or pipeline is actually not available", {type: "warning"});
                        navigateHome();
                    }
                } else {
                    toast("No description found with this slug", {type: "warning"});
                    navigateHome();
                }
                setIsReady(true);
            } catch (e: any) {
                toast("No description found with this slug", {type: "warning"});
                navigateHome();
            }
        }

        const slug = params.slug as string;
        const type = params.type as string;

        getDescription(slug, type);
    }, [navigate, params]);

    const areAllServicesAwake = () => {
        if (!description || !description.steps) return true;
        return description.steps.every((step: any) => step.service.status !== ServiceStatus.SLEEPING);
    };

    const wakeUpAllServices = async () => {
        if (!description || !description.steps) return;

        try {
            setWakingUp(true);
            toast("Sending wake up requests to all services...", {type: "info"});

            const wakeUpPromises = description.steps.map((step: any) =>
                wakeUp(step.service_id)
            );

            const results = await Promise.all(wakeUpPromises);

            const successCount = results.filter((r: any) => r.status === 204).length;
            const failCount = results.length - successCount;

            if (failCount === 0) {
                toast(`All ${successCount} services woken up successfully`, {type: "success"});
            } else if (successCount === 0) {
                toast(`Failed to wake up all services`, {type: "error"});
            } else {
                toast(`${successCount} services woken up, ${failCount} failed`, {type: "warning"});
            }
        } catch (e: any) {
            toast("Error while sending wake up requests: " + e.message, {type: "error"});
        } finally {
            setWakingUp(false);
        }
    };

    return (
        <>
            {isReady ?
                <Box sx={{display: "flex"}}>
                    <ScrollToTop smooth
                                 component={<ArrowUpward style={{color: (colorMode === 'light' ? 'white' : 'black')}}
                                                         sx={{paddingTop: '2px'}}/>}/>
                    <InformationDrawer mobileOpen={mobileOpen} description={description}/>
                    <Box component={"main"}
                         sx={{display: 'flex', flexDirection: 'column', minHeight: '100vh', flexGrow: 1}}>
                        <Toolbar/>
                        <Container maxWidth={false} sx={{py: 2}}>
                            <Grid container spacing={2} justifyContent={"space-between"}
                                  sx={{py: isSmartphone() ? 0 : 1}}>
                                <Grid item>
                                    <Link to={"/home"} style={{textDecoration: "none"}}>
                                        <Button variant={"outlined"} color={"secondary"} startIcon={<ArrowBack/>}>
                                            Back
                                        </Button>
                                    </Link>
                                </Grid>
                                {params.type as string === "service" ? (
                                    <Grid item>
                                        {description.docs_url ? (
                                            <URLLink href={description.docs_url} target={"_blank"}
                                                     sx={{paddingRight: 1}}>
                                                <Button color={"secondary"} variant={"outlined"}
                                                        startIcon={<DescriptionTwoTone/>}>
                                                    Docs
                                                </Button>
                                            </URLLink>) : <></>}
                                        <URLLink href={description.url} target={"_blank"}>
                                            <Button color={"secondary"} variant={"outlined"}
                                                    startIcon={<ApiRounded/>}>
                                                API
                                            </Button>
                                        </URLLink>
                                    </Grid>
                                ) : (
                                    <Tooltip
                                        title={areAllServicesAwake() ? "All services are already awake" : wakingUp ? "Services are waking up" : "Wake up all services"}>
                                        <Grid item>
                                            <Button
                                                color={"secondary"}
                                                variant={"contained"}
                                                startIcon={<NotificationsPausedTwoTone/>}
                                                onClick={wakeUpAllServices}
                                                disabled={wakingUp || areAllServicesAwake()}
                                                disableElevation
                                            >
                                                Wake up all services
                                            </Button>
                                        </Grid>
                                    </Tooltip>
                                )}
                            </Grid>
                        </Container>
                        <Container maxWidth={false}>
                            <Box sx={{
                                height: "calc(100vh - 314px)",
                                width: "100%",
                                border: 2,
                                borderRadius: 1,
                                borderColor: "primary.main"
                            }}
                            >
                                <ReactFlowProvider>
                                    <Board description={description}/>
                                </ReactFlowProvider>
                            </Box>
                        </Container>
                        <Container maxWidth={false}>
                            <Copyright/>
                        </Container>
                    </Box>
                </Box>
                :
                <Box sx={{display: "flex", alignItems: "center", justifyContent: "center"}}>
                    <CircularProgress/>
                </Box>
            }
        </>
    );
}

export default Showcase;
