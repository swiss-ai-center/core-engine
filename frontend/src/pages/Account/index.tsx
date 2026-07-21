import { BadgeOutlined, EditOutlined, MailOutline, PersonOutline, SaveOutlined } from '@mui/icons-material';
import {
    Alert,
    Avatar,
    Box,
    Button,
    Chip,
    CircularProgress,
    Container,
    Divider,
    Stack,
    TextField,
    Toolbar,
    Typography,
} from '@mui/material';
import React, { FormEvent, useEffect, useState } from 'react';
import { useDispatch } from 'react-redux';
import { useAuthentication } from 'utils/hooks/authentication';
import { setMenuIcon } from 'utils/reducers/menuIconSlice';

const Detail = ({label, value}: { label: string, value: string }) => (
    <Box>
        <Typography component="dt" variant="caption" color="text.secondary" fontWeight={600}>
            {label}
        </Typography>
        <Typography component="dd" sx={{m: 0, mt: 0.5, fontSize: '1rem', overflowWrap: 'anywhere'}}>
            {value}
        </Typography>
    </Box>
);

const Account: React.FC = () => {
    const dispatch = useDispatch();
    const {user, isCheckingSession, updateNames} = useAuthentication();
    const [isEditingNames, setIsEditingNames] = useState(false);
    const [firstName, setFirstName] = useState('');
    const [lastName, setLastName] = useState('');
    const [isSavingNames, setIsSavingNames] = useState(false);
    const [nameError, setNameError] = useState('');

    useEffect(() => {
        dispatch(setMenuIcon(false));
    }, [dispatch]);

    useEffect(() => {
        if (!user) return;
        setFirstName(user.first_name);
        setLastName(user.last_name);
    }, [user]);

    const startEditingNames = () => {
        if (!user) return;
        setFirstName(user.first_name);
        setLastName(user.last_name);
        setNameError('');
        setIsEditingNames(true);
    };

    const cancelEditingNames = () => {
        if (user) {
            setFirstName(user.first_name);
            setLastName(user.last_name);
        }
        setNameError('');
        setIsEditingNames(false);
    };

    const saveNames = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        setNameError('');
        setIsSavingNames(true);

        try {
            await updateNames(firstName.trim(), lastName.trim());
            setIsEditingNames(false);
        } catch (error) {
            setNameError(error instanceof Error ? error.message : 'Unable to update your profile.');
        } finally {
            setIsSavingNames(false);
        }
    };

    return (
        <Box component="main" sx={{flexGrow: 1, py: {xs: 3, md: 5}}}>
            <Toolbar/>
            <Container maxWidth="lg">
                <Box sx={{mb: 4}}>
                    <Typography component="h1" variant="h4" fontWeight={600}>Account</Typography>
                    <Typography color="text.secondary" sx={{mt: 0.75}}>
                        Your profile and account information.
                    </Typography>
                </Box>

                {isCheckingSession ? (
                    <CircularProgress size={28}/>
                ) : !user ? (
                    <Alert severity="info">Sign in to view your account.</Alert>
                ) : (
                    <Box
                        sx={{
                            display: 'grid',
                            gridTemplateColumns: {xs: '1fr', md: '300px minmax(0, 1fr)'},
                            bgcolor: 'background.paper',
                            border: '1px solid',
                            borderColor: 'divider',
                            borderRadius: 2,
                            overflow: 'hidden',
                        }}
                    >
                        <Box
                            sx={{
                                p: {xs: 3, md: 4},
                                color: 'primary.contrastText',
                                bgcolor: 'primary.main',
                                display: 'flex',
                                flexDirection: 'column',
                                alignItems: {xs: 'flex-start', md: 'center'},
                                textAlign: {xs: 'left', md: 'center'},
                            }}
                        >
                            <Avatar
                                sx={{
                                    width: 88,
                                    height: 88,
                                    mb: 2.5,
                                    bgcolor: 'rgba(255, 255, 255, 0.18)',
                                    color: 'inherit',
                                    fontSize: '1.75rem',
                                    fontWeight: 700,
                                    border: '1px solid rgba(255, 255, 255, 0.35)',
                                }}
                            >
                                {`${user.first_name.charAt(0)}${user.last_name.charAt(0)}`.toUpperCase()}
                            </Avatar>
                            <Typography variant="h5" fontWeight={600}>
                                {user.first_name} {user.last_name}
                            </Typography>
                            <Typography sx={{mt: 0.75, opacity: 0.85, overflowWrap: 'anywhere'}}>
                                {user.email}
                            </Typography>
                            <Chip
                                label={user.role}
                                size="small"
                                sx={{
                                    mt: 2.5,
                                    color: 'inherit',
                                    bgcolor: 'rgba(255, 255, 255, 0.16)',
                                    textTransform: 'capitalize',
                                    fontWeight: 600,
                                }}
                            />
                        </Box>

                        <Box sx={{p: {xs: 3, md: 4.5}}}>
                            <Stack spacing={4} divider={<Divider/>}>
                                <Box>
                                    <Stack
                                        direction="row"
                                        alignItems="center"
                                        justifyContent="space-between"
                                        spacing={2}
                                        sx={{mb: 3}}
                                    >
                                        <Stack direction="row" spacing={1.25} alignItems="center">
                                            <PersonOutline color="primary"/>
                                            <Typography variant="h6" fontWeight={600}>Personal information</Typography>
                                        </Stack>
                                        {!isEditingNames && (
                                            <Button
                                                size="small"
                                                startIcon={<EditOutlined/>}
                                                onClick={startEditingNames}
                                                sx={{textTransform: 'none'}}
                                            >
                                                Edit
                                            </Button>
                                        )}
                                    </Stack>
                                    {isEditingNames ? (
                                        <Box component="form" onSubmit={saveNames}>
                                            {nameError && <Alert severity="error" sx={{mb: 2}}>{nameError}</Alert>}
                                            <Box
                                                sx={{
                                                    display: 'grid',
                                                    gridTemplateColumns: {xs: '1fr', sm: 'repeat(2, minmax(0, 1fr))'},
                                                    gap: 2,
                                                }}
                                            >
                                                <TextField
                                                    autoFocus
                                                    required
                                                    fullWidth
                                                    label="First name"
                                                    value={firstName}
                                                    onChange={(event) => setFirstName(event.target.value)}
                                                    disabled={isSavingNames}
                                                    inputProps={{maxLength: 100}}
                                                />
                                                <TextField
                                                    required
                                                    fullWidth
                                                    label="Last name"
                                                    value={lastName}
                                                    onChange={(event) => setLastName(event.target.value)}
                                                    disabled={isSavingNames}
                                                    inputProps={{maxLength: 100}}
                                                />
                                            </Box>
                                            <Stack direction="row" justifyContent="flex-end" spacing={1} sx={{mt: 2.5}}>
                                                <Button color="inherit" onClick={cancelEditingNames} disabled={isSavingNames}>
                                                    Cancel
                                                </Button>
                                                <Button
                                                    type="submit"
                                                    variant="contained"
                                                    startIcon={isSavingNames ? <CircularProgress size={16} color="inherit"/> : <SaveOutlined/>}
                                                    disabled={isSavingNames || !firstName.trim() || !lastName.trim()}
                                                >
                                                    Save
                                                </Button>
                                            </Stack>
                                        </Box>
                                    ) : (
                                        <Box
                                            component="dl"
                                            sx={{
                                                m: 0,
                                                display: 'grid',
                                                gridTemplateColumns: {xs: '1fr', sm: 'repeat(2, minmax(0, 1fr))'},
                                                gap: 3,
                                            }}
                                        >
                                            <Detail label="First name" value={user.first_name}/>
                                            <Detail label="Last name" value={user.last_name}/>
                                        </Box>
                                    )}
                                </Box>

                                <Box>
                                    <Stack direction="row" spacing={1.25} alignItems="center" sx={{mb: 3}}>
                                        <MailOutline color="primary"/>
                                        <Typography variant="h6" fontWeight={600}>Contact</Typography>
                                    </Stack>
                                    <Box component="dl" sx={{m: 0}}>
                                        <Detail label="Email address" value={user.email}/>
                                    </Box>
                                </Box>

                                <Box>
                                    <Stack direction="row" spacing={1.25} alignItems="center" sx={{mb: 3}}>
                                        <BadgeOutlined color="primary"/>
                                        <Typography variant="h6" fontWeight={600}>Account details</Typography>
                                    </Stack>
                                    <Box
                                        component="dl"
                                        sx={{
                                            m: 0,
                                            display: 'grid',
                                            gridTemplateColumns: {xs: '1fr', sm: '160px minmax(0, 1fr)'},
                                            gap: 3,
                                        }}
                                    >
                                        <Detail label="Role" value={user.role}/>
                                        <Detail label="User ID" value={user.id}/>
                                    </Box>
                                </Box>

                                {user.address && (
                                    <Box component="dl" sx={{m: 0}}>
                                        <Detail
                                            label="Address"
                                            value={`${user.address.street} ${user.address.street_nbr}, ${user.address.npa} ${user.address.city}, ${user.address.country}`}
                                        />
                                    </Box>
                                )}
                            </Stack>
                        </Box>
                    </Box>
                )}
            </Container>
        </Box>
    );
};

export default Account;
