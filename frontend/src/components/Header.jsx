import React from 'react';
import { useAuth } from '../context/AuthContext';

export const Header = ({ onOpenAuthModal }) => {
    const { user, logout } = useAuth();

    return (
        <header style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '16px 24px',
            backgroundColor: '#111827',
            borderBottom: '1px solid #1f2937'
        }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span style={{ fontSize: '24px' }}>🍲</span>
                <h1 style={{ fontSize: '18px', fontWeight: 'bold', color: '#ffffff', margin: 0 }}>
                    한식 Image RAG 시스템
                </h1>
            </div>

            <div>
                {user ? (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span style={{ color: '#38bdf8', fontSize: '14px', fontWeight: '600' }}>
              👤 {user.username} 님
            </span>
                        <button
                            onClick={logout}
                            style={{
                                backgroundColor: '#ef4444',
                                color: '#ffffff',
                                border: 'none',
                                padding: '6px 12px',
                                borderRadius: '6px',
                                cursor: 'pointer',
                                fontSize: '13px',
                                fontWeight: 'bold'
                            }}
                        >
                            로그아웃
                        </button>
                    </div>
                ) : (
                    <button
                        onClick={onOpenAuthModal}
                        style={{
                            backgroundColor: '#0284c7',
                            color: '#ffffff',
                            border: 'none',
                            padding: '8px 16px',
                            borderRadius: '6px',
                            cursor: 'pointer',
                            fontSize: '14px',
                            fontWeight: 'bold'
                        }}
                    >
                        로그인 / 회원가입
                    </button>
                )}
            </div>
        </header>
    );
};