import {
    AutoAwesomeOutlined,
    RefreshOutlined,
    ScheduleOutlined,
} from '@mui/icons-material';
import {
    Alert,
    Autocomplete,
    Box,
    Button,
    Chip,
    CircularProgress,
    Divider,
    Paper,
    Stack,
    TextField,
    Typography,
    useTheme,
} from '@mui/material';
import { ServiceAccessLevel } from 'enums/serviceAccessLevelEnum';
import { ServiceStatus } from 'enums/serviceStatusEnum';
import { Service } from 'models/Service';
import { Stats } from 'models/Stats';
import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { getAllAdminServices, getStats } from 'utils/api';
import { getStoredAuthenticationToken } from 'utils/authentication';
import { RunState } from 'utils/reducers/runStateSlice';
import StatisticsDonut, {formatStatisticLabel} from './StatisticsDonut';

type ServiceStatisticsSnapshot = {
    stats: Stats;
    services: Service[];
};

type MetricProps = {
    label: string;
    value: string | number;
    detail: string;
};

const Metric = ({label, value, detail}: MetricProps) => (
    <Box sx={{minWidth: 0, px: {xs: 2, md: 3}, py: {xs: 2, md: 2.5}}}>
        <Typography variant="overline" color="text.secondary" fontWeight={700}>
            {label}
        </Typography>
        <Typography variant="h4" fontWeight={650} sx={{mt: 0.25}}>
            {typeof value === 'number' ? value.toLocaleString() : value}
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{mt: 0.25}}>
            {detail}
        </Typography>
    </Box>
);

const statusChipColor = (
    status: ServiceStatus,
): 'success' | 'warning' | 'error' | 'default' => {
    if (status === ServiceStatus.AVAILABLE) return 'success';
    if (status === ServiceStatus.SLEEPING) return 'warning';
    if (status === ServiceStatus.UNAVAILABLE) return 'error';
    return 'default';
};

const formatRate = (count: number, total: number) => (
    total > 0 ? `${((count / total) * 100).toFixed(1)}%` : '—'
);

