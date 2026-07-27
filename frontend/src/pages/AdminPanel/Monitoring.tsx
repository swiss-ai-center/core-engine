import { Box, Typography } from '@mui/material';
import React from 'react';

const AdminMonitoring: React.FC = () => (
    <Box sx={{mt: 1}}>
        <Typography color="text.secondary">
            Running tasks and service resource consumption will be monitored here.
        </Typography>
    </Box>
);

export default AdminMonitoring;
