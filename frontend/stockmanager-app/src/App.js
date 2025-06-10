import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import MainPage from './pages/MainPage';
import LoginPage from './pages/LoginPage';
import MyPage from './pages/MyPage';
import RegisterPage from './pages/RegisterPage';
import StockDetailPage from './pages/StockDetailPage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<MainPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/mypage" element={<MyPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/stockdetail/:symbol" element={<StockDetailPage />} />
      </Routes>
    </Router>
  );
}

export default App;
