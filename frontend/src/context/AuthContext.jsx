import { createContext, useContext, useState, useEffect } from 'react';
import API from '../api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('token'));
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (token) {
            API.get('/api/auth/me')
                .then((res) => {
                    setUser(res.data);
                })
                .catch(() => {
                    localStorage.removeItem('token');
                    setToken(null);
                    setUser(null);
                })
                .finally(() => setLoading(false));
        } else {
            setLoading(false);
        }
    }, [token]);

    const login = async (email, password) => {
        const res = await API.post('/api/auth/login', { email, password });
        const { access_token, user: userData } = res.data;
        localStorage.setItem('token', access_token);
        setToken(access_token);
        setUser(userData);
        return userData;
    };

    const signup = async (name, email, password) => {
        const res = await API.post('/api/auth/signup', { name, email, password });
        const { access_token, user: userData } = res.data;
        localStorage.setItem('token', access_token);
        setToken(access_token);
        setUser(userData);
        return userData;
    };

    const logout = () => {
        localStorage.removeItem('token');
        setToken(null);
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, token, loading, login, signup, logout }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}
