import React from 'react';
import {
    Container,
    Box,
    AppBar,
    Toolbar,
    Link,
    Typography,
    ThemeProvider,
    Grid,
    IconButton, Tooltip, PaletteMode
} from '@mui/material';
import {
    BrowserRouter as Router,
    Route,
    Routes
} from "react-router-dom";
import Showcase from './pages/Showcase';
import Home from './pages/Home';
import CssBaseline from '@mui/material/CssBaseline';
import { QueryStats, LightMode, DarkMode } from '@mui/icons-material';
import { createTheme } from '@mui/material/styles';
import { EngineStats } from './components/EngineStats/EngineStats';
import { grey } from '@mui/material/colors';
import { useDispatch, useSelector } from 'react-redux';
import { toggleColorMode } from './utils/reducers/colorModeSlice';

function Copyright() {
    return (
        <Grid container justifyContent={"space-between"}>
            <Grid item alignItems={"center"} justifyContent={"left"} display={"flex"}>
                <Typography variant={"body2"} color={"text.secondary"} align={"left"}>
                    {'Copyright © '}
                    <Link color={"primary"} href={"https://hes-so.ch/"} target={"_blank"}
                          sx={{textDecoration: "none"}}>HES-SO</Link>
                    {' 2022-' + new Date().getFullYear() + '.'}
                </Typography>
            </Grid>
            <Grid item alignItems={"center"} justifyContent={"center"} display={"flex"}>
                <Link color={"primary"} href={"https://swiss-ai-center.ch/"} target={"_blank"}
                      sx={{textDecoration: "none"}}>
                    <img src={"/logo_full.png"} alt={"Swiss AI Center"} height={"40px"} style={{marginRight: "10px"}}/>
                </Link>
            </Grid>
            <Grid item alignItems={"center"} justifyContent={"right"} display={"flex"}>
                <Typography variant={"body2"} color={"text.secondary"} component={"span"}>
                    <Link color={"primary"} href={"https://swiss-ai-center.ch/"} target={"_blank"}
                          sx={{textDecoration: "none"}}>
                        Official Website
                    </Link>
                    {' | '}
                    <Link color={"primary"} href={"https://github.com/csia-pme/csia-pme/"} target={"_blank"}
                          sx={{textDecoration: "none"}}>
                        GitHub
                    </Link>
                </Typography>
            </Grid>
        </Grid>
    )
        ;
}

function App() {
    const title = "CSIA-PME";
    const dispatch = useDispatch();
    const colorMode = useSelector((state: any) => state.colorMode.value);
    const lightgrey = grey[300];
    const darkgrey = grey[900];

    const getDesignTokens = (mode: PaletteMode) => ({
        palette: {
            mode,
            ...(mode === 'light'
                ? {
                    // palette values for light mode
                    primary: {
                        main: '#e6081d',
                    },
                    secondary: {
                        main: lightgrey,
                    }
                }
                : {
                    // palette values for dark mode
                    primary: {
                        main: '#e6081d'
                    },
                    secondary: {
                        main: darkgrey,
                    }
                }),
        },
    });


    const theme = React.useMemo(
        () =>
            createTheme(getDesignTokens(colorMode)),
        [colorMode],
    );
    const [open, setOpen] = React.useState(false);

    const handleOpenStats = () => {
        setOpen(true);
    }

    const handleCloseStats = () => {
        setOpen(false);
    }

    return (
        <ThemeProvider theme={theme}>

            {/* CssBaseline kickstart an elegant, consistent, and simple baseline to build upon. */}
            <CssBaseline/>
            {/* End CssBaseline */}

            {/* Header navbar */}
            <AppBar position="relative" color={"secondary"}>
                <Toolbar>
                    <Grid container justifyContent={"space-between"} alignItems={"center"}>
                        <Grid item>
                            <Link color="inherit" href="/" underline="none">
                                <img src={"/logo512.png"} alt={"Swiss AI Center"} height={"40px"}
                                     style={{marginRight: "10px"}}/>
                            </Link>
                        </Grid>
                        <Grid item>
                            <Typography variant="h6" color="inherit" noWrap>
                                {title}
                            </Typography>
                        </Grid>
                        <Grid item>
                            <Tooltip title={"Toggle dark / light mode"}>
                                <IconButton sx={{marginLeft: "auto"}} color={"inherit"} size={"large"}
                                            onClick={() => dispatch(toggleColorMode())}>
                                    {colorMode === 'light' ? <LightMode/> : <DarkMode/>}
                                </IconButton>
                            </Tooltip>
                            <Tooltip title={"Engine stats"}>
                                <IconButton sx={{marginLeft: "auto"}} color={"inherit"} size={"large"}
                                            onClick={() => handleOpenStats()}>
                                    <QueryStats/>
                                </IconButton>
                            </Tooltip>
                        </Grid>
                    </Grid>
                </Toolbar>
            </AppBar>
            {/* End Header navbar */}

            <Container>
                {/* Main content */}
                <EngineStats trigger={open} onClose={handleCloseStats}/>
                <Router>
                    <Routes>
                        <Route path={"/showcase"} element={<Showcase/>}/>
                        <Route path={"*"} element={<Home/>}/>
                    </Routes>
                </Router>
                {/* End Main content */}
            </Container>

            {/* Footer */}
            <Box sx={{bgcolor: 'secondary.main', p: 4, mt: 'auto'}} component="footer">
                <Copyright/>
            </Box>
            {/* End footer */}

        </ThemeProvider>
    );
}

export default App;
