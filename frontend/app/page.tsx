"use client";

import Link from "next/link";
import { useAuth } from "@/lib/auth-context";

export default function Home() {
  const { user, loading, logout } = useAuth();

  return (
    <div className="min-h-screen flex flex-col overflow-x-hidden relative">
      {/* Background Shapes */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden z-0 pointer-events-none">
        <div className="absolute top-[-50px] right-[18%] w-[500px] h-[500px] bg-[#A2B6A3] rounded-full opacity-30 blur-[20px]"></div>
        <div className="absolute top-[80px] right-[5%] w-[300px] h-[300px] opacity-70" style={{ backgroundImage: 'radial-gradient(#d4cdbf 2.5px, transparent 2.5px)', backgroundSize: '24px 24px' }}></div>
        <div className="absolute top-[250px] right-[42%] w-[450px] h-[450px] bg-[#CE8465] rounded-full opacity-80 z-0 hidden lg:block"></div>
        <svg className="absolute top-[350px] right-[-60px] w-[250px] h-auto opacity-85 z-[2] text-[#4A5B50]" viewBox="0 0 200 400" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M100 400 C100 300, 150 250, 150 150 C150 50, 80 0, 80 0 C80 0, 100 80, 50 120 C0 160, 20 250, 20 250 C20 250, 80 220, 100 400 Z" fill="currentColor" opacity="0.3" />
          <path d="M100 350 C100 280, 180 200, 180 120 C180 40, 120 10, 120 10 C120 10, 140 70, 90 100 C40 130, 60 220, 60 220 C60 220, 90 180, 100 350 Z" fill="currentColor" opacity="0.5" />
        </svg>
      </div>

      {/* Header */}
      <header className="flex items-center justify-between px-6 md:px-12 py-6 max-w-[1440px] mx-auto w-full relative z-10">
        <div className="flex items-center gap-3 font-serif text-2xl font-semibold text-[#1E2A24]">
          <div className="flex items-center justify-center w-8 h-8">

          </div>
          <span>CampaignMaker <span className="text-[#E26A4A] italic font-normal">AI</span></span>
        </div>
        <nav className="hidden md:flex gap-10 text-[15px] font-medium items-center">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M6 9l6 6 6-6" /></svg>
        </nav>
        <div className="flex items-center gap-6">
          {!loading && user ? (
            <>
              <span className="text-[15px] font-medium text-[#1E2A24]">
                Hello, {user.is_guest ? "Guest" : user.username}
              </span>
              <button
                onClick={() => logout()}
                className="text-[15px] font-medium hover:opacity-70 transition-opacity"
              >
                Log out
              </button>
              <Link href="/home" className="bg-[#1E2A24] text-white px-6 py-3 rounded-full text-[15px] font-medium flex items-center gap-2 hover:bg-[#2a3a31] hover:-translate-y-[1px] transition-all">
                Dashboard
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14M12 5l7 7-7 7" /></svg>
              </Link>
            </>
          ) : (
            <>
              <Link href="/auth/login" className="text-[15px] font-medium hover:opacity-70 transition-opacity">Log in</Link>
              <Link href="/auth/signup" className="bg-[#1E2A24] text-white px-6 py-3 rounded-full text-[15px] font-medium flex items-center gap-2 hover:bg-[#2a3a31] hover:-translate-y-[1px] transition-all">
                Get Started
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14M12 5l7 7-7 7" /></svg>
              </Link>
            </>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex flex-col">
        <section className="flex flex-col lg:flex-row justify-between items-center max-w-[1440px] mx-auto w-full px-8 md:px-12 py-16 lg:py-20 relative z-10 min-h-[75vh] gap-20 lg:gap-0">
          <div className="max-w-[580px] flex flex-col items-center lg:items-start text-center lg:text-left animate-slide-up">
            <span className="text-[#E26A4A] text-[13px] font-bold tracking-[2.5px] uppercase mb-6 block">AI-Powered Campaigns</span>
            <h1 className="font-serif text-5xl md:text-6xl lg:text-[76px] leading-[1.05] text-[#1E2A24] mb-6 font-medium">
              Smarter Campaigns,<br />
              <span className="italic text-[#E26A4A] font-normal">Better Results.</span>
            </h1>
            <p className="text-[18px] leading-relaxed text-[#6B726F] mb-10 max-w-[480px]">
              CampaignMaker AI helps you create, optimize, and launch high-performing campaigns in minutes.
            </p>
            <div className="flex flex-row gap-4 mb-12 justify-center">
              <Link href={user ? "/home" : "/auth/signup"} className="bg-[#1E2A24] text-white px-8 py-4 rounded-full text-base font-medium flex items-center gap-2 hover:-translate-y-0.5 hover:shadow-[0_10px_25px_rgba(30,42,36,0.2)] transition-all">
                Start Creating
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14M12 5l7 7-7 7" /></svg>
              </Link>
              {/* <button className="bg-transparent text-[#1E2A24] px-8 py-4 rounded-full text-base font-medium border border-[#dcd7ce] hover:border-[#1E2A24] hover:bg-black/5 transition-all">
                Explore Templates
              </button> */}
            </div>

          </div>
        </section>

        <section className="bg-[#F6F4EB] py-20 px-8 md:px-12 mt-auto relative z-10 border-t border-[#EBE7DC]">
          <div className="max-w-[1200px] mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12 relative">
            <div className="flex gap-4 items-start">
              <div className="w-12 h-12 bg-[#EFECE3] rounded-xl flex items-center justify-center flex-shrink-0 text-[#1E2A24]">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" /></svg>
              </div>
              <div>
                <h3 className="text-[15px] font-semibold mb-2 text-[#1E2A24]">AI-Powered</h3>
                <p className="text-[13px] leading-relaxed text-[#6B726F]">Generate ideas, content, and strategies with the power of AI.</p>
              </div>
            </div>

            <div className="flex gap-4 items-start">
              <div className="w-12 h-12 bg-[#EFECE3] rounded-xl flex items-center justify-center flex-shrink-0 text-[#1E2A24]">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" /><line x1="16" y1="13" x2="8" y2="13" /><line x1="16" y1="17" x2="8" y2="17" /><polyline points="10 9 9 9 8 9" /></svg>
              </div>
              <div>
                <h3 className="text-[15px] font-semibold mb-2 text-[#1E2A24]">Custom Templates</h3>
                <p className="text-[13px] leading-relaxed text-[#6B726F]">Choose from beautiful, customizable templates for every channel.</p>
              </div>
            </div>

            <div className="flex gap-4 items-start">
              <div className="w-12 h-12 bg-[#EFECE3] rounded-xl flex items-center justify-center flex-shrink-0 text-[#1E2A24]">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12" /></svg>
              </div>
              <div>
                <h3 className="text-[15px] font-semibold mb-2 text-[#1E2A24]">Optimize & Improve</h3>
                <p className="text-[13px] leading-relaxed text-[#6B726F]">Get AI-driven insights to optimize performance and maximize results.</p>
              </div>
            </div>

            <div className="flex gap-4 items-start">
              <div className="w-12 h-12 bg-[#EFECE3] rounded-xl flex items-center justify-center flex-shrink-0 text-[#1E2A24]">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" /><circle cx="9" cy="7" r="4" /><path d="M23 21v-2a4 4 0 0 0-3-3.87" /><path d="M16 3.13a4 4 0 0 1 0 7.75" /></svg>
              </div>
              <div>
                <h3 className="text-[15px] font-semibold mb-2 text-[#1E2A24]">Team Collaboration</h3>
                <p className="text-[13px] leading-relaxed text-[#6B726F]">Work together in real-time and bring your best ideas to life.</p>
              </div>
            </div>
          </div>
        </section>

        <div className="flex justify-center items-center py-10 pb-16 bg-[#F6F4EB]">
          <div className="flex-1 max-w-[300px] h-px bg-[#EBE7DC]"></div>
          <div className="px-6 text-[#8C9F90]">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22c-3-5-6-10-6-15a6 6 0 0 1 12 0c0 5-3 10-6 15z" /><path d="M12 2v20" /><path d="M12 12c-2.5 0-4.5-2-4.5-4.5S9.5 3 12 3" /></svg>
          </div>
          <div className="flex-1 max-w-[300px] h-px bg-[#EBE7DC]"></div>
        </div>
      </main>
    </div>
  );
}
