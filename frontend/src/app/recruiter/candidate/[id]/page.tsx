"use client";
import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import Link from "next/link";
import { recruiterAPI, proctoringAPI } from "@/lib/api";
import { useAuthStore } from "@/lib/store";
import toast from "react-hot-toast";
import {
  ArrowLeft, User, Mail, FileText, Award, Shield, TrendingUp,
  CheckCircle, XCircle, AlertTriangle, Clock, Briefcase
} from "lucide-react";

export default function CandidateDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();
  const candidateId = Number(params.id);

  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login");
      return;
    }
    loadCandidate();
  }, [isAuthenticated, candidateId]);

  const loadCandidate = async () => {
    try {
      const response = await recruiterAPI.getCandidate(candidateId);
      setData(response.data);
    } catch (error) {
      toast.error("Failed to load candidate");
      router.push("/recruiter/dashboard");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-orange-500 border-t-transparent"></div>
      </div>
    );
  }

  if (!data) return null;

  const { candidate, resume, assessments, evaluation } = data;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <Link
            href="/recruiter/dashboard"
            className="flex items-center gap-2 text-gray-600 hover:text-gray-800 mb-4"
          >
            <ArrowLeft className="w-5 h-5" />
            Back to Dashboard
          </Link>
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center">
              <User className="w-8 h-8 text-orange-500" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-800">{candidate.name}</h1>
              <div className="flex items-center gap-4 text-gray-500">
                <span className="flex items-center gap-1">
                  <Mail className="w-4 h-4" />
                  {candidate.email}
                </span>
                <span className={`px-2 py-1 text-xs rounded-full ${
                  candidate.ranking === "high_match"
                    ? "bg-green-100 text-green-700"
                    : candidate.ranking === "potential"
                    ? "bg-yellow-100 text-yellow-700"
                    : "bg-red-100 text-red-700"
                }`}>
                  {candidate.ranking || "Not Evaluated"}
                </span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Left Column - Resume & Skills */}
          <div className="space-y-6">
            {/* Resume Summary */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                <FileText className="w-5 h-5 text-orange-500" />
                Resume Summary
              </h2>
              {resume ? (
                <div className="space-y-4">
                  <div>
                    <p className="text-sm text-gray-500">Experience</p>
                    <p className="font-medium text-gray-800">{resume.experience_years || 0} years</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Education</p>
                    {resume.education?.map((edu: any, idx: number) => (
                      <p key={idx} className="text-gray-800">{edu.degree} {edu.field}</p>
                    ))}
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Contact</p>
                    <p className="text-gray-800">{resume.contact_info?.email}</p>
                    <p className="text-gray-800">{resume.contact_info?.phone}</p>
                  </div>
                </div>
              ) : (
                <p className="text-gray-500">No resume uploaded</p>
              )}
            </div>

            {/* Skills */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-lg font-semibold text-gray-800 mb-4">Skills</h2>
              {resume?.skills?.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {resume.skills.map((skill: string, idx: number) => (
                    <span
                      key={idx}
                      className="px-3 py-1 bg-orange-50 text-orange-700 rounded-full text-sm"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500">No skills extracted</p>
              )}
            </div>
          </div>

          {/* Middle Column - Assessments */}
          <div className="space-y-6">
            {/* Assessment History */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                <Briefcase className="w-5 h-5 text-orange-500" />
                Assessment History
              </h2>
              {assessments?.length > 0 ? (
                <div className="space-y-4">
                  {assessments.map((assessment: any) => (
                    <div key={assessment.id} className="border rounded-lg p-4">
                      <div className="flex justify-between items-start mb-3">
                        <div>
                          <p className="font-medium text-gray-800">Assessment #{assessment.id}</p>
                          <p className="text-sm text-gray-500">
                            {assessment.started_at && new Date(assessment.started_at).toLocaleDateString()}
                          </p>
                        </div>
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          assessment.status === "completed"
                            ? "bg-green-100 text-green-700"
                            : "bg-yellow-100 text-yellow-700"
                        }`}>
                          {assessment.status}
                        </span>
                      </div>
                      
                      {assessment.status === "completed" && (
                        <div className="space-y-2">
                          <ScoreBar label="Technical" value={assessment.technical_score} />
                          <ScoreBar label="Psychometric" value={assessment.psychometric_score} />
                          <ScoreBar label="Total" value={assessment.total_score} />
                        </div>
                      )}

                      {/* Proctoring Summary */}
                      {assessment.proctoring?.total_events > 0 && (
                        <div className="mt-3 pt-3 border-t">
                          <p className="text-sm text-red-600 flex items-center gap-2">
                            <AlertTriangle className="w-4 h-4" />
                            {assessment.proctoring.total_events} proctoring events
                          </p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500">No assessments taken</p>
              )}
            </div>
          </div>

          {/* Right Column - Evaluation */}
          <div className="space-y-6">
            {/* Final Evaluation */}
            {evaluation ? (
              <>
                <div className={`rounded-xl shadow-sm p-6 ${
                  evaluation.recommendation === "hire"
                    ? "bg-green-50 border border-green-200"
                    : evaluation.recommendation === "consider"
                    ? "bg-yellow-50 border border-yellow-200"
                    : "bg-red-50 border border-red-200"
                }`}>
                  <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                    <Award className="w-5 h-5 text-orange-500" />
                    Final Evaluation
                  </h2>
                  
                  <div className="text-center mb-4">
                    <div className={`inline-flex items-center justify-center w-20 h-20 rounded-full ${
                      evaluation.recommendation === "hire"
                        ? "bg-green-100"
                        : evaluation.recommendation === "consider"
                        ? "bg-yellow-100"
                        : "bg-red-100"
                    }`}>
                      {evaluation.recommendation === "hire" ? (
                        <CheckCircle className="w-10 h-10 text-green-600" />
                      ) : evaluation.recommendation === "consider" ? (
                        <Clock className="w-10 h-10 text-yellow-600" />
                      ) : (
                        <XCircle className="w-10 h-10 text-red-600" />
                      )}
                    </div>
                    <p className={`text-2xl font-bold mt-2 ${
                      evaluation.recommendation === "hire"
                        ? "text-green-700"
                        : evaluation.recommendation === "consider"
                        ? "text-yellow-700"
                        : "text-red-700"
                    }`}>
                      {evaluation.recommendation.toUpperCase()}
                    </p>
                    <p className="text-3xl font-bold text-gray-800 mt-1">
                      {evaluation.final_score?.toFixed(1)}%
                    </p>
                  </div>

                  <div className="space-y-2 mb-4">
                    <ScoreBar label="Resume Match" value={evaluation.resume_match_score} />
                    <ScoreBar label="Assessment" value={evaluation.assessment_score} />
                    <ScoreBar label="Integrity" value={evaluation.integrity_score} />
                  </div>
                </div>

                {/* Rationale */}
                <div className="bg-white rounded-xl shadow-sm p-6">
                  <h3 className="font-semibold text-gray-800 mb-3">Decision Rationale</h3>
                  <p className="text-gray-600 text-sm">{evaluation.rationale}</p>
                </div>

                {/* Strengths & Weaknesses */}
                <div className="bg-white rounded-xl shadow-sm p-6">
                  <div className="mb-4">
                    <h3 className="font-semibold text-gray-800 mb-2 flex items-center gap-2">
                      <TrendingUp className="w-4 h-4 text-green-500" />
                      Strengths
                    </h3>
                    <ul className="space-y-1">
                      {evaluation.strengths?.map((s: string, i: number) => (
                        <li key={i} className="text-sm text-green-600 flex items-center gap-2">
                          <CheckCircle className="w-4 h-4" /> {s}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-800 mb-2 flex items-center gap-2">
                      <AlertTriangle className="w-4 h-4 text-orange-500" />
                      Areas for Improvement
                    </h3>
                    <ul className="space-y-1">
                      {evaluation.weaknesses?.map((w: string, i: number) => (
                        <li key={i} className="text-sm text-orange-600 flex items-center gap-2">
                          <AlertTriangle className="w-4 h-4" /> {w}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </>
            ) : (
              <div className="bg-white rounded-xl shadow-sm p-6 text-center">
                <Award className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500">No evaluation yet</p>
                <p className="text-sm text-gray-400">Candidate needs to complete an assessment</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

function ScoreBar({ label, value }: { label: string; value: number }) {
  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="text-gray-600">{label}</span>
        <span className="font-medium text-gray-800">{value?.toFixed(1)}%</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className={`h-2 rounded-full ${
            value >= 70 ? "bg-green-500" : value >= 50 ? "bg-yellow-500" : "bg-red-500"
          }`}
          style={{ width: `${Math.min(value || 0, 100)}%` }}
        ></div>
      </div>
    </div>
  );
}
