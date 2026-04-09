import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Login from './pages/Login';
import Signup from './pages/Signup';

function App() {
    return (
        <Router>
            <AuthProvider>
                <div className="app">
                    <Navbar />
                    <Routes>
                        <Route path="/" element={<Home />} />
                        <Route path="/login" element={<Login />} />
                        <Route path="/signup" element={<Signup />} />
                    </Routes>
                    <footer className="footer">
                        <p>&copy; 2026 Tol Mol Ke Bol. All rights reserved.</p>
                        <p className="disclaimer">We may earn a commission if you purchase through our links.</p>
                    </footer>
                </div>
            </AuthProvider>
        </Router>
    );
}

export default App;
