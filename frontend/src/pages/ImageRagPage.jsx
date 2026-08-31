import React, { useState } from 'react';
import styled from 'styled-components';
import { useImageMatchQuery } from '../query/useImageMatchQuery';
import { ImageUploader } from '../components/ImageUploader';
import { AnalysisResult } from '../components/AnalysisResult';
import { MatchedGallery } from '../components/MatchedGallery';
import { LoadingSpinner } from '../components/LoadingSpinner';

const PageWrapper = styled.div`
  max-width: 800px;
  margin: 0 auto;
  padding: 40px 20px;
  display: flex;
  flex-direction: column;
  gap: 28px;
`;

const Header = styled.header`
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const MainTitle = styled.h1`
  font-size: 28px;
  font-weight: 800;
  background: linear-gradient(135deg, #f8fafc, #94a3b8);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
`;

const SubTitle = styled.p`
  color: #64748b;
  font-size: 15px;
`;

const ErrorBox = styled.div`
  padding: 16px;
  background-color: #ef444420;
  border: 1px solid #ef4444;
  border-radius: 8px;
  color: #fca5a5;
  font-size: 14px;
`;

export const ImageRagPage = () => {
    const [selectedFile, setSelectedFile] = useState(null);
    const [previewUrl, setPreviewUrl] = useState(null);

    const { mutate, data, isPending, isError, error } = useImageMatchQuery();

    const handleSelectFile = (file) => {
        setSelectedFile(file);
        setPreviewUrl(URL.createObjectURL(file));
    };

    const handleSubmit = () => {
        if (!selectedFile) return;
        mutate({ file: selectedFile, topKSamples: 3 });
    };

    return (
        <PageWrapper>
            <Header>
                <MainTitle>한식 Image RAG 검색 시스템</MainTitle>
                <SubTitle>음식 사진을 업로드하면 Gemini가 분석하여 가장 일치하는 로컬 데이터를 매칭합니다.</SubTitle>
            </Header>

            <ImageUploader
                selectedFile={selectedFile}
                previewUrl={previewUrl}
                onSelectFile={handleSelectFile}
                onSubmit={handleSubmit}
                isLoading={isPending}
            />

            {isPending && <LoadingSpinner />}

            {isError && (
                <ErrorBox>
                    분석 중 오류가 발생했습니다: {error?.response?.data?.detail || error.message}
                </ErrorBox>
            )}

            {data && !isPending && (
                <>
                    <AnalysisResult
                        predictedCategory={data.predicted_category}
                        similarityAnalysis={data.similarity_analysis}
                    />
                    <MatchedGallery matchedImages={data.matched_images} />
                </>
            )}
        </PageWrapper>
    );
};