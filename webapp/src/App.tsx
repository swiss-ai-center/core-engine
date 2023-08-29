import React from 'react';
import {
    AppBar, Toolbar, Link, Grid, IconButton, Tooltip, PaletteMode
} from '@mui/material';
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Showcase from './pages/Showcase';
import Home from './pages/Home';
import CssBaseline from '@mui/material/CssBaseline';
import {
    Menu as MenuIcon,
    MenuOpen as CloseIcon,
    LightModeTwoTone, DarkModeTwoTone, QueryStatsTwoTone
} from '@mui/icons-material';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import { EngineStats } from './components/EngineStats/EngineStats';
import { grey } from '@mui/material/colors';
import { useDispatch, useSelector } from 'react-redux';
import { toggleColorMode } from './utils/reducers/colorModeSlice';
import "typeface-inter";


function App() {
    const dispatch = useDispatch();
    const colorMode = useSelector((state: any) => state.colorMode.value);
    const lightgrey = grey[300];
    const darkgrey = grey[900];
    const [mobileOpen, setMobileOpen] = React.useState(false);

    const handleDrawerToggle = () => {
        setMobileOpen(!mobileOpen);
    };

    const getDesignTokens = (mode: PaletteMode) => ({
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
        }
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
            <AppBar position="fixed"
                    elevation={1}
                    sx={{zIndex: (theme) => theme.zIndex.drawer + 1}}
            >
                <Toolbar>
                    <IconButton
                        color="inherit"
                        aria-label="open drawer"
                        edge="start"
                        onClick={handleDrawerToggle}
                        sx={{mr: 2, display: {md: 'none'}}}
                    >
                        {mobileOpen ? <CloseIcon/> : <MenuIcon/>}
                    </IconButton>
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
                            <Tooltip title={"Engine stats"}>
                                <IconButton sx={{marginLeft: "auto"}} color={"inherit"} size={"large"}
                                            onClick={() => handleOpenStats()}>
                                    <QueryStatsTwoTone/>
                                </IconButton>
                            </Tooltip>
                        </Grid>
                    </Grid>
                </Toolbar>
            </AppBar>
            {/* End Header navbar */}

            {/* Main content */}
            <EngineStats trigger={open} onClose={handleCloseStats}/>
            <Router>
                <Routes>
                    <Route path={"/showcase/:type/:id"}
                           element={<Showcase mobileOpen={mobileOpen}/>}/>
                    <Route path={"*"} element={<Home mobileOpen={mobileOpen}
                                                     handleOpen={handleDrawerToggle}
                    />}/>
                </Routes>
            </Router>
            {/* End Main content */}

        </ThemeProvider>
    );
}

export default App;
