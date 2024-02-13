import React from 'react';
import {
    Box,
    Button,
    Container,
    CircularProgress,
    Toolbar,
    Link as URLLink, Grid,
} from '@mui/material';
import { useParams } from 'react-router-dom';
import Board from '../../components/Board/Board';
import { getPipelineDescription, getServiceDescription } from '../../utils/api';
import { OpenInNew, ArrowBack, ArrowUpward } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import Copyright from '../../components/Copyright/Copyright';
import { InformationDrawer } from '../../components/InformationDrawer/InformationDrawer';
import { toast } from 'react-toastify';
import ScrollToTop from 'react-scroll-to-top';
import { useSelector } from 'react-redux';
import { isSmartphone } from '../../utils/functions';


const Showcase: React.FC<{ mobileOpen: boolean }> = ({mobileOpen}) => {
    const params = useParams();
    const navigate = useNavigate();
    const colorMode = useSelector((state: any) => state.colorMode.value);
    const [isReady, setIsReady] = React.useState(false);

    const [description, setDescription] = React.useState<any>(null);

    const navigateBack = () => {
        navigate(-1);
    }

    const getDescription = async (slug: string, type: string) => {
        setIsReady(false);
        if (!slug || !type) {
            toast("No slug or type provided", {type: "warning"});
            navigateBack();
        }
        let desc = {};
        try {
            if (type === 'service') {
                desc = await getServiceDescription(slug);
            } else {
                desc = await getPipelineDescription(slug);
            }
            if (desc) {
                if ((desc as any).status === 'available') {
                    setDescription(desc);
                } else {
                    toast("This service or pipeline is actually not available", {type: "warning"});
                    navigateBack();
                }
            } else {
                toast("No description found with this slug", {type: "warning"});
                navigateBack();
            }
            setIsReady(true);
        } catch (e: any) {
            toast("No description found with this slug", {type: "warning"});
            navigateBack();
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
                                    <Button variant={"outlined"} color={"secondary"} startIcon={<ArrowBack/>}
                                            onClick={navigateBack}>
                                        Back
                                    </Button>
                                </Grid>
                                {params.type as string === "service" ? (
                                    <Grid item>
                                        <URLLink href={description.url}>
                                            <Button color={"secondary"} variant={"outlined"}
                                                    startIcon={<OpenInNew/>}>
                                                OpenAPI Specification
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
                                <Board description={description}/>
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
