import { RefreshOutlined } from '@mui/icons-material';
import {
    Alert,
    alpha,
    Box,
    Button,
    CircularProgress,
    Paper,
    Stack,
    Typography,
    useTheme,
} from '@mui/material';
import { ServiceAccessLevel } from 'enums/serviceAccessLevelEnum';
import { ServiceStatus } from 'enums/serviceStatusEnum';
import { AuthenticatedUser } from 'models/AuthenticatedUser';
import { Pipeline } from 'models/Pipeline';
import { Service } from 'models/Service';
import { Stats } from 'models/Stats';
import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { getAllAdminServices, getAllPipelines, getStats } from 'utils/api';
import {
    getStoredAuthenticationToken,
    getUsers,
} from 'utils/authentication';
import StatisticsDonut, {
    CountItem,
    formatStatisticLabel,
} from './StatisticsDonut';

type EngineSnapshot = {
    stats: Stats;
    services: Service[];
    pipelines: Pipeline[];
    users: AuthenticatedUser[];
};

type MetricProps = {
    label: string;
    value: number;
    detail: string;
};

const Metric = ({label, value, detail}: MetricProps) => (
    <Box sx={{minWidth: 0, px: {xs: 2, md: 3}, py: {xs: 2, md: 2.5}}}>
        <Typography variant="overline" color="text.secondary" fontWeight={700}>
            {label}
        </Typography>
        <Typography variant="h4" fontWeight={650} sx={{mt: 0.25}}>
            {value.toLocaleString()}
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{mt: 0.25}}>
            {detail}
        </Typography>
    </Box>
);

const Distribution = ({items, ariaLabel}: { items: CountItem[], ariaLabel: string }) => {
    const total = items.reduce((sum, item) => sum + item.count, 0);

    return (
        <Box>
            <Box
                role="img"
                aria-label={ariaLabel}
                sx={{
                    display: 'flex',
                    height: 12,
                    overflow: 'hidden',
                    borderRadius: 999,
                    bgcolor: 'action.hover',
                }}
            >
                {total > 0 && items.map((item) => (
                    <Box
                        key={item.label}
                        title={`${item.label}: ${item.count.toLocaleString()}`}
                        sx={{
                            width: `${(item.count / total) * 100}%`,
                            minWidth: item.count > 0 ? 3 : 0,
                            bgcolor: item.color,
                            transition: 'width 250ms ease',
                        }}
                    />
                ))}
            </Box>
            <Box
                sx={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(2, minmax(0, 1fr))',
                    columnGap: 2,
                    rowGap: 1.25,
                    mt: 2,
                }}
            >
                {items.map((item) => (
                    <Stack
                        key={item.label}
                        direction="row"
                        alignItems="center"
                        justifyContent="space-between"
                        spacing={1}
                    >
                        <Stack direction="row" alignItems="center" spacing={1} minWidth={0}>
                            <Box
                                aria-hidden
                                sx={{
                                    width: 8,
                                    height: 8,
                                    flexShrink: 0,
                                    borderRadius: '50%',
                                    bgcolor: item.color,
                                }}
                            />
                            <Typography variant="body2" color="text.secondary" noWrap>
                                {item.label}
                            </Typography>
                        </Stack>
                        <Typography variant="body2" fontWeight={650}>
                            {item.count.toLocaleString()}
                        </Typography>
                    </Stack>
                ))}
            </Box>
        </Box>
    );
};

