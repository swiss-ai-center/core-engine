import { AuthenticatedUser, UserRole } from 'models/AuthenticatedUser';

const TOKEN_STORAGE_KEY = 'authenticationToken';

const engineUrl = process.env.REACT_APP_ENGINE_URL ?? '';

const authHeaders = (token: string): HeadersInit => ({
    Authorization: `Bearer ${token}`,
});

export const getStoredAuthenticationToken = () => sessionStorage.getItem(TOKEN_STORAGE_KEY);

export const storeAuthenticationToken = (token: string) => {
    sessionStorage.setItem(TOKEN_STORAGE_KEY, token);
};

export const clearAuthenticationToken = () => {
    sessionStorage.removeItem(TOKEN_STORAGE_KEY);
};

export const login = async (email: string, password: string): Promise<string> => {
    const formData = new URLSearchParams();
    formData.set('username', email);
    formData.set('password', password);

    const response = await fetch(`${engineUrl}/auth/jwt/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData,
    });

    if (!response.ok) {
        throw new Error(response.status === 400 ? 'Incorrect email or password.' : 'Unable to sign in. Please try again.');
    }

    const data: { access_token: string } = await response.json();
    return data.access_token;
};

export const getCurrentUser = async (token: string): Promise<AuthenticatedUser> => {
    const response = await fetch(`${engineUrl}/me`, {
        headers: authHeaders(token),
    });

    if (!response.ok) {
        throw new Error('Your session is no longer valid.');
    }

    return response.json();
};

export const updateCurrentUserNames = async (
    token: string,
    firstName: string,
    lastName: string,
): Promise<AuthenticatedUser> => {
    const response = await fetch(`${engineUrl}/me`, {
        method: 'PATCH',
        headers: {
            ...authHeaders(token),
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({first_name: firstName, last_name: lastName}),
    });

    if (!response.ok) {
        throw new Error(response.status === 422 ? 'First and last name are required.' : 'Unable to update your profile.');
    }

    return response.json();
};

export const getUsers = async (token: string): Promise<AuthenticatedUser[]> => {
    const response = await fetch(`${engineUrl}/admin/users`, {
        headers: authHeaders(token),
    });

    if (!response.ok) {
        throw new Error('Unable to load users.');
    }

    return response.json();
};

export const updateUserRole = async (
    token: string,
    userId: string,
    role: UserRole,
): Promise<AuthenticatedUser> => {
    const response = await fetch(`${engineUrl}/admin/users/${userId}/role`, {
        method: 'PATCH',
        headers: {
            ...authHeaders(token),
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({role}),
    });

    if (!response.ok) {
        throw new Error('Unable to update this user\'s role.');
    }

    return response.json();
};

export const logout = async (token: string): Promise<void> => {
    await fetch(`${engineUrl}/auth/jwt/logout`, {
        method: 'POST',
        headers: authHeaders(token),
    });
};
