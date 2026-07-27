export type UserRole = 'admin' | 'user';

export interface UserAddress {
    street: string;
    street_nbr: string;
    city: string;
    npa: string;
    country: string;
}

export interface AuthenticatedUser {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
    role: UserRole;
    address?: UserAddress | null;
}
