import { KeyboardArrowDownRounded, KeyboardArrowUpRounded } from '@mui/icons-material';
import {
    Alert,
    Box,
    Button,
    Chip,
    CircularProgress,
    Paper,
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
import { AuthenticatedUser, UserRole } from 'models/AuthenticatedUser';
import { getStoredAuthenticationToken, getUsers, updateUserRole } from 'utils/authentication';
import { useAuthentication } from 'utils/hooks/authentication';

const AdminUsers: React.FC = () => {
    const {user: currentUser} = useAuthentication();
    const [users, setUsers] = useState<AuthenticatedUser[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [updatingUserId, setUpdatingUserId] = useState<string | null>(null);
    const [error, setError] = useState('');

    const loadUsers = useCallback(async () => {
        const token = getStoredAuthenticationToken();
        if (!token) {
            setError('Your session is no longer valid.');
            setIsLoading(false);
            return;
        }

        setError('');
        setIsLoading(true);
        try {
            setUsers(await getUsers(token));
        } catch (loadError) {
            setError(loadError instanceof Error ? loadError.message : 'Unable to load users.');
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        void loadUsers();
    }, [loadUsers]);

    const changeRole = async (userId: string, role: UserRole) => {
        const token = getStoredAuthenticationToken();
        if (!token) {
            setError('Your session is no longer valid.');
            return;
        }

        setError('');
        setUpdatingUserId(userId);
        try {
            const updatedUser = await updateUserRole(token, userId, role);
            setUsers((currentUsers) => currentUsers.map((user) => user.id === userId ? updatedUser : user));
        } catch (roleError) {
            setError(roleError instanceof Error ? roleError.message : 'Unable to update this user\'s role.');
        } finally {
            setUpdatingUserId(null);
        }
    };

    return (
        <Box sx={{mt: 1}}>
            <Typography color="text.secondary" sx={{mb: 3}}>
                Manage user access to the Core Engine.
            </Typography>

            {error && (
                <Alert
                    severity="error"
                    action={<Button color="inherit" size="small" onClick={loadUsers}>Retry</Button>}
                    sx={{mb: 3}}
                >
                    {error}
                </Alert>
            )}

            {isLoading ? (
                <Box sx={{display: 'flex', alignItems: 'center', gap: 1.5, py: 4}}>
                    <CircularProgress size={24}/>
                    <Typography color="text.secondary">Loading users…</Typography>
                </Box>
            ) : (
                <TableContainer component={Paper} variant="outlined" elevation={0}>
                    <Table aria-label="Users">
                        <TableHead>
                            <TableRow>
                                <TableCell>Name</TableCell>
                                <TableCell>Email address</TableCell>
                                <TableCell>Role</TableCell>
                                <TableCell align="right">Access</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {users.map((user) => {
                                const isCurrentUser = user.id === currentUser?.id;
                                const nextRole = user.role === 'admin' ? 'user' : 'admin';
                                const isUpdating = updatingUserId === user.id;

                                return (
                                    <TableRow key={user.id} hover>
                                        <TableCell>
                                            <Typography fontWeight={600}>
                                                {user.first_name} {user.last_name}
                                                {isCurrentUser && (
                                                    <Typography component="span" variant="caption" color="text.secondary" sx={{ml: 1}}>
                                                        You
                                                    </Typography>
                                                )}
                                            </Typography>
                                        </TableCell>
                                        <TableCell sx={{overflowWrap: 'anywhere'}}>{user.email}</TableCell>
                                        <TableCell>
                                            <Chip
                                                label={user.role}
                                                size="small"
                                                color={user.role === 'admin' ? 'primary' : 'default'}
                                                variant={user.role === 'admin' ? 'filled' : 'outlined'}
                                                sx={{textTransform: 'capitalize', fontWeight: 600}}
                                            />
                                        </TableCell>
                                        <TableCell align="right">
                                            <Tooltip title={isCurrentUser ? 'You cannot change your own role.' : ''}>
                                                <span>
                                                    <Button
                                                        size="small"
                                                        variant={user.role === 'admin' ? 'outlined' : 'contained'}
                                                        color={user.role === 'admin' ? 'inherit' : 'primary'}
                                                        startIcon={
                                                            isUpdating
                                                                ? <CircularProgress size={15} color="inherit"/>
                                                                : user.role === 'admin'
                                                                    ? <KeyboardArrowDownRounded/>
                                                                    : <KeyboardArrowUpRounded/>
                                                        }
                                                        disabled={isCurrentUser || isUpdating}
                                                        onClick={() => changeRole(user.id, nextRole)}
                                                        sx={{minWidth: 112, textTransform: 'none'}}
                                                    >
                                                        {user.role === 'admin' ? 'Downgrade' : 'Promote'}
                                                    </Button>
                                                </span>
                                            </Tooltip>
                                        </TableCell>
                                    </TableRow>
                                );
                            })}
                            {users.length === 0 && (
                                <TableRow>
                                    <TableCell colSpan={4} align="center" sx={{py: 5, color: 'text.secondary'}}>
                                        No users found.
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

export default AdminUsers;
