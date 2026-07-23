import { Box, Typography } from '@mui/material';
import React from 'react';

const AdminServiceStatistics: React.FC = () => (
    <Box sx={{mt: 1}}>
        <Typography color="text.secondary">
            Searchable task, success, failure, availability and recent usage statistics by service will appear here.
        </Typography>
    </Box>
);

export default AdminServiceStatistics;