const HorizontalBars = ({
    items,
    ariaLabel,
}: {
    items: CountItem[],
    ariaLabel: string,
}) => {
    if (items.length === 0) {
        return <Typography color="text.secondary">No task activity recorded yet.</Typography>;
    }

    const maximum = Math.max(...items.map((item) => item.count), 1);

    return (
        <Stack role="img" aria-label={ariaLabel} spacing={1.5}>
            {items.map((item) => (
                <Box
                    key={item.label}
                    sx={{
                        display: 'grid',
                        gridTemplateColumns: {
                            xs: '100px minmax(0, 1fr) 36px',
                            sm: '180px minmax(0, 1fr) 44px',
                        },
                        gap: 1.5,
                        alignItems: 'center',
                    }}
                >
                    <Typography variant="body2" color="text.secondary" noWrap title={item.label}>
                        {item.label}
                    </Typography>
                    <Box
                        sx={{
                            height: 8,
                            overflow: 'hidden',
                            borderRadius: 999,
                            bgcolor: 'action.hover',
                        }}
                    >
                        <Box
                            sx={{
                                width: `${(item.count / maximum) * 100}%`,
                                minWidth: item.count > 0 ? 4 : 0,
                                height: '100%',
                                borderRadius: 'inherit',
                                bgcolor: item.color,
                                transition: 'width 250ms ease',
                            }}
                        />
                    </Box>
                    <Typography variant="body2" fontWeight={650} textAlign="right">
                        {item.count.toLocaleString()}
                    </Typography>
                </Box>
            ))}
        </Stack>
    );
};