const AdminServiceStatistics: React.FC = () => {
    const theme = useTheme();
    const [snapshot, setSnapshot] = useState<ServiceStatisticsSnapshot | null>(null);
    const [selectedServiceId, setSelectedServiceId] = useState<string | null>(null);
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
            const [statsResult, services] = await Promise.all([
                getStats(),
                getAllAdminServices(token),
            ]);

            if (!statsResult || typeof statsResult.total !== 'number') {
                throw new Error(statsResult?.error ?? 'Unable to load task statistics.');
            }

            if (requestId !== requestSequence.current) return;

            const nextSnapshot = {
                stats: statsResult as Stats,
                services,
            };
            setSnapshot(nextSnapshot);
            setSelectedServiceId((currentServiceId) => {
                if (currentServiceId && services.some((service) => service.id === currentServiceId)) {
                    return currentServiceId;
                }

                const totals = new Map(
                    nextSnapshot.stats.services.map((service) => [
                        service.service_id,
                        service.total,
                    ]),
                );
                return [...services].sort((left, right) => (
                    (totals.get(right.id) ?? 0) - (totals.get(left.id) ?? 0)
                    || left.name.localeCompare(right.name)
                ))[0]?.id ?? null;
            });
            setLastUpdated(new Date());
        } catch (loadError) {
            if (requestId !== requestSequence.current) return;
            setError(loadError instanceof Error
                ? loadError.message
                : 'Unable to load service statistics.');
        } finally {
            if (requestId === requestSequence.current) setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        void loadSnapshot();
    }, [loadSnapshot]);

    const view = useMemo(() => {
        if (!snapshot) return null;

        const selectedService = snapshot.services.find(
            (service) => service.id === selectedServiceId,
        ) ?? null;
        if (!selectedService) return null;

        const serviceStats = snapshot.stats.services.find(
            (service) => service.service_id === selectedService.id,
        );
        const statusSource = serviceStats?.status ?? snapshot.stats.summary;
        const statusCounts = new Map(
            statusSource.map((status) => [status.status, serviceStats ? status.count : 0]),
        );
        const total = serviceStats?.total ?? 0;
        const finished = statusCounts.get(RunState.FINISHED) ?? 0;
        const errors = statusCounts.get(RunState.ERROR) ?? 0;
        const unavailable = statusCounts.get(RunState.UNAVAILABLE) ?? 0;
        const failed = errors + unavailable;

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
            archived: theme.palette.grey[700],
        };
        const taskStatuses = Array.from(statusCounts.entries())
            .map(([status, count]) => ({
                label: formatStatisticLabel(status),
                count,
                color: statusColors[status] ?? theme.palette.grey[500],
            }))
            .sort((left, right) => right.count - left.count || left.label.localeCompare(right.label));

        return {
            selectedService,
            total,
            finished,
            failed,
            taskStatuses,
        };
    }, [selectedServiceId, snapshot, theme]);

    if (isLoading && !snapshot) {
        return (
            <Stack direction="row" alignItems="center" spacing={1.5} sx={{py: 5}}>
                <CircularProgress size={24}/>
                <Typography color="text.secondary">Loading service statistics…</Typography>
            </Stack>
        );
    }

    if (!snapshot) {
        return (
            <Alert
                severity="error"
                action={<Button color="inherit" size="small" onClick={loadSnapshot}>Retry</Button>}
                sx={{mt: 3}}
            >
                {error || 'Unable to load service statistics.'}
            </Alert>
        );
    }

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
                        Inspect task outcomes and the current operational profile of one service.
                    </Typography>
                    {lastUpdated && (
                        <Typography variant="caption" color="text.secondary">
                            Updated {lastUpdated.toLocaleTimeString([], {
                                hour: '2-digit',
                                minute: '2-digit',
                            })}
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

            {error && <Alert severity="error" sx={{mt: 2}}>{error}</Alert>}

            <Box
                component="section"
                sx={{
                    display: 'grid',
                    gridTemplateColumns: {xs: '1fr', md: 'minmax(280px, 460px) minmax(0, 1fr)'},
                    gap: {xs: 2, md: 4},
                    alignItems: 'end',
                    mt: 3,
                    pb: 3,
                    borderBottom: '1px solid',
                    borderColor: 'divider',
                }}
            >
                <Autocomplete
                    options={snapshot.services}
                    value={view?.selectedService ?? null}
                    onChange={(_, service) => setSelectedServiceId(service?.id ?? null)}
                    getOptionLabel={(service) => service.name}
                    isOptionEqualToValue={(option, value) => option.id === value.id}
                    renderInput={(params) => (
                        <TextField
                            {...params}
                            label="Service"
                            placeholder="Search services"
                        />
                    )}
                    noOptionsText="No services found"
                />

                {view && (
                    <Stack spacing={1}>
                        <Stack
                            direction={{xs: 'column', sm: 'row'}}
                            alignItems={{xs: 'flex-start', sm: 'center'}}
                            spacing={1}
                        >
                            <Typography variant="h6" fontWeight={650}>
                                {view.selectedService.name}
                            </Typography>
                            <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                                <Chip
                                    size="small"
                                    variant="outlined"
                                    color={statusChipColor(view.selectedService.status)}
                                    label={formatStatisticLabel(view.selectedService.status)}
                                />
                                <Chip
                                    size="small"
                                    variant="outlined"
                                    label={`${formatStatisticLabel(
                                        view.selectedService.access_level
                                        ?? ServiceAccessLevel.PUBLIC,
                                    )} access`}
                                />
                                {view.selectedService.has_ai && (
                                    <Chip
                                        size="small"
                                        variant="outlined"
                                        color="primary"
                                        icon={<AutoAwesomeOutlined/>}
                                        label="AI"
                                    />
                                )}
                            </Stack>
                        </Stack>
                        <Typography variant="body2" color="text.secondary">
                            {view.selectedService.summary || view.selectedService.slug}
                        </Typography>
                    </Stack>
                )}
            </Box>

            {!view ? (
                <Alert severity="info" sx={{mt: 3}}>
                    No registered services are available to inspect.
                </Alert>
            ) : (
                <>
                    <Paper
                        variant="outlined"
                        elevation={0}
                        sx={{
                            display: 'grid',
                            gridTemplateColumns: {
                                xs: 'repeat(2, minmax(0, 1fr))',
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
                        <Metric label="Total tasks" value={view.total} detail="All recorded tasks"/>
                        <Metric label="Finished" value={view.finished} detail="Completed successfully"/>
                        <Metric
                            label="Failed"
                            value={view.failed}
                            detail="Error or unavailable"
                        />
                        <Metric
                            label="Success rate"
                            value={formatRate(view.finished, view.total)}
                            detail="Finished / total"
                        />
                        <Metric
                            label="Failure rate"
                            value={formatRate(view.failed, view.total)}
                            detail="Failed / total"
                        />
                    </Paper>

                    <Box
                        sx={{
                            display: 'grid',
                            gridTemplateColumns: {xs: '1fr', lg: 'minmax(0, 1.25fr) minmax(300px, 0.75fr)'},
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
                                    Share and exact count of tasks in every recorded status.
                                </Typography>
                            </Box>
                            <StatisticsDonut
                                items={view.taskStatuses}
                                total={view.total}
                                ariaLabel={`${view.selectedService.name} tasks grouped by status`}
                            />
                        </Box>

                        <Box component="section">
                            <Box
                                sx={{
                                    borderTop: '2px solid',
                                    borderColor: 'primary.main',
                                    pt: 2,
                                    mb: 1,
                                }}
                            >
                                <Typography variant="h6" fontWeight={650}>Service profile</Typography>
                                <Typography variant="body2" color="text.secondary">
                                    Current catalog metadata and availability.
                                </Typography>
                            </Box>

                            <Stack divider={<Divider flexItem/>}>
                                <Stack direction="row" justifyContent="space-between" spacing={2} py={2}>
                                    <Typography color="text.secondary">Availability</Typography>
                                    <Typography fontWeight={650}>
                                        {formatStatisticLabel(view.selectedService.status)}
                                    </Typography>
                                </Stack>
                                <Stack direction="row" justifyContent="space-between" spacing={2} py={2}>
                                    <Typography color="text.secondary">Access level</Typography>
                                    <Typography fontWeight={650}>
                                        {formatStatisticLabel(
                                            view.selectedService.access_level
                                            ?? ServiceAccessLevel.PUBLIC,
                                        )}
                                    </Typography>
                                </Stack>
                                <Stack direction="row" justifyContent="space-between" spacing={2} py={2}>
                                    <Stack direction="row" alignItems="center" spacing={1}>
                                        <AutoAwesomeOutlined fontSize="small"/>
                                        <Typography color="text.secondary">AI service</Typography>
                                    </Stack>
                                    <Typography fontWeight={650}>
                                        {view.selectedService.has_ai ? 'Yes' : 'No'}
                                    </Typography>
                                </Stack>
                                <Stack direction="row" justifyContent="space-between" spacing={2} py={2}>
                                    <Typography color="text.secondary">GPU capability</Typography>
                                    <Typography color="text.secondary">Not exposed</Typography>
                                </Stack>
                            </Stack>
                        </Box>
                    </Box>

                    <Box component="section" sx={{mt: 5}}>
                        <Box
                            sx={{
                                borderTop: '1px solid',
                                borderColor: 'divider',
                                pt: 2,
                            }}
                        >
                            <Stack
                                direction={{xs: 'column', sm: 'row'}}
                                justifyContent="space-between"
                                alignItems={{xs: 'flex-start', sm: 'center'}}
                                spacing={2}
                            >
                                <Box>
                                    <Typography variant="h6" fontWeight={650}>
                                        Recent usage
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary">
                                        The current statistics endpoint provides aggregate counts,
                                        without timestamps or a usage history.
                                    </Typography>
                                </Box>
                                <Stack direction="row" alignItems="center" spacing={1}>
                                    <ScheduleOutlined color="disabled"/>
                                    <Typography variant="body2" color="text.secondary">
                                        No timeline available
                                    </Typography>
                                </Stack>
                            </Stack>
                        </Box>
                    </Box>

                </>
            )}
        </Box>
    );
};

export default AdminServiceStatistics;
