"use client";

import { useState } from "react";
import Image from "next/image";

export default function Home() {
  const [question, setQuestion] = useState("");
  const [gptResponse, setGptResponse] = useState("");
  const [analysis, setAnalysis] = useState("");

  // 임시 GPT 응답 함수 (실제 API 연동은 추후)
  const handleAsk = () => {
    setGptResponse('세종대왕은 1392년에 조선을 세웠다.');
    setAnalysis(""); // 분석 결과 초기화
  };

  // 임시 환각 탐지 함수 (실제 로직/연동은 추후)
  const handleDetect = () => {
    setAnalysis("• 문장 1: 환각 ❌\n• 환각률: 100%");
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#f6f8fa]">
      <div className="w-full max-w-[420px] bg-white rounded-3xl shadow-xl p-7 flex flex-col gap-6">
        {/* 헤더 */}
        <div className="flex flex-col items-center gap-2 mb-2">
          <h1 className="text-xl font-semibold text-gray-800 mt-2">AI 환각 탐지</h1>
        </div>
        {/* 입력 */}
        <div>
          <label className="block mb-2 text-gray-700 font-medium text-base">질문을 입력하세요</label>
          <input
            className="w-full border border-gray-200 rounded-xl px-4 py-3 text-lg focus:outline-none focus:ring-2 focus:ring-blue-400 bg-gray-50 placeholder-gray-400 transition"
            value={question}
            onChange={e => setQuestion(e.target.value)}
            placeholder="예) 세종대왕은 언제 태어났어?"
          />
        </div>
        {/* GPT 질문 버튼 */}
        <button
          className="w-full bg-blue-500 hover:bg-blue-600 text-white py-3 text-lg rounded-xl font-semibold shadow transition disabled:bg-blue-200"
          onClick={handleAsk}
          disabled={!question.trim()}
        >
          GPT에게 질문하기
        </button>
        {/* GPT 응답 */}
        <div>
          <div className="text-gray-600 font-medium mb-1">GPT 응답</div>
          <div className="border border-gray-100 rounded-xl p-4 bg-gray-50 min-h-[48px] text-base text-gray-800">
            {gptResponse || <span className="text-gray-400">GPT의 답변이 여기에 표시됩니다.</span>}
          </div>
        </div>
        {/* 환각 탐지 버튼 */}
        <button
          className="w-full bg-[#e6f0fd] hover:bg-[#d0e6fa] text-blue-700 py-3 text-lg rounded-xl font-semibold shadow transition disabled:bg-gray-200 disabled:text-gray-400"
          onClick={handleDetect}
          disabled={!gptResponse}
        >
          [환각 탐지하기 🔍]
        </button>
        {/* 분석 결과 */}
        <div>
          <div className="text-gray-600 font-medium mb-1">분석 결과</div>
          <pre className="border border-gray-100 rounded-xl p-4 bg-gray-50 min-h-[48px] text-base text-gray-800 whitespace-pre-wrap">
            {analysis || <span className="text-gray-400">분석 결과가 여기에 표시됩니다.</span>}
          </pre>
        </div>
      </div>
    </div>
  );
}
