import {
    Box,
    Drawer,
    Toolbar,
} from '@mui/material';
import React from 'react';
import PipelineConfiguration from '../PipelineConfiguration/PipelineConfiguration';

const isSmartphone = (): boolean => {
    return window.innerWidth < 600;
}
const drawerWidth = isSmartphone() ? '100%' : 500;

export const DescriptionDrawer: React.FC<{
    mobileOpen: boolean,
    description: string,
}> = ({
          mobileOpen,
          description
      }) => {

    const drawer = (
        <>
            <Toolbar/>
            <Box sx={{overflow: 'auto'}}>
                <Box sx={{ml: 3}}>
                    <h3>Description</h3>
                </Box>
                <Box sx={{mx: 3}}>
                    <PipelineConfiguration description={description} show={true}/>
                </Box>
            </Box>
        </>
    );


    return (
        <Box
            component="nav"
            sx={{width: {md: drawerWidth}, flexShrink: {md: 0}}}
            aria-label="mailbox folders"
        >
            {/* The implementation can be swapped with js to avoid SEO duplication of links. */}
            <Drawer
                variant="temporary"
                open={mobileOpen}
                ModalProps={{
                    keepMounted: true, // Better open performance on mobile.
                }}
                sx={{
                    display: {xs: 'block', md: 'none'},
                    '& .MuiDrawer-paper': {boxSizing: 'border-box', width: drawerWidth},
                }}
            >
                {drawer}
            </Drawer>
            <Drawer
                variant="permanent"
                sx={{
                    display: {xs: 'none', md: 'block'},
                    '& .MuiDrawer-paper': {boxSizing: 'border-box', width: drawerWidth},
                }}
                open
            >
                {drawer}
            </Drawer>
        </Box>
    );
}
