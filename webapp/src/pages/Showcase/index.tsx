import React from 'react';
import { Box, Button, Container, Typography, CircularProgress, Toolbar, Link as URLLink } from '@mui/material';
import { useParams } from 'react-router-dom';
import Board from '../../components/Board/Board';
import { getPipelineDescription, getServiceDescription } from '../../utils/api';
import { FullScreen, useFullScreenHandle } from 'react-full-screen';
import { OpenInNew, ArrowBack, Fullscreen } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import Copyright from '../../components/Copyright/Copyright';
import { DescriptionDrawer } from '../../components/DescriptionDrawer/DescriptionDrawer';
import { toast } from 'react-toastify';

const isSmartphone = (): boolean => {
    return window.innerWidth < 600;
}

const Showcase: React.FC<{ mobileOpen: boolean}> = ({mobileOpen}) => {
    const params = useParams();
    const navigate = useNavigate();
    const [isReady, setIsReady] = React.useState(false);

    const [description, setDescription] = React.useState<any>(null);

    const handle = useFullScreenHandle();

    const navigateBack = () => {
        navigate(-1);
    }

    const getDescription = async (id: string, type: string) => {
        setIsReady(false);
        if (!id || !type) {
            toast("No id or type provided", {type: "warning"});
            navigateBack();
        }
        let desc = {};
        try {
            if (type === 'service') {
                desc = await getServiceDescription(id);
            } else {
                desc = await getPipelineDescription(id);
            }
            if (desc) {
                if ((desc as any).status === 'available') {
                    setDescription(desc);
                } else {
                    toast("This service or pipeline is actually not available", {type: "warning"});
                    navigateBack();
                }
            } else {
                toast("No description found with this id", {type: "warning"});
                navigateBack();
            }
            setIsReady(true);
        } catch (e: any) {
            toast("No description found with this id", {type: "warning"});
            navigateBack();
        }
    }

    React.useEffect(() => {
        const id = params.id as string;
        const type = params.type as string;
        getDescription(id, type);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    return (
        <Box sx={{display: "flex"}}>
            {isReady ?
                <>
                    <DescriptionDrawer mobileOpen={mobileOpen} description={description}/>
                    <Box component={"main"} sx={{flexGrow: 1, p: 2, pt: 4}}>
                        <Toolbar/>
                        <Container maxWidth={"lg"}>
                            <Button variant={"outlined"} color={"secondary"} startIcon={<ArrowBack/>}
                                    onClick={navigateBack}>
                                Back
                            </Button>
                        </Container>
                        <Box sx={{pt: 2, pb: 2}}>
                            <Container maxWidth={"lg"}>
                                <Typography
                                    component={"h1"}
                                    variant={"h2"}
                                    align={"center"}
                                    color={"text.primary"}
                                    gutterBottom
                                >
                                    {description ? description.name : ''}
                                </Typography>
                                <Typography variant={"h5"} align={"center"}
                                            color={"text.secondary"} whiteSpace={"pre-line"}
                                            paragraph
                                >
                                    {description ? description.description : ''}
                                </Typography>
                            </Container>
                        </Box>
                        <Container sx={{py: 2}} maxWidth={"lg"}>
                            <Button sx={{mb: 2, visibility: isSmartphone() ? "hidden" : "inherit"}}
                                    color={"secondary"} variant={"outlined"}
                                    onClick={handle.enter} startIcon={<Fullscreen/>}>
                                Go Fullscreen
                            </Button>
                            <FullScreen handle={handle}>
                                <Box sx={handle.active ? {height: "100%", width: "100%"} :
                                    {
                                        height: 500,
                                        width: "100%",
                                        border: 2,
                                        borderRadius: "5px",
                                        borderColor: "primary.main"
                                    }}>
                                    <Board description={description} fullscreen={handle.active}/>
                                </Box>
                            </FullScreen>
                        </Container>
                        {params.type as string === "service" ? (
                        <Container sx={{pb: 2}} maxWidth={"lg"}>
                            <URLLink href={description.url}>
                                <Button sx={{mb: 2}} color={"secondary"} variant={"outlined"}
                                        startIcon={<OpenInNew/>}>
                                    OpenAPI Specification
                                </Button>
                            </URLLink>
                        </Container>) : <></>}
                        <Container maxWidth={"lg"}>
                            <Copyright/>
                        </Container>
                    </Box>
                </>
                :
                <Box sx={{display: "flex", alignItems: "center", justifyContent: "center"}}>
                    <CircularProgress/>
                </Box>
            }
        </Box>
    );
}

export default Showcase;
