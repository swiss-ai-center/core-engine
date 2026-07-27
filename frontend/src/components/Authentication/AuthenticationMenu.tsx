import {
    AccountCircleOutlined,
    AdminPanelSettingsOutlined,
    ArrowDropDownRounded,
    LogoutRounded,
    PersonOutlineRounded,
} from '@mui/icons-material';
import {
    Alert,
    Box,
    Button,
    CircularProgress,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    Divider,
    ListItemIcon,
    Menu,
    MenuItem,
    TextField,
    Typography,
} from '@mui/material';
import { FormEvent, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthentication } from 'utils/hooks/authentication';

export const AuthenticationMenu = () => {
    const navigate = useNavigate();
    const {user, isCheckingSession, signIn, signOut} = useAuthentication();
    const [isLoginOpen, setIsLoginOpen] = useState(false);
    const [menuAnchor, setMenuAnchor] = useState<HTMLElement | null>(null);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState('');

    const closeLogin = () => {
        if (isSubmitting) return;
        setIsLoginOpen(false);
        setError('');
        setPassword('');
    };

    const handleLogin = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        setError('');
        setIsSubmitting(true);

        try {
            await signIn(email.trim(), password);
            setIsLoginOpen(false);
            setPassword('');
        } catch (loginError) {
            setError(loginError instanceof Error ? loginError.message : 'Unable to sign in. Please try again.');
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleLogout = async () => {
        setMenuAnchor(null);
        await signOut();
        setEmail('');
        setPassword('');
    };

    if (isCheckingSession) {
        return <CircularProgress color="inherit" size={20} sx={{ mx: 1.5 }} aria-label="Checking sign-in status"/>;
    }

    return (
        <>
            {user ? (
                <Button
                    color="inherit"
                    onClick={(event) => setMenuAnchor(event.currentTarget)}
                    endIcon={<ArrowDropDownRounded/>}
                    aria-controls={menuAnchor ? 'account-menu' : undefined}
                    aria-haspopup="true"
                    aria-expanded={Boolean(menuAnchor)}
                    sx={{
                        ml: 0.5,
                        maxWidth: {xs: 150, sm: 260},
                        textTransform: 'none',
                        fontWeight: 600,
                    }}
                >
                    <Box component="span" sx={{overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap'}}>
                        {user.email}
                    </Box>
                </Button>
            ) : (
                <Button
                    color="inherit"
                    variant="outlined"
                    startIcon={<PersonOutlineRounded/>}
                    onClick={() => setIsLoginOpen(true)}
                    sx={{
                        ml: 0.5,
                        borderColor: 'currentColor',
                        textTransform: 'none',
                        fontWeight: 600,
                        '&:hover': {borderColor: 'currentColor'},
                    }}
                >
                    Sign in
                </Button>
            )}

            <Menu
                id="account-menu"
                anchorEl={menuAnchor}
                open={Boolean(menuAnchor)}
                onClose={() => setMenuAnchor(null)}
                anchorOrigin={{horizontal: 'right', vertical: 'bottom'}}
                transformOrigin={{horizontal: 'right', vertical: 'top'}}
            >
                <MenuItem onClick={() => { setMenuAnchor(null); navigate('/account'); }}>
                    <ListItemIcon><AccountCircleOutlined fontSize="small"/></ListItemIcon>
                    Account
                </MenuItem>
                <MenuItem onClick={() => { setMenuAnchor(null); navigate('/admin/users'); }}>
                    <ListItemIcon><AdminPanelSettingsOutlined fontSize="small"/></ListItemIcon>
                    Admin panel
                </MenuItem>
                <Divider/>
                <MenuItem onClick={handleLogout}>
                    <ListItemIcon><LogoutRounded fontSize="small"/></ListItemIcon>
                    Logout
                </MenuItem>
            </Menu>

            <Dialog
                open={isLoginOpen}
                onClose={closeLogin}
                fullWidth
                maxWidth="xs"
                PaperProps={{component: 'form', onSubmit: handleLogin}}
            >
                <DialogTitle sx={{pb: 1}}>Sign in</DialogTitle>
                <DialogContent>
                    <Typography color="text.secondary" sx={{mb: 2.5}}>
                        Sign in to your Swiss AI Center account.
                    </Typography>
                    {error && <Alert severity="error" sx={{mb: 2}}>{error}</Alert>}
                    <TextField
                        autoFocus
                        required
                        fullWidth
                        type="email"
                        label="Email address"
                        autoComplete="email"
                        value={email}
                        onChange={(event) => setEmail(event.target.value)}
                        disabled={isSubmitting}
                        sx={{mb: 2}}
                    />
                    <TextField
                        required
                        fullWidth
                        type="password"
                        label="Password"
                        autoComplete="current-password"
                        value={password}
                        onChange={(event) => setPassword(event.target.value)}
                        disabled={isSubmitting}
                    />
                    <Button disabled variant="text" sx={{mt: 1.25, ml: -1, textTransform: 'none'}}>
                        Register (soon)
                    </Button>
                </DialogContent>
                <DialogActions sx={{px: 3, pb: 3}}>
                    <Button onClick={closeLogin} color="inherit" disabled={isSubmitting}>Cancel</Button>
                    <Button type="submit" variant="contained" disabled={isSubmitting} sx={{minWidth: 92}}>
                        {isSubmitting ? <CircularProgress size={20} color="inherit"/> : 'Sign in'}
                    </Button>
                </DialogActions>
            </Dialog>
        </>
    );
};
