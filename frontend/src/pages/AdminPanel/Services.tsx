import { PowerSettingsNewOutlined } from '@mui/icons-material';
import {
    Alert,
    Box,
    Button,
    Chip,
    CircularProgress,
    FormControl,
    IconButton,
    MenuItem,
    Paper,
    Select,
    SelectChangeEvent,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Tooltip,
    Typography,
} from '@mui/material';
import React, { useCallback, useEffect, useState } from 'react';
import { ServiceAccessLevel } from 'enums/serviceAccessLevelEnum';
import { ServiceStatus } from 'enums/serviceStatusEnum';
import { Service } from 'models/Service';
import { getAllAdminServices, updateServiceAccess, wakeUp } from 'utils/api';
import { getStoredAuthenticationToken } from 'utils/authentication';

const accessLabels: Record<ServiceAccessLevel, string> = {
    [ServiceAccessLevel.PUBLIC]: 'Public',
    [ServiceAccessLevel.USER]: 'Users',
    [ServiceAccessLevel.ADMIN]: 'Administrators',
    [ServiceAccessLevel.DISABLED]: 'Disabled',
};

const statusColor = (status: ServiceStatus): 'success' | 'error' | 'warning' | 'default' => {
    if (status === ServiceStatus.AVAILABLE) return 'success';
    if (status === ServiceStatus.UNAVAILABLE) return 'error';
    if (status === ServiceStatus.SLEEPING) return 'warning';
    return 'default';
};

const AdminServices: React.FC = () => {
    const [services, setServices] = useState<Service[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [updatingServiceId, setUpdatingServiceId] = useState<string | null>(null);
    const [wakingServiceId, setWakingServiceId] = useState<string | null>(null);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    const loadServices = useCallback(async () => {
        const token = getStoredAuthenticationToken();
        if (!token) {
            setError('Your session is no longer valid.');
            setIsLoading(false);
            return;
        }

        setError('');
        setSuccess('');
        setIsLoading(true);
        try {
            setServices(await getAllAdminServices(token));
        } catch (loadError) {
            setError(loadError instanceof Error ? loadError.message : 'Unable to load services.');
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        void loadServices();
    }, [loadServices]);

    const changeAccess = async (serviceId: string, event: SelectChangeEvent<ServiceAccessLevel>) => {
        const token = getStoredAuthenticationToken();
        if (!token) {
            setError('Your session is no longer valid.');
            return;
        }

        setError('');
        setSuccess('');
        setUpdatingServiceId(serviceId);
        try {
            const updatedService = await updateServiceAccess(
                token,
                serviceId,
                event.target.value as ServiceAccessLevel,
            );
            setServices((currentServices) => currentServices.map(
                (service) => service.id === serviceId ? updatedService : service,
            ));
        } catch (updateError) {
            setError(updateError instanceof Error ? updateError.message : 'Unable to update service access.');
        } finally {
            setUpdatingServiceId(null);
        }
    };

    const wakeService = async (service: Service) => {
        const token = getStoredAuthenticationToken();
        if (!token) {
            setError('Your session is no longer valid.');
            return;
        }

        setError('');
        setSuccess('');
        setWakingServiceId(service.id);

        try {
            const result = await wakeUp(service.id);
            if (result.error) throw new Error(result.error);

            setServices(await getAllAdminServices(token));
            setSuccess(`Wake-up request sent to ${service.name}.`);
        } catch (wakeError) {
            setError(wakeError instanceof Error ? wakeError.message : 'Unable to wake this service.');
        } finally {
            setWakingServiceId(null);
        }
    };

    return (
        <Box sx={{mt: 1}}>
            <Typography color="text.secondary" sx={{mb: 3}}>
                Control which audience can discover and use each registered service.
            </Typography>

            {error && (
                <Alert
                    severity="error"
                    action={<Button color="inherit" size="small" onClick={loadServices}>Retry</Button>}
                    sx={{mb: 3}}
                >
                    {error}
                </Alert>
            )}

            {success && (
                <Alert severity="success" sx={{mb: 3}} onClose={() => setSuccess('')}>
                    {success}
                </Alert>
            )}

            {isLoading ? (
                <Box sx={{display: 'flex', alignItems: 'center', gap: 1.5, py: 4}}>
                    <CircularProgress size={24}/>
                    <Typography color="text.secondary">Loading services…</Typography>
                </Box>
            ) : (
                <TableContainer component={Paper} variant="outlined" elevation={0}>
                    <Table aria-label="Services" sx={{minWidth: 800}}>
                        <TableHead>
                            <TableRow>
                                <TableCell>Name</TableCell>
                                <TableCell>Slug</TableCell>
                                <TableCell>Status</TableCell>
                                <TableCell sx={{width: 260}}>Access level</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {services.map((service) => {
                                const isUpdating = updatingServiceId === service.id;
                                const isWaking = wakingServiceId === service.id;
                                const isSleeping = service.status === ServiceStatus.SLEEPING;
                                return (
                                    <TableRow key={service.id} hover>
                                        <TableCell>
                                            <Typography fontWeight={600}>{service.name}</Typography>
                                            <Typography variant="body2" color="text.secondary">
                                                {service.summary}
                                            </Typography>
                                        </TableCell>
                                        <TableCell>{service.slug}</TableCell>
                                        <TableCell>
                                            <Box sx={{display: 'flex', alignItems: 'center', gap: 0.75}}>
                                                <Chip
                                                    label={service.status}
                                                    size="small"
                                                    color={statusColor(service.status)}
                                                    variant="outlined"
                                                    sx={{textTransform: 'capitalize', fontWeight: 600}}
                                                />
                                                {isSleeping && (
                                                    <Tooltip title="Wake service" arrow>
                                                        <span>
                                                            <IconButton
                                                                size="small"
                                                                color="primary"
                                                                aria-label={`Wake ${service.name}`}
                                                                onClick={() => wakeService(service)}
                                                                disabled={wakingServiceId !== null}
                                                            >
                                                                {isWaking
                                                                    ? <CircularProgress size={17} color="inherit"/>
                                                                    : <PowerSettingsNewOutlined fontSize="small"/>}
                                                            </IconButton>
                                                        </span>
                                                    </Tooltip>
                                                )}
                                            </Box>
                                        </TableCell>
                                        <TableCell>
                                            <Box sx={{display: 'flex', alignItems: 'center', gap: 1.25}}>
                                                <FormControl size="small" fullWidth>
                                                    <Select<ServiceAccessLevel>
                                                        value={service.access_level}
                                                        onChange={(event) => changeAccess(service.id, event)}
                                                        disabled={isUpdating}
                                                        aria-label={`Access level for ${service.name}`}
                                                        sx={{bgcolor: 'background.paper'}}
                                                    >
                                                        {Object.values(ServiceAccessLevel).map((level) => (
                                                            <MenuItem key={level} value={level}>
                                                                {accessLabels[level]}
                                                            </MenuItem>
                                                        ))}
                                                    </Select>
                                                </FormControl>
                                                {isUpdating && <CircularProgress size={18}/>} 
                                            </Box>
                                        </TableCell>
                                    </TableRow>
                                );
                            })}
                            {services.length === 0 && (
                                <TableRow>
                                    <TableCell colSpan={4} align="center" sx={{py: 5, color: 'text.secondary'}}>
                                        No services found.
                                    </TableCell>
                                </TableRow>
                            )}
                        </TableBody>
                    </Table>
                </TableContainer>
            )}
        </Box>
    );
};

export default AdminServices;