const AdminEngineStatistics: React.FC = () => {
    const theme = useTheme();
    const [snapshot, setSnapshot] = useState<EngineSnapshot | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState('');
    const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
    const requestSequence = useRef(0);

    const loadSnapshot = useCallback(async () => {
        const requestId = ++requestSequence.current;
        const token = getStoredAuthenticationToken();
        if (!token) {
            setError('Your session is no longer valid.');
            setIsLoading(false);
            return;
        }

        setError('');
        setIsLoading(true);

        try {
            const [statsResult, services, pipelines, users] = await Promise.all([
                getStats(),
                getAllAdminServices(token),
                getAllPipelines(token),
                getUsers(token),
            ]);

            if (!statsResult || typeof statsResult.total !== 'number') {
                throw new Error(statsResult?.error ?? 'Unable to load task statistics.');
            }

            if (requestId !== requestSequence.current) return;

            setSnapshot({
                stats: statsResult as Stats,
                services,
                pipelines,
                users,
            });
            setLastUpdated(new Date());
        } catch (loadError) {
            if (requestId !== requestSequence.current) return;
            setError(loadError instanceof Error ? loadError.message : 'Unable to load engine statistics.');
        } finally {
            if (requestId === requestSequence.current) setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        void loadSnapshot();
    }, [loadSnapshot]);

    const view = useMemo(() => {
        if (!snapshot) return null;

        const availableServices = snapshot.services.filter(
            (service) => service.status === ServiceStatus.AVAILABLE,
        ).length;
        const aiServices = snapshot.services.filter((service) => service.has_ai).length;

        const statusColors: Record<string, string> = {
            finished: theme.palette.success.main,
            pending: theme.palette.warning.main,
            scheduled: theme.palette.info.main,
            fetching: theme.palette.secondary.main,
            processing: theme.palette.primary.main,
            saving: theme.palette.info.dark,
            skipped: theme.palette.grey[500],
            unavailable: theme.palette.warning.dark,
            error: theme.palette.error.main,
        };

        const taskStatuses = [...snapshot.stats.summary]
            .sort((left, right) => right.count - left.count)
            .map((status) => ({
                label: formatStatisticLabel(status.status),
                count: status.count,
                color: statusColors[status.status] ?? theme.palette.grey[500],
            }));

        const serviceStatusColors: Record<ServiceStatus, string> = {
            [ServiceStatus.AVAILABLE]: theme.palette.success.main,
            [ServiceStatus.SLEEPING]: theme.palette.warning.main,
            [ServiceStatus.UNAVAILABLE]: theme.palette.error.main,
            [ServiceStatus.DISABLED]: theme.palette.grey[500],
        };
        const serviceStatuses = Object.values(ServiceStatus).map((status) => ({
            label: formatStatisticLabel(status),
            count: snapshot.services.filter((service) => service.status === status).length,
            color: serviceStatusColors[status],
        }));

        const accessColors: Record<ServiceAccessLevel, string> = {
            [ServiceAccessLevel.PUBLIC]: theme.palette.success.main,
            [ServiceAccessLevel.USER]: theme.palette.info.main,
            [ServiceAccessLevel.ADMIN]: theme.palette.primary.main,
            [ServiceAccessLevel.DISABLED]: theme.palette.grey[500],
        };
        const accessLevels = Object.values(ServiceAccessLevel).map((level) => ({
            label: formatStatisticLabel(level),
            count: snapshot.services.filter((service) => service.access_level === level).length,
            color: accessColors[level],
        }));

        const serviceTotals = new Map(
            snapshot.stats.services.map((service) => [service.service_id, service.total]),
        );
        const serviceActivity = snapshot.services
            .map((service) => ({
                label: service.name,
                count: serviceTotals.get(service.id) ?? 0,
                color: theme.palette.primary.main,
            }))
            .filter((service) => service.count > 0)
            .sort((left, right) => right.count - left.count || left.label.localeCompare(right.label))
            .slice(0, 8);

        return {
            availableServices,
            aiServices,
            taskStatuses,
            serviceStatuses,
            accessLevels,
            serviceActivity,
        };
    }, [snapshot, theme]);

    if (isLoading && !snapshot) {
        return (
            <Stack direction="row" alignItems="center" spacing={1.5} sx={{py: 5}}>
                <CircularProgress size={24}/>
                <Typography color="text.secondary">Loading engine statistics…</Typography>
            </Stack>
        );
    }

    if (!snapshot || !view) {
        return (
            <Alert
                severity="error"
                action={<Button color="inherit" size="small" onClick={loadSnapshot}>Retry</Button>}
                sx={{mt: 3}}
            >
                {error || 'Unable to load engine statistics.'}
            </Alert>
        );
    }

    const metrics: MetricProps[] = [
        {
            label: 'Services',
            value: snapshot.services.length,
            detail: `${view.availableServices.toLocaleString()} available`,
        },
        {
            label: 'Pipelines',
            value: snapshot.pipelines.length,
            detail: 'Registered workflows',
        },
        {
            label: 'Users',
            value: snapshot.users.length,
            detail: `${snapshot.users.filter((user) => user.role === 'admin').length.toLocaleString()} administrators`,
        },
        {
            label: 'Tasks',
            value: snapshot.stats.total,
            detail: 'Across all services',
        },
        {
            label: 'AI services',
            value: view.aiServices,
            detail: 'Declared in service metadata',
        },
    ];

    return (
        <Box sx={{width: '100%', maxWidth: 1440, mx: 'auto', mt: 1}}>
            <Stack
                direction={{xs: 'column', sm: 'row'}}
                alignItems={{xs: 'stretch', sm: 'center'}}
                justifyContent="space-between"
                spacing={2}
            >
                <Box>
                    <Typography color="text.secondary">
                        Current engine snapshot from the existing catalog and task statistics.
                    </Typography>
                    {lastUpdated && (
                        <Typography variant="caption" color="text.secondary">
                            Updated {lastUpdated.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'})}
                        </Typography>
                    )}
                </Box>
                <Button
                    variant="outlined"
                    startIcon={isLoading ? <CircularProgress size={16}/> : <RefreshOutlined/>}
                    onClick={loadSnapshot}
                    disabled={isLoading}
                    sx={{alignSelf: 'flex-start', textTransform: 'none'}}
                >
                    Refresh
                </Button>
            </Stack>

            {error && (
                <Alert severity="error" sx={{mt: 2}}>
                    {error}
                </Alert>
            )}

            <Paper
                variant="outlined"
                elevation={0}
                sx={{
                    display: 'grid',
                    gridTemplateColumns: {
                        xs: 'repeat(2, minmax(0, 1fr))',
                        sm: 'repeat(2, minmax(0, 1fr))',
                        md: 'repeat(5, minmax(0, 1fr))',
                    },
                    mt: 3,
                    overflow: 'hidden',
                    '& > *': {
                        borderRight: '1px solid',
                        borderBottom: '1px solid',
                        borderColor: 'divider',
                    },
                    '& > *:last-child': {
                        gridColumn: {xs: '1 / -1', md: 'auto'},
                    },
                }}
            >
                {metrics.map((metric) => <Metric key={metric.label} {...metric}/>)}
            </Paper>

            <Box
                sx={{
                    display: 'grid',
                    gridTemplateColumns: {xs: '1fr', lg: 'repeat(2, minmax(0, 1fr))'},
                    gap: {xs: 5, lg: 7},
                    mt: 5,
                }}
            >
                <Box component="section">
                    <Box
                        sx={{
                            borderTop: '2px solid',
                            borderColor: 'primary.main',
                            pt: 2,
                            mb: 3,
                        }}
                    >
                        <Typography variant="h6" fontWeight={650}>Task status</Typography>
                        <Typography variant="body2" color="text.secondary">
                            Share and exact count of tasks in each recorded status.
                        </Typography>
                    </Box>
                    <StatisticsDonut
                        items={view.taskStatuses}
                        total={snapshot.stats.total}
                        ariaLabel="Task distribution grouped by status"
                    />
                </Box>

                <Box component="section">
                    <Box
                        sx={{
                            display: 'flex',
                            flexDirection: {xs: 'column', sm: 'row'},
                            alignItems: {xs: 'flex-start', sm: 'baseline'},
                            justifyContent: 'space-between',
                            borderTop: '2px solid',
                            borderColor: 'primary.main',
                            pt: 2,
                            mb: 3,
                        }}
                    >
                        <Box>
                            <Typography variant="h6" fontWeight={650}>Most active services</Typography>
                            <Typography variant="body2" color="text.secondary">
                                Top registered services by total task volume.
                            </Typography>
                        </Box>
                        <Typography variant="caption" color="text.secondary">
                            Up to 8 services
                        </Typography>
                    </Box>

                    <HorizontalBars
                        items={view.serviceActivity.map((item, index) => ({
                            ...item,
                            color: index === 0
                                ? theme.palette.primary.main
                                : alpha(theme.palette.primary.main, Math.max(0.35, 0.85 - index * 0.07)),
                        }))}
                        ariaLabel="Most active services by total task count"
                    />
                </Box>
            </Box>

            <Box component="section" sx={{mt: 5}}>
                <Box
                    sx={{
                        borderTop: '1px solid',
                        borderColor: 'divider',
                        pt: 2,
                        mb: 3,
                    }}
                >
                    <Typography variant="h6" fontWeight={650}>Service profile</Typography>
                    <Typography variant="body2" color="text.secondary">
                        Operational state and configured audience.
                    </Typography>
                </Box>

                <Box
                    sx={{
                        display: 'grid',
                        gridTemplateColumns: {xs: '1fr', md: 'repeat(2, minmax(0, 1fr))'},
                        gap: {xs: 4, md: 7},
                    }}
                >
                    <Box>
                        <Typography variant="subtitle2" fontWeight={650} sx={{mb: 1.5}}>
                            Availability
                        </Typography>
                        <Distribution
                            items={view.serviceStatuses}
                            ariaLabel="Service count grouped by availability"
                        />
                    </Box>

                    <Box>
                        <Typography variant="subtitle2" fontWeight={650} sx={{mb: 1.5}}>
                            Access level
                        </Typography>
                        <Distribution
                            items={view.accessLevels}
                            ariaLabel="Service count grouped by access level"
                        />
                    </Box>
                </Box>

                <Typography variant="caption" color="text.secondary" sx={{display: 'block', mt: 3}}>
                    AI capability comes from service metadata. GPU capability is not currently
                    exposed by the service model.
                </Typography>
            </Box>

        </Box>
    );
};

export default AdminEngineStatistics;
