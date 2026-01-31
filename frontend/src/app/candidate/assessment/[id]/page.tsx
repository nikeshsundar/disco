"use client";
import { useEffect, useState, useRef, useCallback } from "react";
import { useRouter, useParams } from "next/navigation";
import axios from "axios";
import toast from "react-hot-toast";
import dynamic from "next/dynamic";
import Webcam from "react-webcam";
import {
  Clock, ChevronLeft, ChevronRight, Send, Code, FileText,
  CheckCircle, AlertTriangle, Eye, Play, Camera
} from "lucide-react";

const API_BASE = "http://localhost:8000/api";

// Dynamic import for Monaco Editor (SSR disabled)
const MonacoEditor = dynamic(() => import("@monaco-editor/react"), { ssr: false });

interface Question {
  id: number;
  question_type: string;
  category: string;
  difficulty: string;
  question_text: string;
  options?: string[];
  max_score: number;
  time_limit_seconds: number;
  skill_tags?: string[];
  is_answered: boolean;
}

// Demo questions for testing
const demoQuestions: Question[] = [
  {
    id: 1,
    question_type: "mcq",
    category: "technical",
    difficulty: "medium",
    question_text: "What is the time complexity of binary search?",
    options: ["O(1)", "O(n)", "O(log n)", "O(n²)"],
    max_score: 10,
    time_limit_seconds: 60,
    skill_tags: ["algorithms", "data-structures"],
    is_answered: false
  },
  {
    id: 2,
    question_type: "coding",
    category: "technical",
    difficulty: "medium",
    question_text: "Write a Python function to reverse a string without using built-in reverse methods.",
    max_score: 20,
    time_limit_seconds: 300,
    skill_tags: ["python", "algorithms"],
    is_answered: false
  },
  {
    id: 3,
    question_type: "text",
    category: "soft_skills",
    difficulty: "easy",
    question_text: "Describe a situation where you had to work under pressure. How did you handle it?",
    max_score: 15,
    time_limit_seconds: 180,
    skill_tags: ["communication", "problem-solving"],
    is_answered: false
  },
  {
    id: 4,
    question_type: "slider",
    category: "psychometric",
    difficulty: "easy",
    question_text: "On a scale of 1-10, how comfortable are you working in a team environment?",
    max_score: 5,
    time_limit_seconds: 30,
    skill_tags: ["teamwork"],
    is_answered: false
  },
  {
    id: 5,
    question_type: "mcq",
    category: "technical",
    difficulty: "hard",
    question_text: "Which design pattern is used when you want to decouple an abstraction from its implementation?",
    options: ["Factory Pattern", "Bridge Pattern", "Singleton Pattern", "Observer Pattern"],
    max_score: 10,
    time_limit_seconds: 60,
    skill_tags: ["design-patterns"],
    is_answered: false
  }
];

