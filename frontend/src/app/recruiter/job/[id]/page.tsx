"use client";
import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import Link from "next/link";
import { recruiterAPI } from "@/lib/api";
import { useAuthStore } from "@/lib/store";
import toast from "react-hot-toast";
import {
  ArrowLeft, Briefcase, Users, CheckCircle, Clock, XCircle,
  TrendingUp, Eye
} from "lucide-react";

export default function JobDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();
  const jobId = Number(params.id);

  const [job, setJob] = useState<any>(null);
  const [shortlist, setShortlist] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login");
      return;
    }
    loadJob();
    loadShortlist();
  }, [isAuthenticated, jobId]);

  const loadJob = async () => {
    try {
      const response = await recruiterAPI.getJob(jobId);
      setJob(response.data);
    } catch (error) {
      toast.error("Failed to load job");
    } finally {
      setLoading(false);
    }
  };

  const loadShortlist = async () => {
    try {
      const response = await recruiterAPI.getShortlist(jobId);
      setShortlist(response.data);
    } catch (error) {
      console.error("Failed to load shortlist");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-orange-500 border-t-transparent"></div>
      </div>
    );
  }

  if (!job) return null;

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
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                <Briefcase className="w-6 h-6 text-orange-500" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-800">{job.job?.title}</h1>
                <span className={`px-2 py-1 text-xs rounded-full ${
                  job.job?.is_active ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"
                }`}>
                  {job.job?.is_active ? "Active" : "Inactive"}
                </span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Job Details */}
          <div className="lg:col-span-1 space-y-6">
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-lg font-semibold text-gray-800 mb-4">Job Details</h2>
              <p className="text-gray-600 mb-4">{job.job?.description}</p>
              
              <div className="space-y-3">
                <div>
                  <p className="text-sm text-gray-500">Required Skills</p>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {job.job?.required_skills?.map((skill: string, idx: number) => (
                      <span key={idx} className="px-2 py-1 bg-orange-50 text-orange-700 rounded text-sm">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
                
                <div>
                  <p className="text-sm text-gray-500">Preferred Skills</p>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {job.job?.preferred_skills?.map((skill: string, idx: number) => (
                      <span key={idx} className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-sm">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <p className="text-sm text-gray-500">Min Experience</p>
                  <p className="text-gray-800">{job.job?.min_experience_years} years</p>
                </div>
              </div>
            </div>

            {/* Stats */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-lg font-semibold text-gray-800 mb-4">Application Stats</h2>
              <div className="space-y-3">
                <StatRow label="Total Applications" value={job.stats?.total_applications || 0} />
                <StatRow label="Completed" value={job.stats?.completed || 0} color="green" />
                <StatRow label="In Progress" value={job.stats?.in_progress || 0} color="yellow" />
                <StatRow label="Not Started" value={job.stats?.not_started || 0} color="gray" />
              </div>
            </div>
          </div>

          {/* Shortlisted Candidates */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                <Users className="w-5 h-5 text-orange-500" />
                Candidate Shortlist
              </h2>

              {shortlist ? (
                <div className="space-y-6">
                  {/* High Match */}
                  <CandidateGroup
                    title="High Match"
                    icon={<CheckCircle className="w-5 h-5 text-green-500" />}
                    candidates={shortlist.high_match || []}
                    color="green"
                  />

                  {/* Potential */}
                  <CandidateGroup
                    title="Potential"
                    icon={<Clock className="w-5 h-5 text-yellow-500" />}
                    candidates={shortlist.potential || []}
                    color="yellow"
                  />

                  {/* Reject */}
                  <CandidateGroup
                    title="Not Recommended"
                    icon={<XCircle className="w-5 h-5 text-red-500" />}
                    candidates={shortlist.reject || []}
                    color="red"
                  />
                </div>
              ) : (
                <p className="text-gray-500 text-center py-8">No candidates have completed assessments yet</p>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

function StatRow({ label, value, color = "gray" }: { label: string; value: number; color?: string }) {
  const colors: Record<string, string> = {
    green: "text-green-600",
    yellow: "text-yellow-600",
    gray: "text-gray-600",
  };

  return (
    <div className="flex justify-between items-center">
      <span className="text-gray-600">{label}</span>
      <span className={`font-semibold ${colors[color]}`}>{value}</span>
    </div>
  );
}

function CandidateGroup({
  title,
  icon,
  candidates,
  color,
}: {
  title: string;
  icon: React.ReactNode;
  candidates: any[];
  color: string;
}) {
  const borderColors: Record<string, string> = {
    green: "border-green-200",
    yellow: "border-yellow-200",
    red: "border-red-200",
  };

  if (candidates.length === 0) {
    return null;
  }

  return (
    <div className={`border rounded-lg ${borderColors[color]}`}>
      <div className="p-3 bg-gray-50 border-b flex items-center gap-2">
        {icon}
        <span className="font-medium text-gray-800">{title}</span>
        <span className="text-sm text-gray-500">({candidates.length})</span>
      </div>
      <div className="divide-y">
        {candidates.map((candidate: any) => (
          <div key={candidate.candidate_id} className="p-4 flex items-center justify-between">
            <div>
              <p className="font-medium text-gray-800">{candidate.name}</p>
              <p className="text-sm text-gray-500">{candidate.email}</p>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="font-semibold text-gray-800">{candidate.final_score?.toFixed(1)}%</p>
                <p className="text-xs text-gray-500">
                  Tech: {candidate.technical_score?.toFixed(0)}% | Psych: {candidate.psychometric_score?.toFixed(0)}%
                </p>
              </div>
              <Link
                href={`/recruiter/candidate/${candidate.candidate_id}`}
                className="text-orange-500 hover:text-orange-600"
              >
                <Eye className="w-5 h-5" />
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
