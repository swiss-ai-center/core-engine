import { useContext } from 'react';
import { AuthenticationContext } from 'utils/contexts/authentication';

export const useAuthentication = () => useContext(AuthenticationContext);
