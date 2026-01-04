/**
 * 風險評估問卷組件（金管會標準版）
 * 12 題完整問卷 - 單頁顯示
 */

import React, { useState, useEffect } from 'react';
import './RiskQuestionnaire.css';

const API_BASE = 'http://localhost:5005/api';

const RiskQuestionnaire = ({ onComplete, onSkip }) => {
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(true);
  const [calculating, setCalculating] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadQuestions();
  }, []);

  const loadQuestions = async () => {
    try {
      const res = await fetch(`${API_BASE}/risk-assessment/questions`);
      const data = await res.json();
      const questionsArray = Array.isArray(data) ? data : (data.questions || []);
      setQuestions(questionsArray);
      setLoading(false);
    } catch (err) {
      console.error('載入問卷失敗:', err);
      setError('載入問卷失敗');
      setLoading(false);
    }
  };

  const handleSingleAnswer = (questionId, value) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: value
    }));
  };

  const handleMultipleAnswer = (questionId, value) => {
    setAnswers(prev => {
      const current = prev[questionId] || [];
      
      if (value === 1) {
        return { ...prev, [questionId]: [1] };
      }
      
      let newValues = current.filter(v => v !== 1);
      
      if (newValues.includes(value)) {
        newValues = newValues.filter(v => v !== value);
      } else {
        newValues = [...newValues, value];
      }
      
      return { ...prev, [questionId]: newValues };
    });
  };

  const calculateResult = async () => {
    setCalculating(true);
    try {
      const res = await fetch(`${API_BASE}/risk-assessment/calculate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ answers })
      });
      const data = await res.json();
      setResult(data);
    } catch (err) {
      setError('計算失敗，請重試');
    }
    setCalculating(false);
  };

  const handleComplete = () => {
    if (onComplete && result) {
      onComplete(result.risk_level);
    }
  };

  const answeredCount = Object.keys(answers).filter(k => {
    const ans = answers[k];
    return ans !== undefined && ans !== null && 
           (Array.isArray(ans) ? ans.length > 0 : true);
  }).length;

  const allAnswered = answeredCount === questions.length && questions.length > 0;

  if (loading) {
    return <div className="questionnaire-loading">載入問卷中...</div>;
  }

  if (error) {
    return <div className="questionnaire-error">{error}</div>;
  }

  // 顯示結果
  if (result) {
    return (
      <div className="questionnaire-result">
        <div className="result-header">
          <h2>📊 風險屬性評估結果</h2>
        </div>
        
        <div className="result-card">
          <div className="result-score">
            <span className="score-label">總分</span>
            <span className="score-value">{result.total_score}</span>
            <span className="score-max">/ {result.max_score}</span>
          </div>
          
          <div className={`result-level ${result.risk_level}`}>
            <span className="level-icon">
              {result.risk_level === 'conservative' && '🛡️'}
              {result.risk_level === 'moderate' && '⚖️'}
              {result.risk_level === 'aggressive' && '🚀'}
            </span>
            <span className="level-name">{result.risk_level_name}</span>
          </div>
          
          <p className="result-description">{result.description}</p>
          
          <div className="result-suitable">
            <h4>合適投資標的之風險報酬等級</h4>
            <div className="rr-badges">
              {result.suitable_rr && result.suitable_rr.map(rr => (
                <span key={rr} className={`rr-badge ${rr.toLowerCase()}`}>{rr}</span>
              ))}
            </div>
            <p className="rr-desc">{result.suitable_rr_desc}</p>
          </div>
        </div>

        <div className="result-actions">
          <button className="btn btn-secondary" onClick={() => setResult(null)}>
            重新評估
          </button>
          <button className="btn btn-primary" onClick={handleComplete}>
            使用此結果
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="risk-questionnaire">
      <div className="questionnaire-header">
        <h2>📋 金管會投資風險屬性評估問卷</h2>
        <p className="subtitle">
          依據金管會規定，請依您的實際情況回答下列 {questions.length} 個問題
        </p>
        
        <div className="progress-bar">
          <div 
            className="progress-fill" 
            style={{ width: `${(answeredCount / questions.length) * 100}%` }}
          />
        </div>
        <div className="progress-text">
          已完成 {answeredCount} / {questions.length} 題
        </div>
      </div>

      <div className="questions-container">
        {questions.map((q, index) => (
          <div 
            key={q.id} 
            className={`question-card ${answers[q.id] !== undefined && (Array.isArray(answers[q.id]) ? answers[q.id].length > 0 : true) ? 'answered' : ''}`}
          >
            <div className="question-number">
              第 {index + 1} 題
              {q.type === 'multiple' && <span className="question-type">（可複選）</span>}
            </div>
            
            <div className="question-text">{q.question}</div>
            
            {q.hint && <div className="question-hint">💡 {q.hint}</div>}
            
            <div className={`options-list ${q.type === 'multiple' ? 'multiple' : 'single'}`}>
              {q.options.map(opt => {
                const isSelected = q.type === 'multiple'
                  ? (answers[q.id] || []).includes(opt.value)
                  : answers[q.id] === opt.value;
                
                return (
                  <button
                    key={opt.value}
                    className={`option-btn ${isSelected ? 'selected' : ''}`}
                    onClick={() => 
                      q.type === 'multiple'
                        ? handleMultipleAnswer(q.id, opt.value)
                        : handleSingleAnswer(q.id, opt.value)
                    }
                  >
                    <span className="option-indicator">
                      {q.type === 'multiple' 
                        ? (isSelected ? '☑' : '☐')
                        : (isSelected ? '●' : '○')
                      }
                    </span>
                    <span className="option-label">{opt.label}</span>
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      <div className="questionnaire-footer">
        <button 
          className="btn btn-primary btn-large"
          onClick={calculateResult}
          disabled={!allAnswered || calculating}
        >
          {calculating ? '計算中...' : `🎯 查看結果 (${answeredCount}/${questions.length})`}
        </button>
        
        {!allAnswered && (
          <p className="hint-text">請完成所有題目後才能查看結果</p>
        )}

        {onSkip && (
          <button className="btn-text" onClick={onSkip}>
            跳過問卷，直接選擇風險偏好
          </button>
        )}
      </div>
    </div>
  );
};

export default RiskQuestionnaire;