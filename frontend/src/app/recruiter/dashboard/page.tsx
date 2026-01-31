"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import axios from "axios";
import toast from "react-hot-toast";
import {
  Briefcase, Users, FileText, Plus, LogOut, User, BarChart3,
  TrendingUp, CheckCircle, Clock, XCircle, Eye, ChevronRight
} from "lucide-react";

const API_BASE = "http://localhost:8000/api";

// Mock user for testing (no auth required)
const mockUser = {
  id: 1,
  email: "recruiter@cygnusa.com",
  full_name: "Test Recruiter",
  role: "recruiter"
};

interface DashboardData {
  jobs_count: number;
  active_jobs: number;
  total_candidates: number;
  status_breakdown: Record<string, number>;
  ranking_breakdown: Record<string, number>;
  jobs: any[];
  recent_evaluations: any[];
}

export default function RecruiterDashboard() {
  const router = useRouter();
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("overview");

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const response = await axios.get(`${API_BASE}/recruiter/dashboard`);
      setData(response.data);
    } catch (error) {
      // Use demo data if API fails
      setData({
        jobs_count: 2,
        active_jobs: 2,
        total_candidates: 0,
        status_breakdown: { pending: 0, in_progress: 0, completed: 0 },
        ranking_breakdown: { high_match: 0, potential: 0, low_match: 0 },
        jobs: [],
        recent_evaluations: []
      });
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

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <div className="bg-gradient-to-r from-orange-500 to-orange-600 text-white p-2 rounded-lg">
              <Briefcase className="w-6 h-6" />
            </div>
            <span className="text-xl font-bold text-gray-800">CYGNUSA Elite-Hire</span>
            <span className="ml-2 px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded-full">
              Recruiter
            </span>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-gray-600">
              <User className="w-5 h-5" />
              <span>{mockUser.full_name}</span>
            </div>
            <Link
              href="/candidate/dashboard"
              className="text-orange-500 hover:text-orange-600 font-medium"
            >
              Switch to Candidate →
            </Link>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4">
          <nav className="flex gap-8">
            {[
              { id: "overview", label: "Overview", icon: BarChart3 },
              { id: "jobs", label: "Jobs", icon: Briefcase },
              { id: "candidates", label: "Candidates", icon: Users },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 py-4 border-b-2 transition ${
                  activeTab === tab.id
                    ? "border-orange-500 text-orange-500"
                    : "border-transparent text-gray-500 hover:text-gray-700"
                }`}
              >
                <tab.icon className="w-5 h-5" />
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </div>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {activeTab === "overview" && <OverviewTab data={data} />}
        {activeTab === "jobs" && <JobsTab />}
        {activeTab === "candidates" && <CandidatesTab />}
      </main>
    </div>
  );
}

// Overview Tab
function OverviewTab({ data }: { data: DashboardData | null }) {
  if (!data) return null;

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid md:grid-cols-4 gap-4">
        <StatCard
          label="Total Jobs"
          value={data.jobs_count}
          icon={<Briefcase className="w-6 h-6" />}
          color="blue"
        />
        <StatCard
          label="Active Jobs"
          value={data.active_jobs}
          icon={<CheckCircle className="w-6 h-6" />}
          color="green"
        />
        <StatCard
          label="Total Candidates"
          value={data.total_candidates}
          icon={<Users className="w-6 h-6" />}
          color="purple"
        />
        <StatCard
          label="High Match"
          value={data.ranking_breakdown.high_match || 0}
          icon={<TrendingUp className="w-6 h-6" />}
          color="orange"
        />
      </div>

      {/* Candidate Status Breakdown */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Candidate Status</h2>
          <div className="space-y-4">
            <StatusBar
              label="Pending"
              value={data.status_breakdown.pending || 0}
              total={data.total_candidates}
              color="gray"
            />
            <StatusBar
              label="In Progress"
              value={data.status_breakdown.in_progress || 0}
              total={data.total_candidates}
              color="yellow"
            />
            <StatusBar
              label="Completed"
              value={data.status_breakdown.completed || 0}
              total={data.total_candidates}
              color="green"
            />
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Candidate Ranking</h2>
          <div className="space-y-4">
            <StatusBar
              label="High Match"
              value={data.ranking_breakdown.high_match || 0}
              total={data.total_candidates}
              color="green"
            />
            <StatusBar
              label="Potential"
              value={data.ranking_breakdown.potential || 0}
              total={data.total_candidates}
              color="yellow"
            />
            <StatusBar
              label="Reject"
              value={data.ranking_breakdown.reject || 0}
              total={data.total_candidates}
              color="red"
            />
          </div>
        </div>
      </div>

      {/* Recent Evaluations */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">Recent Evaluations</h2>
        {data.recent_evaluations.length === 0 ? (
          <p className="text-gray-500">No evaluations yet</p>
        ) : (
          <div className="space-y-3">
            {data.recent_evaluations.map((eval_: any, idx: number) => (
              <div
                key={idx}
                className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
              >
                <div className="flex items-center gap-4">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                    eval_.recommendation === "hire"
                      ? "bg-green-100 text-green-600"
                      : eval_.recommendation === "consider"
                      ? "bg-yellow-100 text-yellow-600"
                      : "bg-red-100 text-red-600"
                  }`}>
                    {eval_.recommendation === "hire" ? (
                      <CheckCircle className="w-5 h-5" />
                    ) : eval_.recommendation === "consider" ? (
                      <Clock className="w-5 h-5" />
                    ) : (
                      <XCircle className="w-5 h-5" />
                    )}
                  </div>
                  <div>
                    <p className="font-medium text-gray-800">Candidate #{eval_.candidate_id}</p>
                    <p className="text-sm text-gray-500">
                      {new Date(eval_.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className={`font-semibold ${
                    eval_.recommendation === "hire"
                      ? "text-green-600"
                      : eval_.recommendation === "consider"
                      ? "text-yellow-600"
                      : "text-red-600"
                  }`}>
                    {eval_.recommendation.toUpperCase()}
                  </p>
                  <p className="text-sm text-gray-500">Score: {eval_.final_score?.toFixed(1)}%</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// Jobs Tab
function JobsTab() {
  const [jobs, setJobs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    required_skills: "",
    preferred_skills: "",
    min_experience_years: 0,
    education_requirements: "",
  });

  useEffect(() => {
    loadJobs();
  }, []);

  const loadJobs = async () => {
    try {
      const response = await axios.get(`${API_BASE}/recruiter/jobs`);
      setJobs(response.data);
    } catch (error) {
      setJobs([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateJob = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await axios.post(`${API_BASE}/recruiter/jobs`, {
        ...formData,
        required_skills: formData.required_skills.split(",").map((s) => s.trim()),
        preferred_skills: formData.preferred_skills.split(",").map((s) => s.trim()),
        education_requirements: formData.education_requirements.split(",").map((s) => s.trim()),
      });
      toast.success("Job created successfully!");
      setShowForm(false);
      setFormData({
        title: "",
        description: "",
        required_skills: "",
        preferred_skills: "",
        min_experience_years: 0,
        education_requirements: "",
      });
      loadJobs();
    } catch (error) {
      toast.error("Failed to create job");
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold text-gray-800">Job Listings</h2>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 bg-orange-500 hover:bg-orange-600 text-white px-4 py-2 rounded-lg"
        >
          <Plus className="w-5 h-5" />
          Create Job
        </button>
      </div>

      {showForm && (
        <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">New Job Posting</h3>
          <form onSubmit={handleCreateJob} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Job Title</label>
              <input
                type="text"
                required
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-orange-500 text-gray-800"
                placeholder="e.g., Full Stack Developer"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea
                required
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-orange-500 h-24 text-gray-800"
                placeholder="Job description..."
              />
            </div>
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Required Skills (comma separated)
                </label>
                <input
                  type="text"
                  value={formData.required_skills}
                  onChange={(e) => setFormData({ ...formData, required_skills: e.target.value })}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-orange-500 text-gray-800"
                  placeholder="Python, React, SQL"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Preferred Skills (comma separated)
                </label>
                <input
                  type="text"
                  value={formData.preferred_skills}
                  onChange={(e) => setFormData({ ...formData, preferred_skills: e.target.value })}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-orange-500 text-gray-800"
                  placeholder="Docker, AWS, TypeScript"
                />
              </div>
            </div>
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Min Experience (years)
                </label>
                <input
                  type="number"
                  min="0"
                  value={formData.min_experience_years}
                  onChange={(e) => setFormData({ ...formData, min_experience_years: Number(e.target.value) })}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-orange-500 text-gray-800"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Education Requirements
                </label>
                <input
                  type="text"
                  value={formData.education_requirements}
                  onChange={(e) => setFormData({ ...formData, education_requirements: e.target.value })}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-orange-500 text-gray-800"
                  placeholder="Bachelor's in CS, B.Tech"
                />
              </div>
            </div>
            <div className="flex justify-end gap-3">
              <button
                type="button"
                onClick={() => setShowForm(false)}
                className="px-4 py-2 text-gray-600 hover:text-gray-800"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="bg-orange-500 hover:bg-orange-600 text-white px-6 py-2 rounded-lg"
              >
                Create Job
              </button>
            </div>
          </form>
        </div>
      )}

      {loading ? (
        <p className="text-gray-500">Loading...</p>
      ) : jobs.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm p-8 text-center">
          <Briefcase className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">No jobs created yet</p>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 gap-4">
          {jobs.map((job) => (
            <div key={job.id} className="bg-white rounded-xl shadow-sm p-6">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="text-lg font-semibold text-gray-800">{job.title}</h3>
                  <p className="text-gray-500 text-sm mt-1 line-clamp-2">{job.description}</p>
                </div>
                <span className={`px-2 py-1 text-xs rounded-full ${
                  job.is_active ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"
                }`}>
                  {job.is_active ? "Active" : "Inactive"}
                </span>
              </div>
              <div className="mt-4">
                <p className="text-sm text-gray-600">
                  Required: {job.required_skills?.slice(0, 4).join(", ")}
                </p>
                <p className="text-sm text-gray-600">
                  Experience: {job.min_experience_years}+ years
                </p>
              </div>
              <Link
                href={`/recruiter/job/${job.id}`}
                className="mt-4 flex items-center gap-2 text-orange-500 hover:text-orange-600 text-sm font-medium"
              >
                View Details <ChevronRight className="w-4 h-4" />
              </Link>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// Candidates Tab
function CandidatesTab() {
  const [candidates, setCandidates] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState({ status: "", ranking: "" });

  useEffect(() => {
    loadCandidates();
  }, [filter]);

  const loadCandidates = async () => {
    setLoading(true);
    try {
      const queryParams = new URLSearchParams();
      if (filter.status) queryParams.append('status', filter.status);
      if (filter.ranking) queryParams.append('ranking', filter.ranking);
      
      const response = await axios.get(`${API_BASE}/recruiter/candidates?${queryParams}`);
      setCandidates(response.data);
    } catch (error) {
      setCandidates([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold text-gray-800">All Candidates</h2>
        <div className="flex gap-3">
          <select
            value={filter.status}
            onChange={(e) => setFilter({ ...filter, status: e.target.value })}
            className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-orange-500 text-gray-800"
          >
            <option value="">All Status</option>
            <option value="pending">Pending</option>
            <option value="in_progress">In Progress</option>
            <option value="completed">Completed</option>
          </select>
          <select
            value={filter.ranking}
            onChange={(e) => setFilter({ ...filter, ranking: e.target.value })}
            className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-orange-500 text-gray-800"
          >
            <option value="">All Rankings</option>
            <option value="high_match">High Match</option>
            <option value="potential">Potential</option>
            <option value="reject">Reject</option>
          </select>
        </div>
      </div>

      {loading ? (
        <p className="text-gray-500">Loading...</p>
      ) : candidates.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm p-8 text-center">
          <Users className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">No candidates found</p>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Candidate</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Ranking</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Skills</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Score</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {candidates.map((candidate) => (
                <tr key={candidate.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div>
                      <p className="font-medium text-gray-800">{candidate.name}</p>
                      <p className="text-sm text-gray-500">{candidate.email}</p>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      candidate.status === "completed"
                        ? "bg-green-100 text-green-700"
                        : candidate.status === "in_progress"
                        ? "bg-yellow-100 text-yellow-700"
                        : "bg-gray-100 text-gray-600"
                    }`}>
                      {candidate.status}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      candidate.ranking === "high_match"
                        ? "bg-green-100 text-green-700"
                        : candidate.ranking === "potential"
                        ? "bg-yellow-100 text-yellow-700"
                        : candidate.ranking === "reject"
                        ? "bg-red-100 text-red-700"
                        : "bg-gray-100 text-gray-600"
                    }`}>
                      {candidate.ranking || "N/A"}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <p className="text-sm text-gray-600 truncate max-w-[200px]">
                      {candidate.skills?.slice(0, 3).join(", ") || "N/A"}
                    </p>
                  </td>
                  <td className="px-6 py-4">
                    <p className="font-medium text-gray-800">
                      {candidate.evaluation?.final_score?.toFixed(1) || "-"}%
                    </p>
                  </td>
                  <td className="px-6 py-4">
                    <Link
                      href={`/recruiter/candidate/${candidate.id}`}
                      className="text-orange-500 hover:text-orange-600"
                    >
                      <Eye className="w-5 h-5" />
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

// Helper Components
function StatCard({
  label,
  value,
  icon,
  color,
}: {
  label: string;
  value: number;
  icon: React.ReactNode;
  color: string;
}) {
  const colors: Record<string, string> = {
    blue: "bg-blue-50 text-blue-600",
    green: "bg-green-50 text-green-600",
    purple: "bg-purple-50 text-purple-600",
    orange: "bg-orange-50 text-orange-600",
  };

  return (
    <div className="bg-white rounded-xl shadow-sm p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-500">{label}</p>
          <p className="text-3xl font-bold text-gray-800 mt-1">{value}</p>
        </div>
        <div className={`p-3 rounded-lg ${colors[color]}`}>{icon}</div>
      </div>
    </div>
  );
}

function StatusBar({
  label,
  value,
  total,
  color,
}: {
  label: string;
  value: number;
  total: number;
  color: string;
}) {
  const percentage = total > 0 ? (value / total) * 100 : 0;
  const colors: Record<string, string> = {
    gray: "bg-gray-400",
    yellow: "bg-yellow-400",
    green: "bg-green-500",
    red: "bg-red-500",
  };

  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="text-gray-600">{label}</span>
        <span className="text-gray-800 font-medium">{value}</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className={`h-2 rounded-full ${colors[color]}`}
          style={{ width: `${percentage}%` }}
        ></div>
      </div>
    </div>
  );
}
