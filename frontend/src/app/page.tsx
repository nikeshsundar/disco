"use client";
import Link from "next/link";
import { Briefcase, Users, Shield, Brain, FileCheck, BarChart3 } from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <div className="bg-gradient-to-r from-orange-500 to-orange-600 text-white p-2 rounded-lg">
              <Briefcase className="w-6 h-6" />
            </div>
            <span className="text-xl font-bold text-gray-800">CYGNUSA Elite-Hire</span>
          </div>
          <nav className="flex gap-4">
            <Link
              href="/candidate/dashboard"
              className="text-gray-600 hover:text-orange-500 px-4 py-2 transition"
            >
              Candidate Portal
            </Link>
            <Link
              href="/recruiter/dashboard"
              className="bg-orange-500 hover:bg-orange-600 text-white px-4 py-2 rounded-lg transition"
            >
              Recruiter Portal
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="bg-gradient-to-br from-orange-500 via-orange-600 to-red-600 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <h1 className="text-5xl font-bold mb-6">
            AI-Enabled HR Evaluation System
          </h1>
          <p className="text-xl mb-8 opacity-90 max-w-2xl mx-auto">
            From resume upload to final hiring decision — with transparent rationale at every step.
            Streamline your recruitment with intelligent assessment and explainable recommendations.
          </p>
          <div className="flex gap-4 justify-center">
            <Link
              href="/candidate/dashboard"
              className="bg-white text-orange-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition"
            >
              I&apos;m a Candidate
            </Link>
            <Link
              href="/recruiter/dashboard"
              className="bg-orange-700 text-white px-8 py-3 rounded-lg font-semibold hover:bg-orange-800 transition"
            >
              I&apos;m a Recruiter
            </Link>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12 text-gray-800">
            Core Features
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            <FeatureCard
              icon={<FileCheck className="w-8 h-8" />}
              title="Multi-Modal Assessment"
              description="MCQs, coding challenges, text responses, and psychometric sliders — all in one platform."
            />
            <FeatureCard
              icon={<Brain className="w-8 h-8" />}
              title="Dual-Track Scoring"
              description="Technical skills AND soft skills assessment for a complete candidate evaluation."
            />
            <FeatureCard
              icon={<Shield className="w-8 h-8" />}
              title="Integrity Shield"
              description="Advanced proctoring with face detection, tab monitoring, and audit trail logging."
            />
            <FeatureCard
              icon={<Users className="w-8 h-8" />}
              title="Smart Resume Shortlisting"
              description="Automatic parsing and matching against job requirements with skill extraction."
            />
            <FeatureCard
              icon={<BarChart3 className="w-8 h-8" />}
              title="Explainable Decisions"
              description="Clear rationale for every recommendation — know exactly why a candidate is ranked."
            />
            <FeatureCard
              icon={<Briefcase className="w-8 h-8" />}
              title="Recruiter Dashboard"
              description="Comprehensive candidate management with shortlisting and detailed analytics."
            />
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12 text-gray-800">
            How It Works
          </h2>
          <div className="flex flex-col md:flex-row gap-8 items-center justify-center">
            <Step number={1} title="Upload Resume" description="Candidates upload their resume for automatic parsing" />
            <Arrow />
            <Step number={2} title="Take Assessment" description="Complete technical and psychometric evaluations" />
            <Arrow />
            <Step number={3} title="Get Scored" description="Automatic scoring with integrity verification" />
            <Arrow />
            <Step number={4} title="View Decision" description="Transparent hiring recommendation with rationale" />
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-8">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <p className="text-gray-400">
            © 2026 CYGNUSA Elite-Hire | SRM Innovation Hackathon
          </p>
        </div>
      </footer>
    </div>
  );
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode; title: string; description: string }) {
  return (
    <div className="bg-gray-50 p-6 rounded-xl hover:shadow-lg transition">
      <div className="text-orange-500 mb-4">{icon}</div>
      <h3 className="text-xl font-semibold mb-2 text-gray-800">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </div>
  );
}

function Step({ number, title, description }: { number: number; title: string; description: string }) {
  return (
    <div className="text-center">
      <div className="w-12 h-12 bg-orange-500 text-white rounded-full flex items-center justify-center text-xl font-bold mx-auto mb-3">
        {number}
      </div>
      <h3 className="font-semibold text-gray-800">{title}</h3>
      <p className="text-sm text-gray-600 max-w-[150px]">{description}</p>
    </div>
  );
}

function Arrow() {
  return (
    <div className="hidden md:block text-gray-300 text-2xl">→</div>
  );
}