export default function AssessmentPage() {
  const params = useParams();
  const router = useRouter();
  const assessmentId = Number(params.id);

  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [answers, setAnswers] = useState<Record<number, any>>({});
  const [timeStart, setTimeStart] = useState<number>(Date.now());
  const [codeOutput, setCodeOutput] = useState("");
  const [runningCode, setRunningCode] = useState(false);
  
  // Proctoring state
  const webcamRef = useRef<Webcam>(null);
  const [proctorWarnings, setProctorWarnings] = useState<string[]>([]);
  const [tabSwitchCount, setTabSwitchCount] = useState(0);

  useEffect(() => {
    loadQuestions();
    setupProctoring();
    
    return () => {
      // Cleanup proctoring listeners
      document.removeEventListener("visibilitychange", handleVisibilityChange);
      document.removeEventListener("copy", handleCopyPaste);
      document.removeEventListener("paste", handleCopyPaste);
    };
  }, [assessmentId]);

  const loadQuestions = async () => {
    try {
      // Try to load from API first
      const response = await axios.get(`${API_BASE}/assessment/${assessmentId}/questions`);
      setQuestions(response.data.questions);
    } catch (error) {
      // Use demo questions for testing
      console.log("Using demo questions for testing");
      setQuestions(demoQuestions);
    } finally {
      setLoading(false);
    }
  };

  // Proctoring Setup
  const setupProctoring = () => {
    // Tab switching detection
    document.addEventListener("visibilitychange", handleVisibilityChange);
    
    // Copy-paste detection
    document.addEventListener("copy", handleCopyPaste);
    document.addEventListener("paste", handleCopyPaste);
    
    // Right-click prevention
    document.addEventListener("contextmenu", (e) => e.preventDefault());
  };

  const handleVisibilityChange = useCallback(() => {
    if (document.hidden) {
      setTabSwitchCount((prev) => prev + 1);
      const newWarning = `Tab switch detected at ${new Date().toLocaleTimeString()}`;
      setProctorWarnings((prev) => [...prev, newWarning]);
      
      toast.error("⚠️ Tab switching detected! This is being recorded.");
    }
  }, [assessmentId]);

  const handleCopyPaste = useCallback((e: Event) => {
    const eventType = e.type === "copy" ? "copy" : "paste";
    const warning = `${eventType} detected at ${new Date().toLocaleTimeString()}`;
    setProctorWarnings((prev) => [...prev, warning]);
    
    toast.error(`⚠️ ${eventType.charAt(0).toUpperCase() + eventType.slice(1)} detected!`);
  }, [assessmentId]);

  const currentQuestion = questions[currentIndex];

  const handleAnswerChange = (value: any) => {
    setAnswers((prev) => ({
      ...prev,
      [currentQuestion.id]: value,
    }));
  };

  const handleSubmitAnswer = async () => {
    if (!answers[currentQuestion.id] && answers[currentQuestion.id] !== 0) {
      toast.error("Please provide an answer");
      return;
    }

    setSubmitting(true);
    const timeTaken = Math.floor((Date.now() - timeStart) / 1000);

    try {
      // Mark as answered (demo mode - no API call needed for testing)
      setAnswers((prev) => ({
        ...prev,
        [currentQuestion.id]: { value: answers[currentQuestion.id], answered: true },
      }));
      
      toast.success("Answer submitted!");
      
      // Move to next question
      if (currentIndex < questions.length - 1) {
        setCurrentIndex(currentIndex + 1);
        setTimeStart(Date.now());
        setCodeOutput("");
      }
    } catch (error: any) {
      toast.error("Failed to submit answer");
    } finally {
      setSubmitting(false);
    }
  };

  const handleRunCode = async () => {
    if (!answers[currentQuestion.id]) {
      toast.error("Please write some code first");
      return;
    }

    setRunningCode(true);
    try {
      // Try API first
      const result = await axios.post(`${API_BASE}/assessment/execute-code`, {
        code: answers[currentQuestion.id],
        language: "python",
      });
      
      if (result.data.success) {
        setCodeOutput(result.data.output || "Code executed successfully (no output)");
      } else {
        setCodeOutput(`Error: ${result.data.error || "Unknown error"}`);
      }
    } catch (error) {
      // Demo mode - simulate code execution
      const code = answers[currentQuestion.id];
      if (code.includes("print")) {
        setCodeOutput("Hello, World! (simulated output)");
      } else {
        setCodeOutput("Code executed successfully (demo mode - no actual execution)");
      }
    } finally {
      setRunningCode(false);
    }
  };

  const handleCompleteAssessment = async () => {
    const answeredCount = Object.values(answers).filter((a: any) => a?.answered).length;
    if (answeredCount < questions.length) {
      const confirm = window.confirm(
        `You have answered ${answeredCount} of ${questions.length} questions. Are you sure you want to submit?`
      );
      if (!confirm) return;
    }

    toast.success("Assessment completed! (Demo mode)");
    router.push("/candidate/dashboard");
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-orange-500 border-t-transparent"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-3 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <h1 className="text-lg font-semibold text-gray-800">Assessment</h1>
            <span className="text-sm text-gray-500">
              Question {currentIndex + 1} of {questions.length}
            </span>
          </div>
          
          <div className="flex items-center gap-4">
            {/* Proctoring Status */}
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${
                tabSwitchCount === 0 ? "bg-green-500" : "bg-red-500"
              } animate-pulse`}></div>
              <span className="text-sm text-gray-600">
                {tabSwitchCount === 0 ? "Proctoring Active" : `${tabSwitchCount} violations`}
              </span>
            </div>
            
            <button
              onClick={handleCompleteAssessment}
              className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg text-sm"
            >
              Complete Assessment
            </button>
          </div>
        </div>
        
        {/* Progress Bar */}
        <div className="w-full bg-gray-200 h-1">
          <div
            className="bg-orange-500 h-1 transition-all"
            style={{ width: `${((currentIndex + 1) / questions.length) * 100}%` }}
          ></div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto p-4 grid lg:grid-cols-4 gap-4">
        {/* Question Navigator */}
        <div className="bg-white rounded-xl shadow-sm p-4">
          <h2 className="font-semibold text-gray-800 mb-3">Questions</h2>
          <div className="grid grid-cols-5 gap-2">
            {questions.map((q, idx) => (
              <button
                key={q.id}
                onClick={() => {
                  setCurrentIndex(idx);
                  setTimeStart(Date.now());
                  setCodeOutput("");
                }}
                className={`w-10 h-10 rounded-lg text-sm font-medium transition ${
                  idx === currentIndex
                    ? "bg-orange-500 text-white"
                    : answers[q.id]?.answered
                    ? "bg-green-100 text-green-700"
                    : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                }`}
              >
                {idx + 1}
              </button>
            ))}
          </div>
          
          {/* Legend */}
          <div className="mt-4 space-y-2 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-orange-500 rounded"></div>
              <span className="text-gray-600">Current</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-green-100 rounded"></div>
              <span className="text-gray-600">Answered</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-gray-100 rounded"></div>
              <span className="text-gray-600">Not answered</span>
            </div>
          </div>

          {/* Webcam Preview */}
          <div className="mt-4">
            <h3 className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
              <Camera className="w-4 h-4" /> Webcam
            </h3>
            <div className="rounded-lg overflow-hidden bg-gray-900">
              <Webcam
                ref={webcamRef}
                audio={false}
                width={200}
                height={150}
                screenshotFormat="image/jpeg"
                className="w-full"
              />
            </div>
          </div>
        </div>

        {/* Main Question Area */}
        <div className="lg:col-span-3">
          {currentQuestion && (
            <div className="bg-white rounded-xl shadow-sm p-6">
              {/* Question Header */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                    currentQuestion.category === "technical"
                      ? "bg-blue-100 text-blue-700"
                      : "bg-purple-100 text-purple-700"
                  }`}>
                    {currentQuestion.category}
                  </span>
                  <span className={`px-3 py-1 rounded-full text-sm ${
                    currentQuestion.difficulty === "easy"
                      ? "bg-green-100 text-green-700"
                      : currentQuestion.difficulty === "medium"
                      ? "bg-yellow-100 text-yellow-700"
                      : "bg-red-100 text-red-700"
                  }`}>
                    {currentQuestion.difficulty}
                  </span>
                  <span className="text-sm text-gray-500">
                    {currentQuestion.max_score} points
                  </span>
                </div>
                <div className="flex items-center gap-2 text-gray-500">
                  <Clock className="w-4 h-4" />
                  <span className="text-sm">{currentQuestion.time_limit_seconds}s limit</span>
                </div>
              </div>

              {/* Question Text */}
              <div className="mb-6">
                <h2 className="text-lg font-medium text-gray-800 whitespace-pre-wrap">
                  {currentQuestion.question_text}
                </h2>
                {currentQuestion.skill_tags && currentQuestion.skill_tags.length > 0 && (
                  <div className="flex gap-2 mt-3">
                    {currentQuestion.skill_tags.map((tag) => (
                      <span key={tag} className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* Answer Input based on question type */}
              {currentQuestion.question_type === "mcq" && (
                <MCQInput
                  options={currentQuestion.options || []}
                  selected={answers[currentQuestion.id]}
                  onChange={handleAnswerChange}
                  disabled={answers[currentQuestion.id]?.answered}
                />
              )}

              {currentQuestion.question_type === "coding" && (
                <CodingInput
                  value={answers[currentQuestion.id] || ""}
                  onChange={handleAnswerChange}
                  onRun={handleRunCode}
                  output={codeOutput}
                  running={runningCode}
                  disabled={answers[currentQuestion.id]?.answered}
                />
              )}

              {currentQuestion.question_type === "text" && (
                <TextInput
                  value={answers[currentQuestion.id] || ""}
                  onChange={handleAnswerChange}
                  disabled={answers[currentQuestion.id]?.answered}
                />
              )}

              {currentQuestion.question_type === "slider" && (
                <SliderInput
                  value={answers[currentQuestion.id] || 3}
                  onChange={handleAnswerChange}
                  disabled={answers[currentQuestion.id]?.answered}
                />
              )}

              {/* Navigation and Submit */}
              <div className="flex items-center justify-between mt-6 pt-6 border-t">
                <button
                  onClick={() => {
                    setCurrentIndex(Math.max(0, currentIndex - 1));
                    setTimeStart(Date.now());
                    setCodeOutput("");
                  }}
                  disabled={currentIndex === 0}
                  className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:text-gray-800 disabled:opacity-50"
                >
                  <ChevronLeft className="w-5 h-5" />
                  Previous
                </button>

                <button
                  onClick={handleSubmitAnswer}
                  disabled={submitting || answers[currentQuestion.id]?.answered}
                  className="flex items-center gap-2 bg-orange-500 hover:bg-orange-600 text-white px-6 py-2 rounded-lg disabled:opacity-50"
                >
                  {submitting ? (
                    "Submitting..."
                  ) : answers[currentQuestion.id]?.answered ? (
                    <>
                      <CheckCircle className="w-5 h-5" />
                      Answered
                    </>
                  ) : (
                    <>
                      <Send className="w-5 h-5" />
                      Submit Answer
                    </>
                  )}
                </button>

                <button
                  onClick={() => {
                    setCurrentIndex(Math.min(questions.length - 1, currentIndex + 1));
                    setTimeStart(Date.now());
                    setCodeOutput("");
                  }}
                  disabled={currentIndex === questions.length - 1}
                  className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:text-gray-800 disabled:opacity-50"
                >
                  Next
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// MCQ Component
function MCQInput({
  options,
  selected,
  onChange,
  disabled,
}: {
  options: string[];
  selected: number;
  onChange: (value: number) => void;
  disabled: boolean;
}) {
  return (
    <div className="space-y-3">
      {options.map((option, idx) => (
        <label
          key={idx}
          className={`flex items-center gap-3 p-4 rounded-lg border-2 cursor-pointer transition ${
            selected === idx
              ? "border-orange-500 bg-orange-50"
              : "border-gray-200 hover:border-gray-300"
          } ${disabled ? "opacity-50 cursor-not-allowed" : ""}`}
        >
          <input
            type="radio"
            name="mcq"
            checked={selected === idx}
            onChange={() => !disabled && onChange(idx)}
            className="w-5 h-5 text-orange-500"
            disabled={disabled}
          />
          <span className="text-gray-800">{option}</span>
        </label>
      ))}
    </div>
  );
}

// Coding Editor Component
function CodingInput({
  value,
  onChange,
  onRun,
  output,
  running,
  disabled,
}: {
  value: string;
  onChange: (value: string) => void;
  onRun: () => void;
  output: string;
  running: boolean;
  disabled: boolean;
}) {
  return (
    <div className="space-y-4">
      <div className="border rounded-lg overflow-hidden">
        <div className="bg-gray-800 px-4 py-2 flex items-center justify-between">
          <span className="text-white text-sm flex items-center gap-2">
            <Code className="w-4 h-4" /> Python
          </span>
          <button
            onClick={onRun}
            disabled={running || disabled}
            className="flex items-center gap-2 bg-green-500 hover:bg-green-600 text-white px-3 py-1 rounded text-sm disabled:opacity-50"
          >
            <Play className="w-4 h-4" />
            {running ? "Running..." : "Run Code"}
          </button>
        </div>
        <MonacoEditor
          height="300px"
          language="python"
          theme="vs-dark"
          value={value}
          onChange={(val) => !disabled && onChange(val || "")}
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            readOnly: disabled,
            scrollBeyondLastLine: false,
          }}
        />
      </div>
      
      {output && (
        <div className="bg-gray-900 rounded-lg p-4">
          <p className="text-gray-400 text-sm mb-2">Output:</p>
          <pre className="text-green-400 text-sm whitespace-pre-wrap font-mono">
            {output}
          </pre>
        </div>
      )}
    </div>
  );
}

// Text Input Component
function TextInput({
  value,
  onChange,
  disabled,
}: {
  value: string;
  onChange: (value: string) => void;
  disabled: boolean;
}) {
  return (
    <div>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        className="w-full h-48 p-4 border rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent resize-none text-gray-800"
        placeholder="Type your answer here..."
      />
      <p className="text-sm text-gray-500 mt-2">
        Word count: {value.split(/\s+/).filter(Boolean).length}
      </p>
    </div>
  );
}

// Slider Component
function SliderInput({
  value,
  onChange,
  disabled,
}: {
  value: number;
  onChange: (value: number) => void;
  disabled: boolean;
}) {
  const labels = [
    "Strongly Disagree",
    "Disagree",
    "Neutral",
    "Agree",
    "Strongly Agree",
  ];

  return (
    <div className="py-4">
      <div className="flex justify-between mb-2">
        {labels.map((label, idx) => (
          <span
            key={idx}
            className={`text-xs ${
              value === idx + 1 ? "text-orange-500 font-medium" : "text-gray-500"
            }`}
          >
            {label}
          </span>
        ))}
      </div>
      <input
        type="range"
        min="1"
        max="5"
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        disabled={disabled}
        className="w-full h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-orange-500"
      />
      <div className="flex justify-between mt-1">
        {[1, 2, 3, 4, 5].map((n) => (
          <span
            key={n}
            className={`text-sm font-medium ${
              value === n ? "text-orange-500" : "text-gray-400"
            }`}
          >
            {n}
          </span>
        ))}
      </div>
    </div>
  );
}
