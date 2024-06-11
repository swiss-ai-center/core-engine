import {
    DarkModeTwoTone,
    LightModeTwoTone,
    MenuOpenRounded as CloseIcon,
    MenuRounded as MenuIcon,
    QueryStatsTwoTone
} from '@mui/icons-material';
import { AppBar, Grid, IconButton, Link, PaletteMode, Toolbar, Tooltip } from '@mui/material';
import { grey } from '@mui/material/colors';
import CssBaseline from '@mui/material/CssBaseline';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import Home from 'pages/Home';
import Info from 'pages/Info';
import PipelineEditor from "pages/PipelineEditor";
import Showcase from 'pages/Showcase';
import React, { useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import { EngineStats } from './components/EngineStats/EngineStats';
import { toggleColorMode } from './utils/reducers/colorModeSlice';
import "typeface-inter";


function App() {
    const dispatch = useDispatch();
    const menuIcon = useSelector((state: any) => state.menuIcon.value);
    const colorMode = useSelector((state: any) => state.colorMode.value);
    const lightgrey = grey[300];
    const darkgrey = grey[900];
    const [mobileOpen, setMobileOpen] = React.useState(false);

    const handleDrawerToggle = () => {
        setMobileOpen(!mobileOpen);
    };

    const getDesignTokens = useCallback((mode: PaletteMode) => ({
        palette: {
            mode,
            ...(mode === 'light'
                ? {
                    // palette values for light mode
                    primary: {
                        main: '#d41367',
                    },
                    primary_light: {
                        main: '#e989b3',
                    },
                    secondary: {
                        main: '#89264f'
                    },
                    background_color: {
                        main: lightgrey,
                    }
                }
                : {
                    // palette values for dark mode
                    primary: {
                        main: '#d41367'
                    },
                    primary_light: {
                        main: '#89264f',
                    },
                    secondary: {
                        main: '#e989b3'
                    },
                    background_color: {
                        main: darkgrey,
                    }
                })
        },
        typography: {
            fontFamily: ["Neue Haas Grotesk Display Pro, sans-serif", "Helvetica now, sans-serif"].join(','),
        },
        components: {
            MuiFab: {
                styleOverrides: {
                    sizeSmall: {
                        width: 24,
                        height: 24,
                        minHeight: 'unset',
                        '& .MuiSvgIcon-root': {
                            fontSize: 16,
                        },
                    },
                },
            },
        },
    }), [darkgrey, lightgrey]);

    const theme = React.useMemo(
        () =>
            createTheme(getDesignTokens(colorMode)),
        [colorMode, getDesignTokens],
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
            <AppBar position={"fixed"} elevation={0} sx={{
                zIndex: (theme) => theme.zIndex.drawer + 1,
                backgroundColor: colorMode === "light" ? "primary.main" : "background_color.main"
            }}>
                <Toolbar>
                    {menuIcon ?
                        <IconButton
                            color={"inherit"}
                            aria-label={"open drawer"}
                            edge={"start"}
                            onClick={handleDrawerToggle}
                            sx={{mr: 2, display: {md: 'none'}}}
                        >
                            {mobileOpen ? <CloseIcon/> : <MenuIcon/>}
                        </IconButton> : <></>}
                    <Grid container justifyContent={"space-between"} alignItems={"center"} sx={{height: "100%"}}>
                        <Grid item>
                            <Link color={"inherit"} href={"/"} underline={"none"}>
                                <img src={colorMode === "light" ? "/logo_full_white_sec.png" : "/logo_full_white.png"}
                                     alt={"Swiss AI Center"} height={"25px"}
                                     style={{marginRight: "10px", marginTop: "2px"}}/>
                            </Link>
                        </Grid>
                        <Grid item>
                            <Tooltip title={"Toggle dark / light mode"}>
                                <IconButton sx={{marginLeft: "auto"}} color={"inherit"} size={"large"}
                                            onClick={() => dispatch(toggleColorMode())}>
                                    {colorMode === 'light' ? <LightModeTwoTone/> : <DarkModeTwoTone/>}
                                </IconButton>
                            </Tooltip>
                            {/* if page is Info, hide stats button */}
                            {window.location.pathname === "/" ? <></> :
                                <Tooltip title={"Engine stats"}>
                                    <IconButton sx={{marginLeft: "auto"}} color={"inherit"} size={"large"}
                                                onClick={() => handleOpenStats()}>
                                        <QueryStatsTwoTone/>
                                    </IconButton>
                                </Tooltip>}
                        </Grid>
                    </Grid>
                </Toolbar>
            </AppBar>
            {/* End Header navbar */}

            {/* Main content */}
            <EngineStats trigger={open} onClose={handleCloseStats}/>
            <Router>
                <Routes>
                    <Route path={"/showcase/:type/:slug"} element={<Showcase mobileOpen={mobileOpen}/>}/>
                    <Route path={"/showcase"} element={<Info/>}/>
                    <Route path={"/home"} element={<Home mobileOpen={mobileOpen} handleOpen={handleDrawerToggle}/>}/>
                    <Route path={"*"} element={<Info/>}/>
                    <Route path={"/pipeline-editor"}
                           element={<PipelineEditor mobileOpen={mobileOpen} handleOpen={handleDrawerToggle}/>}/>
                </Routes>
            </Router>
            {/* End Main content */}

        </ThemeProvider>
    );
}

export default App;
