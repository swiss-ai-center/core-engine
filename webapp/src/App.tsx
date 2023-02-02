import React from 'react';
import {
    Container, Box, AppBar, Toolbar, Link, Typography, ThemeProvider, Grid, IconButton, Tooltip, PaletteMode
} from '@mui/material';
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Showcase from './pages/Showcase';
import Home from './pages/Home';
import CssBaseline from '@mui/material/CssBaseline';
import { QueryStats, LightMode, DarkMode } from '@mui/icons-material';
import { createTheme } from '@mui/material/styles';
import { EngineStats } from './components/EngineStats/EngineStats';
import { grey } from '@mui/material/colors';
import { useDispatch, useSelector } from 'react-redux';
import { toggleColorMode } from './utils/reducers/colorModeSlice';

declare module '@mui/material/styles' {
    interface Palette {
        background_color: Palette['primary'];
    }

    interface PaletteOptions {
        background_color: PaletteOptions['primary'];
    }
}

// declare module to extend the theme colors
declare module '@mui/material/AppBar' {
    interface AppBarPropsColorOverrides {
        background_color: true;
    }
}

function Copyright(colorMode: any) {
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
                    <img src={colorMode.colorMode === "light" ? "/logo_full.png" : "/logo_full_white.png"}
                         alt={"Swiss AI Center"} height={"50px"}/>
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
                        main: '#da0066',
                    },
                    secondary: {
                        main: '#83d6de'
                    },
                    background_color: {
                        main: lightgrey,
                    }
                }
                : {
                    // palette values for dark mode
                    primary: {
                        main: '#da0066'
                    },
                    secondary: {
                        main: '#83d6de'
                    },
                    background_color: {
                        main: darkgrey,
                    }
                }),
        },
    });


    const theme = React.useMemo(
        () =>
            createTheme(getDesignTokens(colorMode)),
        // eslint-disable-next-line react-hooks/exhaustive-deps
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
            <AppBar position="relative" color={"background_color"}>
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
            <Box sx={{bgcolor: 'background_color.main', p: 4, mt: 'auto'}} component="footer">
                <Copyright colorMode={colorMode}/>
            </Box>
            {/* End footer */}

        </ThemeProvider>
    );
}

export default App;
