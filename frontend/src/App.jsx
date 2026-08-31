import React, { useState } from 'react';
import { useAuth } from './context/AuthContext';
import { Header } from './components/Header';
import { AuthModal } from './components/AuthModal';
import { ImageUploader } from './components/ImageUploader';
import { AnalysisResult } from './components/AnalysisResult';
import { MatchedGallery } from './components/MatchedGallery';
import { LoadingSpinner } from './components/LoadingSpinner';
import { imageRagApi } from './api/imageRagApi.js';
import './App.css';

export default function App() {
    const { user } = useAuth();
    const [authModalOpen, setAuthModalOpen] = useState(false);

    const [selectedImage, setSelectedImage] = useState(null);
    const [previewUrl, setPreviewUrl] = useState(null);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    const handleImageSelect = (file) => {
        setSelectedImage(file);
        setPreviewUrl(URL.createObjectURL(file));
        setResult(null);
        setError(null);
    };

    const handleAnalyze = async () => {
        if (!selectedImage) return;

        // 미로그인 시 로그인 모달 팝업
        if (!user) {
            alert('RAG 분석 서비스는 로그인 후 이용 가능합니다.');
            setAuthModalOpen(true);
            return;
        }

        setLoading(true);
        setError(null);
        try {
            const data = await imageRagApi.matchImage(selectedImage);
            setResult(data);
        } catch (err) {
            if (err.response?.status === 401) {
                setError('인증이 만료되었습니다. 다시 로그인해 주세요.');
                setAuthModalOpen(true);
            } else {
                setError(err.response?.data?.detail || err.message || '분석 중 오류가 발생했습니다.');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ minHeight: '100vh', backgroundColor: '#0b1120', color: '#ffffff' }}>
            <Header onOpenAuthModal={() => setAuthModalOpen(true)} />

            <main style={{ maxWidth: '800px', margin: '0 auto', padding: '30px 20px' }}>
                <div style={{ textAlign: 'center', marginBottom: '30px' }}>
                    <p style={{ color: '#94a3b8', fontSize: '15px' }}>
                        음식 사진을 업로드하면 Gemini가 분석하여 가장 일치하는 로컬 데이터를 매칭합니다.
                    </p>
                </div>

                <ImageUploader
                    previewUrl={previewUrl}
                    onImageSelect={handleImageSelect}
                />

                <div style={{ textAlign: 'center', marginTop: '20px' }}>
                    <button
                        onClick={handleAnalyze}
                        disabled={!selectedImage || loading}
                        style={{
                            width: '100%',
                            padding: '14px',
                            backgroundColor: !selectedImage || loading ? '#334155' : '#0284c7',
                            color: '#ffffff',
                            border: 'none',
                            borderRadius: '8px',
                            fontSize: '16px',
                            fontWeight: 'bold',
                            cursor: !selectedImage || loading ? 'not-allowed' : 'pointer',
                            transition: 'background-color 0.2s'
                        }}
                    >
                        {loading ? 'AI 멀티모달 분석 중...' : '유사 음식 검색 및 RAG 분석 실행'}
                    </button>
                </div>

                {loading && <LoadingSpinner />}

                {error && (
                    <div style={{
                        marginTop: '20px',
                        padding: '16px',
                        backgroundColor: '#ef444420',
                        border: '1px solid #ef4444',
                        borderRadius: '8px',
                        color: '#f87171',
                        textAlign: 'center'
                    }}>
                        {error}
                    </div>
                )}

                {result && (
                    <div style={{ marginTop: '30px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
                        <AnalysisResult
                            category={result.predicted_category}
                            analysis={result.similarity_analysis}
                        />
                        <MatchedGallery
                            images={result.matched_images}
                        />
                    </div>
                )}
            </main>

            <AuthModal
                isOpen={authModalOpen}
                onClose={() => setAuthModalOpen(false)}
            />
        </div>
    );
}