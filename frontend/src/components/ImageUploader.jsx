import React, { useRef } from 'react';
import styled from 'styled-components';
import { UploadCloud, Image as ImageIcon } from 'lucide-react';

const UploadArea = styled.div`
  border: 2px dashed ${props => props.$isDragOver ? '#38bdf8' : '#334155'};
  background-color: ${props => props.$isDragOver ? '#1e293b' : '#1e293b80'};
  border-radius: 12px;
  padding: 32px;
  text-align: center;
  transition: all 0.2s ease;
  cursor: pointer;

  &:hover {
    border-color: #38bdf8;
    background-color: #1e293b;
  }
`;

const PreviewContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
`;

const ImagePreview = styled.img`
  max-width: 100%;
  max-height: 280px;
  border-radius: 8px;
  object-fit: cover;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
`;

const SubmitButton = styled.button`
  margin-top: 16px;
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #0ea5e9, #38bdf8);
  color: #0f172a;
  font-weight: 700;
  font-size: 16px;
  border-radius: 8px;
  transition: opacity 0.2s;

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  &:hover:not(:disabled) {
    opacity: 0.9;
  }
`;

export const ImageUploader = ({ selectedFile, previewUrl, onSelectFile, onSubmit, isLoading }) => {
    const fileInputRef = useRef(null);

    const handleDrop = (e) => {
        e.preventDefault();
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            onSelectFile(e.dataTransfer.files[0]);
        }
    };

    return (
        <div>
            <UploadArea
                onClick={() => fileInputRef.current?.click()}
                onDragOver={(e) => e.preventDefault()}
                onDrop={handleDrop}
            >
                <input
                    type="file"
                    ref={fileInputRef}
                    style={{ display: 'none' }}
                    accept="image/jpeg,image/png,image/webp"
                    onChange={(e) => e.target.files?.[0] && onSelectFile(e.target.files[0])}
                />

                {previewUrl ? (
                    <PreviewContainer>
                        <ImagePreview src={previewUrl} alt="업로드 이미지 미리보기" />
                        <p style={{ color: '#94a3b8', fontSize: '13px' }}>클릭하거나 다른 이미지를 드롭하여 변경</p>
                    </PreviewContainer>
                ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
                        <UploadCloud size={44} color="#38bdf8" />
                        <div>
                            <p style={{ fontSize: '16px', fontWeight: '600', color: '#f1f5f9' }}>음식 사진을 드래그하거나 클릭하여 업로드</p>
                            <p style={{ fontSize: '13px', color: '#64748b', marginTop: '4px' }}>JPG, PNG, WEBP 포맷 지원</p>
                        </div>
                    </div>
                )}
            </UploadArea>

            <SubmitButton onClick={onSubmit} disabled={!selectedFile || isLoading}>
                {isLoading ? '분석 중...' : '유사 음식 검색 및 RAG 분석 실행'}
            </SubmitButton>
        </div>
    );
};