import React from 'react';
import {
    Box,
    Button,
    Container,
    CircularProgress,
    Toolbar,
    Link as URLLink, Grid,
} from '@mui/material';
import { Link, useNavigate, useParams } from 'react-router-dom';
import Board from '../../components/Board/Board';
import { getPipelineDescription, getServiceDescription } from '../../utils/api';
import { DescriptionTwoTone, ApiRounded, ArrowBack, ArrowUpward } from '@mui/icons-material';
import Copyright from '../../components/Copyright/Copyright';
import { InformationDrawer } from '../../components/InformationDrawer/InformationDrawer';
import { toast } from 'react-toastify';
import ScrollToTop from 'react-scroll-to-top';
import { useSelector } from 'react-redux';
import { isSmartphone } from '../../utils/functions';
import { ReactFlowProvider } from 'reactflow';


const Showcase: React.FC<{ mobileOpen: boolean }> = ({mobileOpen}) => {
    const params = useParams();
    const navigate = useNavigate();
    const colorMode = useSelector((state: any) => state.colorMode.value);
    const [isReady, setIsReady] = React.useState(false);

    const [description, setDescription] = React.useState<any>(null);

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
                    const stepsDescriptions = await Promise.all(steps.map((step: any) => getServiceDescription(step.identifier)));
                    for (let i = 0; i < steps.length; i++) {
                        steps[i].service = stepsDescriptions[i];
                    }
                    desc.steps = steps;
                }
                if ((desc as any).status === 'available') {
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

    React.useEffect(() => {
        const slug = params.slug as string;
        const type = params.type as string;
        getDescription(slug, type);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    return (
        <>
            {isReady ?
                <Box sx={{display: "flex"}}>
                    <ScrollToTop smooth
                                 component={<ArrowUpward style={{color: (colorMode === 'light' ? 'white' : 'black')}}
                                                         sx={{paddingTop: '2px'}}/>}/>
                    <InformationDrawer mobileOpen={mobileOpen} description={description}/>
                    <Box component={"main"} sx={{flexGrow: 1, pb: 4}}>
                        <Toolbar/>
                        <Container sx={{my: 2}} maxWidth={false}>
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
                                    </Grid>) : <></>
                                }
                            </Grid>
                        </Container>
                        <Container maxWidth={false}>
                            <Box sx={{
                                height: 500,
                                width: "100%",
                                border: 2,
                                borderRadius: "5px",
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
