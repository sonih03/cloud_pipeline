import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';

export const AuthModal = ({ isOpen, onClose }) => {
    const [isLoginTab, setIsLoginTab] = useState(true);
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [errorMsg, setErrorMsg] = useState('');
    const [loading, setLoading] = useState(false);

    const { login, register } = useAuth();

    if (!isOpen) return null;

    const handleSubmit = async (e) => {
        e.preventDefault();
        setErrorMsg('');
        setLoading(true);

        try {
            if (isLoginTab) {
                await login(username, password);
                onClose();
            } else {
                await register(username, password);
                alert('회원가입이 완료되었습니다! 로그인해 주세요.');
                setIsLoginTab(true);
            }
        } catch (err) {
            setErrorMsg(err.response?.data?.detail || '오류가 발생했습니다.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{
            position: 'fixed',
            top: 0, left: 0, right: 0, bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.75)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000
        }}>
            <div style={{
                backgroundColor: '#1e293b',
                padding: '30px',
                borderRadius: '12px',
                width: '360px',
                border: '1px solid #334155',
                boxShadow: '0 10px 25px rgba(0,0,0,0.5)'
            }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
                    <div style={{ display: 'flex', gap: '10px' }}>
                        <button
                            onClick={() => { setIsLoginTab(true); setErrorMsg(''); }}
                            style={{
                                background: 'none',
                                border: 'none',
                                color: isLoginTab ? '#38bdf8' : '#94a3b8',
                                fontSize: '16px',
                                fontWeight: 'bold',
                                cursor: 'pointer',
                                borderBottom: isLoginTab ? '2px solid #38bdf8' : 'none',
                                paddingBottom: '4px'
                            }}
                        >
                            로그인
                        </button>
                        <button
                            onClick={() => { setIsLoginTab(false); setErrorMsg(''); }}
                            style={{
                                background: 'none',
                                border: 'none',
                                color: !isLoginTab ? '#38bdf8' : '#94a3b8',
                                fontSize: '16px',
                                fontWeight: 'bold',
                                cursor: 'pointer',
                                borderBottom: !isLoginTab ? '2px solid #38bdf8' : 'none',
                                paddingBottom: '4px'
                            }}
                        >
                            회원가입
                        </button>
                    </div>
                    <button
                        onClick={onClose}
                        style={{ background: 'none', border: 'none', color: '#94a3b8', fontSize: '18px', cursor: 'pointer' }}
                    >
                        ✕
                    </button>
                </div>

                {errorMsg && (
                    <div style={{
                        backgroundColor: '#ef444420',
                        color: '#f87171',
                        padding: '10px',
                        borderRadius: '6px',
                        marginBottom: '15px',
                        fontSize: '13px'
                    }}>
                        {errorMsg}
                    </div>
                )}

                <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
                    <div>
                        <label style={{ display: 'block', color: '#cbd5e1', fontSize: '13px', marginBottom: '6px' }}>아이디</label>
                        <input
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                            style={{
                                width: '100%',
                                padding: '10px',
                                borderRadius: '6px',
                                backgroundColor: '#0f172a',
                                border: '1px solid #334155',
                                color: '#ffffff',
                                boxSizing: 'border-box'
                            }}
                        />
                    </div>

                    <div>
                        <label style={{ display: 'block', color: '#cbd5e1', fontSize: '13px', marginBottom: '6px' }}>비밀번호</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            style={{
                                width: '100%',
                                padding: '10px',
                                borderRadius: '6px',
                                backgroundColor: '#0f172a',
                                border: '1px solid #334155',
                                color: '#ffffff',
                                boxSizing: 'border-box'
                            }}
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        style={{
                            marginTop: '10px',
                            padding: '12px',
                            borderRadius: '6px',
                            backgroundColor: '#0284c7',
                            color: '#ffffff',
                            border: 'none',
                            fontWeight: 'bold',
                            cursor: loading ? 'not-allowed' : 'pointer'
                        }}
                    >
                        {loading ? '처리 중...' : isLoginTab ? '로그인' : '회원가입 완료'}
                    </button>
                </form>
            </div>
        </div>
    );
};