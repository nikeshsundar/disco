"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import axios from "axios";
import toast from "react-hot-toast";
import {
  Briefcase, Upload, FileText, CheckCircle, Clock,
  User, TrendingUp, Play
} from "lucide-react";

const API_BASE = "http://localhost:8000/api";

// Mock user for testing (no auth required)
const mockUser = {
  id: 1,
  email: "test@example.com",
  full_name: "Test Candidate",
  role: "candidate"
};

export default function CandidateDashboard() {
  const router = useRouter();
  const [jobs, setJobs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [parsedResume, setParsedResume] = useState<any>(null);

  useEffect(() => {
    loadJobs();
  }, []);

  const loadJobs = async () => {
    try {
      const response = await axios.get(`${API_BASE}/recruiter/jobs`);
      setJobs(response.data);
    } catch (error) {
      console.log("No jobs available yet");
      setJobs([]);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    const allowedTypes = ['.pdf', '.docx', '.doc'];
    const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
    if (!allowedTypes.includes(ext)) {
      toast.error("Please upload a PDF or Word document");
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API_BASE}/candidate/resume/parse-test`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      const data = response.data.parsed_data;
      
      // Check if there was an extraction error (image-based PDF)
      if (data.error) {
        toast.error(data.error);
        // Still show the result so user knows what happened
        setParsedResume({
          ...data,
          isImagePDF: true
        });
      } else if (data.skills && data.skills.length > 0) {
        setParsedResume(data);
        toast.success("Resume uploaded and parsed successfully!");
      } else {
        // No skills found - might be extraction issue
        toast.error("Could not extract data. Try uploading a DOCX file instead.");
        setParsedResume({
          ...data,
          extractionIssue: true
        });
      }
    } catch (error: any) {
      console.error("Upload error:", error);
      toast.error("Upload failed. Please try again.");
    } finally {
      setUploading(false);
    }
  };

  const startAssessment = (jobId: number) => {
    router.push(`/candidate/assessment/${jobId}`);
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
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-gray-600">
              <User className="w-5 h-5" />
              <span>{mockUser.full_name}</span>
            </div>
            <Link
              href="/recruiter/dashboard"
              className="text-orange-500 hover:text-orange-600 font-medium"
            >
              Switch to Recruiter →
            </Link>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-8">Candidate Dashboard</h1>

        <div className="grid md:grid-cols-3 gap-6 mb-8">
          {/* Resume Upload Card */}
          <div className="bg-white rounded-xl shadow-sm p-6 md:col-span-2">
            <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <FileText className="w-5 h-5 text-orange-500" />
              Resume
            </h2>
            
            {parsedResume ? (
              <div className="space-y-4">
                {/* Error/Warning for image-based PDFs */}
                {(parsedResume.error || parsedResume.isImagePDF || parsedResume.extractionIssue) ? (
                  <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-lg">
                    <div className="flex items-center gap-2 text-yellow-700 font-medium mb-2">
                      ⚠️ Could not extract text from your PDF
                    </div>
                    <p className="text-yellow-600 text-sm mb-3">
                      Your PDF appears to be image-based or has embedded fonts that can&apos;t be read.
                      Please try one of these options:
                    </p>
                    <ul className="text-yellow-600 text-sm list-disc ml-5 space-y-1">
                      <li>Save your resume as a <strong>DOCX file</strong> from Word/Google Docs</li>
                      <li>Export as a text-based PDF (not scanned)</li>
                      <li>Copy-paste your resume content into a simple document</li>
                    </ul>
                    <button
                      onClick={() => setParsedResume(null)}
                      className="mt-3 bg-yellow-500 hover:bg-yellow-600 text-white px-4 py-2 rounded text-sm"
                    >
                      Try Again
                    </button>
                  </div>
                ) : (
                  <>
                    <div className="flex items-center gap-2 text-green-600">
                      <CheckCircle className="w-5 h-5" />
                      <span className="font-medium">Resume uploaded and parsed successfully!</span>
                    </div>
                    
                    {/* Name and Contact */}
                    {(parsedResume.name || parsedResume.contact_info?.email) && (
                      <div className="bg-blue-50 p-4 rounded-lg">
                        {parsedResume.name && (
                          <h3 className="font-semibold text-lg text-gray-800">{parsedResume.name}</h3>
                        )}
                        <div className="flex gap-4 text-sm text-gray-600 mt-1">
                          {parsedResume.contact_info?.email && <span>📧 {parsedResume.contact_info.email}</span>}
                          {parsedResume.contact_info?.phone && <span>📱 {parsedResume.contact_info.phone}</span>}
                        </div>
                      </div>
                    )}
                    
                    <div className="grid md:grid-cols-2 gap-4">
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <h3 className="font-medium text-gray-700 mb-2">Skills Detected ({parsedResume.skills?.length || 0})</h3>
                        <div className="flex flex-wrap gap-2 max-h-40 overflow-y-auto">
                          {parsedResume.skills?.slice(0, 20).map((skill: string, i: number) => (
                            <span key={i} className="bg-orange-100 text-orange-700 px-2 py-1 rounded text-sm">
                              {skill}
                            </span>
                          ))}
                          {parsedResume.skills?.length > 20 && (
                            <span className="text-gray-500 text-sm">+{parsedResume.skills.length - 20} more</span>
                          )}
                        </div>
                      </div>
                      
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <h3 className="font-medium text-gray-700 mb-2">Experience</h3>
                        <p className="text-gray-600">
                          {parsedResume.experience_years === 0 ? "Fresher / Entry Level" : 
                           parsedResume.experience_years < 1 ? "< 1 year (Internship experience)" :
                           `${parsedResume.experience_years} year${parsedResume.experience_years > 1 ? 's' : ''}`}
                        </p>
                        
                        <h3 className="font-medium text-gray-700 mt-3 mb-2">Education</h3>
                        <div className="text-gray-600 text-sm">
                          {Array.isArray(parsedResume.education) ? 
                            parsedResume.education.map((edu: any, i: number) => (
                              <div key={i} className="mb-1">
                                {typeof edu === 'string' ? edu : `${edu.degree}${edu.field ? ` in ${edu.field}` : ''}`}
                              </div>
                            )) : "Not specified"}
                        </div>
                      </div>
                    </div>

                    <button
                      onClick={() => setParsedResume(null)}
                      className="text-orange-500 hover:text-orange-600 text-sm"
                    >
                      Upload a different resume
                    </button>
                  </>
                )}
              </div>
            ) : (
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600 mb-4">Upload your resume to get started</p>
                <label className="cursor-pointer">
                  <input
                    type="file"
                    accept=".pdf,.docx,.doc"
                    onChange={handleFileUpload}
                    className="hidden"
                  />
                  <span className={`inline-flex items-center gap-2 bg-orange-500 hover:bg-orange-600 text-white px-6 py-3 rounded-lg font-medium transition ${uploading ? 'opacity-50 cursor-not-allowed' : ''}`}>
                    {uploading ? (
                      <>
                        <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
                        Processing...
                      </>
                    ) : (
                      <>
                        <Upload className="w-5 h-5" />
                        Choose File (PDF/DOCX)
                      </>
                    )}
                  </span>
                </label>
              </div>
            )}
          </div>

          {/* Status Card */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-orange-500" />
              Your Status
            </h2>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Resume</span>
                <span className={`px-2 py-1 rounded text-sm ${parsedResume ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}`}>
                  {parsedResume ? 'Uploaded' : 'Pending'}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Assessments</span>
                <span className="px-2 py-1 rounded text-sm bg-gray-100 text-gray-600">
                  0 Completed
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Overall Ranking</span>
                <span className="px-2 py-1 rounded text-sm bg-gray-100 text-gray-600">
                  Not evaluated
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Available Jobs */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <Briefcase className="w-5 h-5 text-orange-500" />
            Available Positions
          </h2>

          {jobs.length === 0 ? (
            <div className="text-center py-8">
              <Briefcase className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">No positions available at the moment.</p>
              <p className="text-gray-400 text-sm mt-2">Check back later or contact the recruiter.</p>
              
              {/* Demo button to start assessment anyway */}
              <button
                onClick={() => router.push('/candidate/assessment/1')}
                className="mt-4 inline-flex items-center gap-2 bg-orange-500 hover:bg-orange-600 text-white px-6 py-3 rounded-lg font-medium transition"
              >
                <Play className="w-5 h-5" />
                Start Demo Assessment
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              {jobs.map((job: any) => (
                <div key={job.id} className="border rounded-lg p-4 hover:border-orange-300 transition">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-semibold text-gray-800">{job.title}</h3>
                      <p className="text-gray-600 text-sm mt-1">{job.description?.substring(0, 100)}...</p>
                      <div className="flex gap-2 mt-2 flex-wrap">
                        {job.required_skills?.slice(0, 4).map((skill: string, i: number) => (
                          <span key={i} className="bg-gray-100 text-gray-600 px-2 py-1 rounded text-xs">
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                    <button
                      onClick={() => startAssessment(job.id)}
                      className="bg-orange-500 hover:bg-orange-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition flex items-center gap-2"
                    >
                      <Play className="w-4 h-4" />
                      Take Assessment
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
