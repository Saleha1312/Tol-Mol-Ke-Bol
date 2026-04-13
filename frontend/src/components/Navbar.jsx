import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/');
    };

    return (
        <nav className="navbar">
            <div className="navbar-inner">
                <Link to="/" className="navbar-brand">
                    <img src="/favicon.png" alt="Tol Mol Ke Bol Logo" className="brand-logo" />
                </Link>
                <div className="navbar-links">
                    {user ? (
                        <>
                            <span className="navbar-greeting">Hi, {user.name}</span>
                            <button onClick={handleLogout} className="btn-nav btn-logout" id="logout-btn">
                                Logout
                            </button>
                        </>
                    ) : (
                        <>
                            <Link to="/login" className="btn-nav" id="login-link">Login</Link>
                            <Link to="/signup" className="btn-nav btn-primary" id="signup-link">Sign Up</Link>
                        </>
                    )}
                </div>
            </div>
        </nav>
    );
}
