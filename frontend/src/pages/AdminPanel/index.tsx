import {
    AccountTreeOutlined,
    AnalyticsOutlined,
    ArticleOutlined,
    MiscellaneousServicesOutlined,
    MonitorHeartOutlined,
    PeopleOutline,
    QueryStatsOutlined,
} from '@mui/icons-material';
import {
    Alert,
    Box,
    CircularProgress,
    List,
    ListItemButton,
    ListItemIcon,
    ListItemText,
    Toolbar,
    Tooltip,
    Typography,
} from '@mui/material';
import React, { useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { NavLink, useParams } from 'react-router-dom';
import { useAuthentication } from 'utils/hooks/authentication';
import { setMenuIcon } from 'utils/reducers/menuIconSlice';
import AdminEngineStatistics from './EngineStatistics';
import AdminLogs from './Logs';
import AdminMonitoring from './Monitoring';
import AdminPipelines from './Pipelines';
import AdminServices from './Services';
import AdminServiceStatistics from './ServiceStatistics';
import AdminUsers from './Users';

const sections = {
    users: {label: 'Users', icon: <PeopleOutline/>},
    pipelines: {label: 'Pipelines', icon: <AccountTreeOutlined/>},
    services: {label: 'Services', icon: <MiscellaneousServicesOutlined/>},
    logs: {label: 'Logs', icon: <ArticleOutlined/>},
    monitoring: {label: 'Monitoring', icon: <MonitorHeartOutlined/>},
    'engine-statistics': {label: 'Engine statistics', icon: <QueryStatsOutlined/>},
    'service-statistics': {label: 'Service statistics', icon: <AnalyticsOutlined/>},
};

type AdminSection = keyof typeof sections;

const categories: { label: string, sections: AdminSection[] }[] = [
    {label: 'User management', sections: ['users']},
    {label: 'Engine resources', sections: ['pipelines', 'services']},
    {label: 'Monitoring', sections: ['logs', 'monitoring']},
    {label: 'Statistics', sections: ['engine-statistics', 'service-statistics']},
];

const AdminPanel: React.FC = () => {
    const dispatch = useDispatch();
    const {section = 'users'} = useParams<{ section: AdminSection }>();
    const {user, isCheckingSession} = useAuthentication();
    const activeSection = section in sections ? section as AdminSection : 'users';

    useEffect(() => {
        dispatch(setMenuIcon(false));
    }, [dispatch]);

    if (isCheckingSession) {
        return (
            <Box component="main" sx={{flexGrow: 1, p: 4}}>
                <Toolbar/>
                <CircularProgress size={28}/>
            </Box>
        );
    }

    if (!user || user.role !== 'admin') {
        return (
            <Box component="main" sx={{flexGrow: 1, p: 4}}>
                <Toolbar/>
                <Alert severity="warning">Administrator access is required to view this page.</Alert>
            </Box>
        );
    }

    return (
        <Box sx={{display: 'flex', flexGrow: 1, minHeight: '100vh'}}>
            <Box
                component="aside"
                sx={{
                    width: {xs: 76, sm: 280},
                    flexShrink: 0,
                    bgcolor: 'background.paper',
                    borderRight: '1px solid',
                    borderColor: 'divider',
                }}
            >
                <Toolbar/>
                <Box sx={{px: {xs: 1, sm: 3}, pt: {xs: 2, sm: 4}}}>
                    <Box sx={{display: {xs: 'none', sm: 'block'}, px: 1.75, mb: 2.5}}>
                        <Typography variant="subtitle2" fontWeight={700}>
                            Admin panel
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                            Workspace management
                        </Typography>
                    </Box>
                    <Box sx={{display: 'grid', gap: {xs: 1.5, sm: 3}}}>
                        {categories.map((category) => (
                            <Box key={category.label}>
                                <Typography
                                    variant="overline"
                                    color="text.secondary"
                                    fontWeight={700}
                                    sx={{display: {xs: 'none', sm: 'block'}, px: 2, mb: 0.75}}
                                >
                                    {category.label}
                                </Typography>
                                <List disablePadding sx={{display: 'grid', gap: 1}}>
                                    {category.sections.map((key) => {
                                        const item = sections[key];
                                        return (
                                            <Tooltip key={key} title={item.label} placement="right">
                                                <ListItemButton
                                                    component={NavLink}
                                                    to={`/admin/${key}`}
                                                    sx={{
                                                        position: 'relative',
                                                        minHeight: 52,
                                                        borderRadius: 1.5,
                                                        px: {xs: 1.5, sm: 2},
                                                        py: 1.25,
                                                        justifyContent: {xs: 'center', sm: 'flex-start'},
                                                        transition: 'background-color 150ms ease, color 150ms ease',
                                                        '&:hover': {
                                                            bgcolor: 'action.hover',
                                                        },
                                                        '&.active': {
                                                            color: 'primary.main',
                                                            bgcolor: 'action.selected',
                                                        },
                                                        '&.active::before': {
                                                            content: '""',
                                                            position: 'absolute',
                                                            left: 0,
                                                            top: 11,
                                                            bottom: 11,
                                                            width: 3,
                                                            borderRadius: '0 3px 3px 0',
                                                            bgcolor: 'primary.main',
                                                        },
                                                    }}
                                                >
                                                    <ListItemIcon sx={{minWidth: {xs: 0, sm: 44}, color: 'inherit'}}>
                                                        {item.icon}
                                                    </ListItemIcon>
                                                    <ListItemText
                                                        primary={item.label}
                                                        primaryTypographyProps={{fontWeight: 500}}
                                                        sx={{display: {xs: 'none', sm: 'block'}}}
                                                    />
                                                </ListItemButton>
                                            </Tooltip>
                                        );
                                    })}
                                </List>
                            </Box>
                        ))}
                    </Box>
                </Box>
            </Box>

            <Box component="main" sx={{flexGrow: 1, minWidth: 0}}>
                <Toolbar/>
                <Box sx={{p: {xs: 3, md: 5}}}>
                    <Typography component="h1" variant="h4" fontWeight={600}>
                        {sections[activeSection].label}
                    </Typography>
                    {activeSection === 'users' && <AdminUsers/>}
                    {activeSection === 'pipelines' && <AdminPipelines/>}
                    {activeSection === 'services' && <AdminServices/>}
                    {activeSection === 'logs' && <AdminLogs/>}
                    {activeSection === 'monitoring' && <AdminMonitoring/>}
                    {activeSection === 'engine-statistics' && <AdminEngineStatistics/>}
                    {activeSection === 'service-statistics' && <AdminServiceStatistics/>}
                </Box>
            </Box>
        </Box>
    );
};

export default AdminPanel;
