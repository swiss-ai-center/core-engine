import React, { ReactNode, useCallback, useEffect, useMemo, useState } from 'react';
import { AuthenticatedUser } from 'models/AuthenticatedUser';
import {
    clearAuthenticationToken,
    getCurrentUser,
    getStoredAuthenticationToken,
    login,
    logout,
    storeAuthenticationToken,
    updateCurrentUserNames,
} from 'utils/authentication';
import { AuthenticationContext } from 'utils/contexts/authentication';

export const AuthenticationProvider = ({children}: { children: ReactNode }) => {
    const [user, setUser] = useState<AuthenticatedUser | null>(null);
    const [isCheckingSession, setIsCheckingSession] = useState(true);

    useEffect(() => {
        const token = getStoredAuthenticationToken();
        if (!token) {
            setIsCheckingSession(false);
            return;
        }

        getCurrentUser(token)
            .then(setUser)
            .catch(clearAuthenticationToken)
            .finally(() => setIsCheckingSession(false));
    }, []);

    const signIn = useCallback(async (email: string, password: string) => {
        const token = await login(email, password);
        const currentUser = await getCurrentUser(token);
        storeAuthenticationToken(token);
        setUser(currentUser);
    }, []);

    const signOut = useCallback(async () => {
        const token = getStoredAuthenticationToken();

        try {
            if (token) await logout(token);
        } catch {
            // A local logout must still succeed if the API is temporarily unavailable.
        } finally {
            clearAuthenticationToken();
            setUser(null);
        }
    }, []);

    const updateNames = useCallback(async (firstName: string, lastName: string) => {
        const token = getStoredAuthenticationToken();
        if (!token) throw new Error('You are not signed in.');

        const updatedUser = await updateCurrentUserNames(token, firstName, lastName);
        setUser(updatedUser);
    }, []);

    const value = useMemo(
        () => ({user, isCheckingSession, signIn, signOut, updateNames}),
        [user, isCheckingSession, signIn, signOut, updateNames],
    );

    return (
        <AuthenticationContext.Provider value={value}>
            {children}
        </AuthenticationContext.Provider>
    );
};
