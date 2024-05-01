import React from 'react';
import {
    Box,
    Container,
    Toolbar,
    Grid,
    Typography,
    Card,
    CardContent,
    Divider,
    Stack,
    styled,
    Paper,
    Link as URLLink, Button, CardHeader,
} from '@mui/material';
import {
    ArrowUpward,
    PublicTwoTone,
    DescriptionTwoTone,
    GitHub,
    AllInclusiveTwoTone,
    ArrowForward
} from '@mui/icons-material';
import Copyright from '../../components/Copyright/Copyright';
import ScrollToTop from 'react-scroll-to-top';
import { useDispatch, useSelector } from 'react-redux';
import { isSmartphone } from '../../utils/functions';
import { useNavigate } from 'react-router-dom';
import { setMenuIcon } from '../../utils/reducers/menuIconSlice';

const Item = styled(Paper)(({theme}) => ({
    backgroundColor: theme.palette.mode === 'dark' ? '#1A2027' : '#fff',
    ...theme.typography.body2,
    padding: theme.spacing(1),
    textAlign: 'center',
    color: theme.palette.text.secondary
}));

const Info: React.FC = () => {
    const dispatch = useDispatch();
    const colorMode = useSelector((state: any) => state.colorMode.value);

    const navigate = useNavigate();
    const [isHovered, setHovered] = React.useState(false);

    const navigateHome = () => {
        navigate("/home");
    }

    React.useEffect(() => {
        if (window.location.pathname !== '/') {
            navigate("/");
        }
    }, [navigate]);

    React.useEffect(() => {
        dispatch(setMenuIcon(false));
    });

    return (
        <Box sx={{display: "flex"}}>
            <ScrollToTop smooth
                         component={<ArrowUpward style={{color: (colorMode === 'light' ? 'white' : 'black')}}
                                                 sx={{paddingTop: '2px'}}/>}/>
            <Box component={"main"} sx={{flexGrow: 1, py: 4}}>
                <Toolbar/>
                <Container>
                    <Typography
                        component={"h1"}
                        variant={"h2"}
                        align={"center"}
                        color={"text.primary"}
                        gutterBottom
                    >
                        Core Engine of the Swiss AI Center
                    </Typography>
                    <Typography variant={"h5"} align={"justify"} color={"text.secondary"} mb={4} paragraph>
                        The Swiss AI Center is supported by the University of Applied Science Western Switzerland
                        HES-SO. Its main mission is to accelerate the adoption of AI by SMEs, by organising activities
                        such as prototyping, education for enterprises, networking events,
                        conferences, methodologies. One important activity is the Core Engine, a rapid prototyping tool
                        allowing to define seamlessly data pipelines involving AI services.
                    </Typography>
                    <Box sx={{display: 'flex', justifyContent: 'center', flexWrap: 'wrap', gap: 1}} my={4}>
                        <Button endIcon={isHovered ? <ArrowForward/> : <></>} onClick={navigateHome}
                                variant={"contained"}
                                disableElevation
                                color={"secondary"}
                                size={"large"}
                                fullWidth={isSmartphone()}
                                onMouseEnter={() => setHovered(true)}
                                onMouseLeave={() => setHovered(false)}
                        >
                            Launch the application
                        </Button>
                    </Box>
                    <Stack
                        direction={{xs: 'column', sm: 'row'}}
                        divider={<Divider orientation="vertical" flexItem/>}
                        spacing={{xs: 1, sm: 2}}
                        justifyContent={"center"}
                    >
                        <Item variant={"outlined"}>
                            <URLLink href={"https://swiss-ai-center.ch"} target={"_blank"} color={"inherit"}
                                     sx={{textDecoration: "none"}}>
                                <Button variant={"text"} startIcon={<PublicTwoTone/>}>
                                    Website
                                </Button>
                            </URLLink>
                        </Item>
                        <Item variant={"outlined"}>
                            <URLLink href={"https://docs.swiss-ai-center.ch"} target={"_blank"} color={"inherit"}
                                     sx={{textDecoration: "none"}}>
                                <Button variant={"text"} startIcon={<DescriptionTwoTone/>}>
                                    Documentation
                                </Button>
                            </URLLink>
                        </Item>
                        <Item variant={"outlined"}>
                            <URLLink href={"https://github.com/swiss-ai-center"} target={"_blank"} color={"inherit"}
                                     sx={{textDecoration: "none"}}>
                                <Button variant={"text"} startIcon={<GitHub/>}>
                                    GitHub
                                </Button>
                            </URLLink>
                        </Item>
                        <Item variant={"outlined"}>
                            <URLLink href={"https://mlops.swiss-ai-center.ch"} target={"_blank"} color={"inherit"}
                                     sx={{textDecoration: "none"}}>
                                <Button variant={"text"} startIcon={<AllInclusiveTwoTone/>}>
                                    A guide to MLOps
                                </Button>
                            </URLLink>
                        </Item>
                    </Stack>
                </Container>
                <Container>
                    <Typography variant={"h4"} align={"center"} color={"text.secondary"} my={4} paragraph>
                        About the Core Engine
                    </Typography>
                    <Grid container spacing={2} justifyContent={"center"}>
                        <Grid item xs={12} md={6}>
                            <Card sx={{height: "100%"}} variant={"outlined"}>
                                <CardHeader title={"What is the Core Engine?"}
                                            titleTypographyProps={{variant: "h5"}}/>
                                <CardContent>
                                    <Typography variant={"h6"} align={"justify"} color={"text.secondary"} paragraph>
                                        This application is a showcase of the Swiss AI Center Core Engine.
                                        It provides a set of services and pipelines to demonstrate the capabilities
                                        of the platform. You can test the services and pipelines, chain them
                                        together
                                        and create your own workflows.
                                    </Typography>
                                </CardContent>
                            </Card>
                        </Grid>
                        <Grid item xs={12} md={6}>
                            <Card sx={{height: "100%"}} variant={"outlined"}>
                                <CardHeader title={"How to use the Core Engine?"}
                                            titleTypographyProps={{variant: "h5"}}/>
                                <CardContent>
                                    <Typography variant={"h6"} align={"justify"} color={"text.secondary"} paragraph>
                                        To use the Core Engine, just click on the "Launch the application" button
                                        and
                                        you will be redirected to the list of services and pipelines. You can filter
                                        them by category, search for a specific service or pipeline, and sort them
                                        by
                                        name. To add your own services or pipelines, just head to the <URLLink
                                        target={"_blank"}
                                        href={"https://docs.swiss-ai-center.ch"}>documentation</URLLink> and follow
                                        the
                                        instructions.
                                    </Typography>
                                </CardContent>
                            </Card>
                        </Grid>
                        <Grid item xs={12} md={6}>
                            <Card sx={{height: "100%"}} variant={"outlined"}>
                                <CardHeader title={"How much does it cost?"}
                                            titleTypographyProps={{variant: "h5"}}/>
                                <CardContent>
                                    <Typography variant={"h6"} align={"justify"} color={"text.secondary"} paragraph>
                                        The Core Engine is free to use. It is an open-source project and is
                                        maintained by the Swiss AI Center. You can use the services and pipelines
                                        to develop your own applications and workflows. If you need help or support,
                                        you can <URLLink href={"mailto:info@swiss-ai-center.ch"}>contact
                                        us</URLLink>.
                                    </Typography>
                                </CardContent>
                            </Card>
                        </Grid>
                        <Grid item xs={12} md={6}>
                            <Card sx={{height: "100%"}} variant={"outlined"}>
                                <CardHeader title={"How to contribute?"} titleTypographyProps={{variant: "h5"}}/>
                                <CardContent>
                                    <Typography variant={"h6"} align={"justify"} color={"text.secondary"} paragraph>
                                        The Core Engine is an open-source project and is maintained by the Swiss AI
                                        Center. If you want to contribute to the project, you can fork the
                                        repository
                                        on <URLLink
                                        target={"_blank"}
                                        href={"https://github.com/swiss-ai-center/core-engine"}>GitHub</URLLink> and
                                        submit a pull request. You can also open an issue if you find a
                                        bug or have a feature request.
                                    </Typography>
                                </CardContent>
                            </Card>
                        </Grid>
                    </Grid>
                </Container>
                <Container>
                    <Copyright/>
                </Container>
            </Box>
        </Box>
    );
}

export default Info;
