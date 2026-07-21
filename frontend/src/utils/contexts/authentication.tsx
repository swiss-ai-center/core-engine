import { createContext } from 'react';
import { AuthenticatedUser } from 'models/AuthenticatedUser';

export interface AuthenticationContextValue {
    user: AuthenticatedUser | null;
    isCheckingSession: boolean;
    signIn: (email: string, password: string) => Promise<void>;
    signOut: () => Promise<void>;
    updateNames: (firstName: string, lastName: string) => Promise<void>;
}

export const AuthenticationContext = createContext<AuthenticationContextValue>({
    user: null,
    isCheckingSession: true,
    signIn: async () => undefined,
    signOut: async () => undefined,
    updateNames: async () => undefined,
});
