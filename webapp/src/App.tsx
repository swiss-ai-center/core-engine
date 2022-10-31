import React from 'react';
import { Container, Box, AppBar, Toolbar, Link, Typography, ThemeProvider, Grid } from '@mui/material';
import {
    BrowserRouter as Router,
    Route,
    Routes
} from "react-router-dom";
import Showcase from './pages/Showcase/Showcase';
import Home from './pages/Home/Home';
import CssBaseline from '@mui/material/CssBaseline';
import { Home as HomeIcon } from '@mui/icons-material';
import { createTheme } from '@mui/material/styles';

function Copyright() {
    return (
        <Grid container>
            <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary" align="left">
                    {'Copyright © '}
                    <Link color="inherit" href="https://hes-so.ch/">
                        HES-SO
                    </Link>{' '}
                    {new Date().getFullYear()}
                    {'.'}
                </Typography>
            </Grid>
            <Grid item display={"flex"} justifyContent={"flex-end"} xs={6}>
                <Typography variant="body2" color="text.secondary" component={"span"}>
                    <Link color="inherit" href="https://swiss-ai-center.ch/">
                        Official Website
                    </Link>
                    {' | '}
                    <Link color="inherit" href="https://github.com/csia-pme/csia-pme/">
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
    const theme = createTheme();
    return (<ThemeProvider theme={theme}>

            {/* CssBaseline kickstart an elegant, consistent, and simple baseline to build upon. */}
            <CssBaseline/>
            {/* End CssBaseline */}

            {/* Header navbar */}
            <AppBar position="relative">
                <Toolbar>
                    <HomeIcon sx={{mr: 2}}/>
                    <Typography variant="h6" color="inherit" noWrap>
                        {title}
                    </Typography>
                </Toolbar>
            </AppBar>
            {/* End Header navbar */}

            <Container>
                {/* Main content */}
                <Router>
                    <Routes>
                        <Route path={"/showcase"} element={<Showcase/>}/>
                        <Route path={"*"} element={<Home/>}/>
                    </Routes>
                </Router>
                {/* End Main content */}
            </Container>

            {/* Footer */}
            <Box sx={{bgcolor: 'lightgray', p: 6}} component="footer">
                <Copyright/>
            </Box>
            {/* End footer */}

        </ThemeProvider>
    );
}

export default App;
