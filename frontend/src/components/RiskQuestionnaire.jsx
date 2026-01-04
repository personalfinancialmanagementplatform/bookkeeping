/**
 * 風險評估問卷組件
 * 檔案位置: frontend/src/components/RiskQuestionnaire.jsx
 */

import React, { useState } from 'react';
import { useRiskQuestionnaire } from '../hooks/useStockData';
import './RiskQuestionnaire.css';

const RiskQuestionnaire = ({ onComplete, onSkip }) => {
  const {
    questions,
    answers,
    setAnswer,
    calculateResult,
    result,
    loading,
    isComplete,
    reset
  } = useRiskQuestionnaire();
  
  const [currentStep, setCurrentStep] = useState(0); // 0: 問卷, 1: 結果

  const handleOptionClick = (questionId, value) => {
    setAnswer(questionId, value);
  };

  const handleSubmit = async () => {
    const res = await calculateResult();
    if (res) {
      setCurrentStep(1);
    }
  };

  const handleUseResult = () => {
    if (result && onComplete) {
      onComplete(result.risk_level);
    }
  };

  const handleRetry = () => {
    reset();
    setCurrentStep(0);
  };

  const handleSkip = () => {
    if (onSkip) {
      onSkip();
    }
  };

  const answeredCount = Object.keys(answers).length;
  const progress = (answeredCount / 5) * 100;

  return (
    <div className="risk-questionnaire">
      {currentStep === 0 ? (
        <>
          <div className="questionnaire-header">
            <h2>📋 風險承受度評估</h2>
            <p className="subtitle">
              回答以下 5 個問題，幫助我們了解您的投資風格
            </p>
            
            <div className="progress-container">
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: `${progress}%` }}
                />
              </div>
              <span className="progress-text">{answeredCount}/5</span>
            </div>
          </div>

          <div className="questions-container">
            {questions.map((q, index) => (
              <div 
                key={q.id} 
                className={`question-card ${answers[q.id] ? 'answered' : ''}`}
              >
                <div className="question-number">Q{index + 1}</div>
                <div className="question-text">{q.question}</div>
                
                <div className="options">
                  {q.options.map((option) => (
                    <button
                      key={option.value}
                      className={`option-btn ${answers[q.id] === option.value ? 'selected' : ''}`}
                      onClick={() => handleOptionClick(q.id, option.value)}
                    >
                      <span className="option-indicator">
                        {answers[q.id] === option.value ? '●' : '○'}
                      </span>
                      <span className="option-text">{option.text}</span>
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <div className="questionnaire-actions">
            <button 
              className="btn btn-secondary"
              onClick={handleSkip}
            >
              跳過，直接選擇風險等級
            </button>
            
            <button 
              className="btn btn-primary"
              onClick={handleSubmit}
              disabled={!isComplete || loading}
            >
              {loading ? '計算中...' : '查看評估結果'}
            </button>
          </div>
        </>
      ) : (
        <div className="result-container">
          <div className="result-header">
            <h2>📊 評估結果</h2>
          </div>
          
          {result && (
            <>
              <div className={`result-card risk-${result.risk_level}`}>
                <div className="result-score">
                  <span className="score-value">{result.score}</span>
                  <span className="score-max">/ {result.max_score}</span>
                </div>
                
                <div className="result-level">
                  <span className="level-label">您的風險屬性</span>
                  <span className="level-value">{result.risk_level_name}</span>
                </div>
                
                <div className="result-description">
                  {result.description}
                </div>
              </div>
              
              <div className="risk-scale">
                <div className="scale-bar">
                  <div className="scale-section conservative">
                    <span>保守型</span>
                    <span className="score-range">5-8分</span>
                  </div>
                  <div className="scale-section moderate">
                    <span>穩健型</span>
                    <span className="score-range">9-14分</span>
                  </div>
                  <div className="scale-section aggressive">
                    <span>積極型</span>
                    <span className="score-range">15-20分</span>
                  </div>
                </div>
                <div 
                  className="scale-marker"
                  style={{ left: `${(result.score / result.max_score) * 100}%` }}
                >
                  <span className="marker-dot">▼</span>
                </div>
              </div>
              
              <div className="result-actions">
                <button 
                  className="btn btn-secondary"
                  onClick={handleRetry}
                >
                  重新測驗
                </button>
                
                <button 
                  className="btn btn-primary"
                  onClick={handleUseResult}
                >
                  使用「{result.risk_level_name}」進行配置
                </button>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default RiskQuestionnaire;