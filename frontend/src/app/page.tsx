"use client";

import { useState } from "react";
import Image from "next/image";
import LoginButton from "@/components/LoginButton";
import { useAuthContext } from "@/contexts/AuthContext";

export default function Home() {
  const { user, loading } = useAuthContext();
  const [question, setQuestion] = useState("");
  const [gptResponse, setGptResponse] = useState("");
  const [analysis, setAnalysis] = useState("");
  const [sentences, setSentences] = useState<string[]>([]);
  const [hallucinationResults, setHallucinationResults] = useState<any[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showSVO, setShowSVO] = useState(false);
  const [svoResults, setSvoResults] = useState<any[]>([]);
  const [isSVOAnalyzing, setIsSVOAnalyzing] = useState(false);
  const [svoMethod, setSvoMethod] = useState<'gpt' | 'konlpy'>('gpt');

  // GPT API 호출 함수
  const handleAsk = async () => {
    try {
      setGptResponse("응답을 생성하고 있습니다...");
      setAnalysis(""); // 분석 결과 초기화
      
      // 인증 토큰 가져오기
      const idToken = user ? await user.getIdToken() : null;
      
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };
      
      if (idToken) {
        headers['Authorization'] = `Bearer ${idToken}`;
      }
      
      const response = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        headers,
        body: JSON.stringify({ prompt: question }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setGptResponse(data.response);
      
      // GPT 응답을 받으면 문장으로 분리
      const sentenceList = splitIntoSentences(data.response);
      setSentences(sentenceList);
    } catch (error) {
      console.error('Error:', error);
      const errorMessage = error instanceof Error ? error.message : '알 수 없는 오류가 발생했습니다';
      setGptResponse(`오류가 발생했습니다: ${errorMessage}`);
    }
  };

  // 문장 분리 함수
  const splitIntoSentences = (text: string) => {
    return text.split(/[.!?]+/).filter(sentence => sentence.trim().length > 0);
  };

  // SVO 분석 함수 (실제 ai-engine 연결)
  const handleSVOAnalysis = async () => {
    console.log('SVO 분석 시작, 문장들:', sentences);
    
    if (sentences.length === 0) {
      console.log('분석할 문장이 없습니다.');
      return;
    }
    
    setIsSVOAnalyzing(true);
    
    try {
      const svoPromises = sentences.map(async (sentence) => {
        console.log('분석할 문장:', sentence);
        
        if (!sentence.trim()) {
          console.log('빈 문장 건너뛰기');
          return null;
        }
        
        const response = await fetch('http://localhost:8000/svo', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ 
            text: sentence.trim(),
            language: 'auto',
            method: svoMethod  // 선택된 분석 방법 사용
          }),
        });
        
        console.log('API 응답 상태:', response.status);
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('SVO 분석 결과:', result);
        
        // SVO 결과를 데이터베이스에 저장
        try {
          const saveResponse = await fetch('http://localhost:8000/save_svo', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              text: sentence.trim(),
              language: result.language || 'auto',
              result: JSON.stringify(result)
            }),
          });
          console.log('SVO 저장 결과:', await saveResponse.json());
        } catch (saveError) {
          console.error('SVO 저장 오류:', saveError);
        }
        
        return result;
      });
      
      const results = await Promise.all(svoPromises);
      const validResults = results.filter(result => result !== null);
      console.log('전체 SVO 결과:', validResults);
      setSvoResults(validResults);
    } catch (error) {
      console.error('SVO 분석 오류:', error);
      // 오류 시 기본값으로 폴백
      const fallbackResults = sentences.map((sentence) => {
        const isKorean = /[가-힣]/.test(sentence);
        return {
          sentence: sentence.trim(),
          language: isKorean ? 'ko' : 'en',
          svo: {
            subject: isKorean ? '주어' : 'Subject',
            verb: isKorean ? '동사' : 'Verb',
            object: isKorean ? '목적어' : 'Object'
          }
        };
      });
      setSvoResults(fallbackResults);
    } finally {
      setIsSVOAnalyzing(false);
    }
  };

  // 환각 탐지 함수 (테스트 케이스)
  const handleDetect = () => {
    setIsAnalyzing(true);
    
    // GPT 응답을 문장으로 분리
    const sentenceList = splitIntoSentences(gptResponse);
    setSentences(sentenceList);
    
    // 테스트 케이스: 환각 결과 생성
    setTimeout(() => {
      const results = sentenceList.map((sentence, index) => {
        // 테스트용 환각 판정 (실제로는 AI 엔진에서 분석)
        const isHallucination = sentence.includes('1392') || sentence.includes('조선을 세웠다');
        return {
          sentence: sentence.trim(),
          isHallucination,
          reason: isHallucination ? '(1392년 → 실제로는 1397년)' : '사실 확인됨'
        };
      });
      
      setHallucinationResults(results);
      setIsAnalyzing(false);
      
      // 전체 환각률 계산
      const hallucinationRate = Math.round((results.filter(r => r.isHallucination).length / results.length) * 100);
      setAnalysis(`환각률: ${hallucinationRate}%`);
    }, 2000);
  };

  const renderMainContent = () => {
    if (loading) {
      return (
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      );
    }

    if (!user) {
      return (
        <div className="text-center py-8">
          <div className="text-gray-600 mb-4">
            서비스를 이용하려면 로그인이 필요합니다.
          </div>
          <div className="text-sm text-gray-500">
            위의 Google 로그인 버튼을 클릭하여 로그인해주세요.
          </div>
        </div>
      );
    }

    return (
      <>
        {/* 입력 */}
        <div>
          <label className="block mb-2 text-black font-medium text-base">질문을 입력하세요</label>
          <input
            className="w-full border border-black rounded-xl px-4 py-3 text-lg focus:outline-none focus:ring-2 focus:ring-blue-400 bg-gray-50 placeholder-black text-black transition"
            value={question}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setQuestion(e.target.value)}
            placeholder="예) 세종대왕은 언제 태어났어?"
          />
        </div>
        {/* GPT 질문 버튼 */}
        <button
          className="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white py-3 text-lg rounded-xl font-semibold shadow transition disabled:bg-gray-300 disabled:text-gray-500"
          onClick={handleAsk}
          disabled={!question.trim()}
        >
          GPT에게 질문하기
        </button>
        
        {/* GPT 응답 - 문장별로 표시 */}
        {gptResponse && (
          <div>
            <div className="text-black font-medium mb-3 flex items-center gap-2">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              GPT 응답
            </div>
            <div className="space-y-3">
              {sentences.length > 0 ? (
                sentences.map((sentence, index) => (
                  <div key={index} className="bg-gray-50 border border-gray-100 rounded-xl p-4">
                    <div className="text-sm text-gray-500 mb-1">문장 {index + 1}</div>
                    <div className="text-gray-800">{sentence.trim()}</div>
                  </div>
                ))
              ) : (
                <div className="bg-gray-50 border border-gray-100 rounded-xl p-4 text-gray-800">
                  {gptResponse}
                </div>
              )}
            </div>
            
            {/* SVO 분석 방법 선택 */}
            <div className="mt-4 space-y-3">
              <div className="flex gap-2">
                <label className="flex items-center gap-2 text-sm">
                  <input
                    type="radio"
                    name="svoMethod"
                    value="gpt"
                    checked={svoMethod === 'gpt'}
                    onChange={(e) => setSvoMethod(e.target.value as 'gpt' | 'konlpy')}
                    className="text-purple-500"
                  />
                  <span className="text-gray-700">🤖 GPT 분석</span>
                </label>
                <label className="flex items-center gap-2 text-sm">
                  <input
                    type="radio"
                    name="svoMethod"
                    value="konlpy"
                    checked={svoMethod === 'konlpy'}
                    onChange={(e) => setSvoMethod(e.target.value as 'gpt' | 'konlpy')}
                    className="text-purple-500"
                  />
                  <span className="text-gray-700">📊 KoNLPy 분석</span>
                </label>
              </div>
              
              {/* SVO 분석 토글 버튼 */}
              <button
                onClick={() => {
                  if (!showSVO && sentences.length > 0) {
                    handleSVOAnalysis();
                  }
                  setShowSVO(!showSVO);
                }}
                className="w-full bg-purple-500 hover:bg-purple-600 text-white py-2 text-sm rounded-lg font-medium transition flex items-center justify-center gap-2"
              >
                {isSVOAnalyzing ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    SVO 분석 중...
                  </>
                ) : (
                  <>
                    🔍 {showSVO ? 'SVO 분석 숨기기' : 'SVO 분석 보기'}
                  </>
                )}
              </button>
            </div>
            
            {/* SVO 분석 결과 */}
            {showSVO && svoResults.length > 0 && (
              <div className="mt-4">
                <div className="text-black font-medium mb-3 flex items-center gap-2">
                  <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                  SVO 분석 결과
                </div>
                <div className="space-y-3">
                  {svoResults.map((result, index) => (
                    <div key={index} className="bg-purple-50 border border-purple-200 rounded-xl p-4">
                      <div className="text-sm text-purple-600 mb-2 font-medium">
                        문장 {index + 1} ({result.language === 'ko' ? '🇰🇷 한국어' : '🇺🇸 영어'})
                      </div>
                      <div className="text-gray-800 mb-3">{result.sentence}</div>
                      <div className="grid grid-cols-3 gap-2 text-sm">
                        <div className="bg-red-100 border border-red-200 rounded p-2">
                          <div className="text-red-700 font-medium">주어 (S)</div>
                          <div className="text-red-600">{result.svo.subject}</div>
                        </div>
                        <div className="bg-green-100 border border-green-200 rounded p-2">
                          <div className="text-green-700 font-medium">동사 (V)</div>
                          <div className="text-green-600">{result.svo.verb}</div>
                        </div>
                        <div className="bg-blue-100 border border-blue-200 rounded p-2">
                          <div className="text-blue-700 font-medium">목적어 (O)</div>
                          <div className="text-blue-600">{result.svo.object}</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
        
        {/* 환각 탐지 버튼 */}
        <button
          className="w-full bg-green-500 hover:bg-green-600 text-white py-3 text-lg rounded-xl font-semibold shadow transition disabled:bg-gray-300 disabled:text-gray-500 flex items-center justify-center gap-2"
          onClick={handleDetect}
          disabled={!gptResponse || isAnalyzing}
        >
          {isAnalyzing ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              분석 중...
            </>
          ) : (
            <>
              🔍 환각 탐지하기
            </>
          )}
        </button>
        
        {/* 분석 결과 - 문장별 환각 판정 */}
        {hallucinationResults.length > 0 && (
          <div>
            <div className="text-black font-medium mb-3 flex items-center gap-2">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              분석 결과
            </div>
            <div className="space-y-3">
              {hallucinationResults.map((result, index) => (
                <div 
                  key={index} 
                  className={`border rounded-xl p-4 ${
                    result.isHallucination 
                      ? 'bg-red-50 border-red-200' 
                      : 'bg-green-50 border-green-200'
                  }`}
                >
                  <div className="flex items-center gap-2 mb-2">
                    {result.isHallucination ? (
                      <>
                        <span className="text-red-500 text-xl">❌</span>
                        <span className="text-red-700 font-medium">문장 {index + 1}: 환각</span>
                        <span className="text-red-500 text-xl">❌</span>
                      </>
                    ) : (
                      <>
                        <span className="text-green-500 text-xl">✓</span>
                        <span className="text-green-700 font-medium">문장 {index + 1}: 사실</span>
                        <span className="text-green-500 text-xl">✓</span>
                      </>
                    )}
                  </div>
                  <div className="text-sm text-gray-600">{result.reason}</div>
                </div>
              ))}
              
              {/* 전체 환각률 */}
              <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-5 h-5 bg-blue-500 rounded flex items-center justify-center">
                    <div className="w-3 h-3 bg-white rounded"></div>
                  </div>
                  <span className="text-blue-700 font-medium">환각률: {analysis}</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </>
    );
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-purple-50">
      <div className="w-full max-w-[480px] bg-white rounded-3xl shadow-xl p-8 flex flex-col gap-6">
        {/* 헤더 */}
        <div className="flex flex-col items-center gap-3 mb-4">
          <div className="w-16 h-16 flex items-center justify-center">
            <Image 
              src="/ai-logo.jpg" 
              alt="AI Logo" 
              width={64} 
              height={64}
              className="w-16 h-16"
            />
          </div>
          <h1 className="text-2xl font-bold text-gray-800">AI 환각 탐지기</h1>
          <p className="text-gray-600 text-center text-sm">
            GPT 응답의 사실 여부를 분석해드립니다
          </p>
          <div className="mt-2">
            <LoginButton />
          </div>
        </div>
        {renderMainContent()}
      </div>
    </div>
  );
}
