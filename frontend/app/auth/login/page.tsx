"use client";

import { useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function LoginPage() {
    const { login, continueAsGuest } = useAuth();
    const router = useRouter();

    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setIsLoading(true);

        try {
            await login(username, password);
            router.push("/"); // redirect to home or dashboard after login
        } catch (err: any) {
            setError(err.message || "Failed to log in. Please try again.");
        } finally {
            setIsLoading(false);
        }
    };

    const handleGuest = async () => {
        setError(null);
        setIsLoading(true);
        try {
            await continueAsGuest();
            router.push("/"); // redirect to home or dashboard
        } catch (err: any) {
            setError(err.message || "Failed to log in as guest.");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex">
            {/* Left Column: Form */}
            <div className="flex-1 flex flex-col justify-center px-8 md:px-16 lg:px-24 xl:px-32 relative bg-[#FCFBF8]">
                {/* Logo/Brand */}
                <div className="absolute top-8 left-8 md:top-12 md:left-12 flex items-center gap-3 font-serif text-xl font-semibold text-[#1E2A24]">
                    <Link href="/" className="flex items-center gap-3 cursor-pointer">
                        <div className="flex items-center justify-center w-8 h-8">
                            <svg width="28" height="28" viewBox="0 0 32 32" fill="none">
                                <path d="M16 28C9.37258 28 4 22.6274 4 16C4 9.37258 9.37258 4 16 4C19.3137 4 22.3137 5.34315 24.4853 7.51472L20.2426 11.7574C19.1174 10.6321 17.6321 10 16 10C12.6863 10 10 12.6863 10 16C10 19.3137 12.6863 22 16 22C17.6321 22 19.1174 21.3679 20.2426 20.2426L24.4853 24.4853C22.3137 26.6569 19.3137 28 16 28Z" fill="#1E2A24" />
                                <circle cx="23.5" cy="16" r="4.5" fill="#E26A4A" />
                            </svg>
                        </div>
                        <span>CampaignMaker <span className="text-[#E26A4A] italic font-normal">AI</span></span>
                    </Link>
                </div>

                <div className="max-w-[400px] w-full mx-auto animate-slide-up">
                    <h1 className="font-serif text-4xl text-[#1E2A24] mb-2 font-medium">Welcome back</h1>
                    <p className="text-[15px] text-[#6B726F] mb-8">Enter your details to access your account.</p>

                    <form onSubmit={handleSubmit} className="space-y-5">
                        {error && (
                            <div className="p-3 rounded-lg bg-red-50 border border-red-100 text-red-600 text-sm">
                                {error}
                            </div>
                        )}

                        <div className="space-y-1.5">
                            <label className="text-[14px] font-medium text-[#1E2A24]" htmlFor="username">Username</label>
                            <input
                                id="username"
                                type="text"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                placeholder="Enter your username"
                                required
                                className="w-full px-4 py-3 rounded-xl border border-[#EBE7DC] bg-white text-[#1E2A24] placeholder:text-[#A0A7A3] focus:outline-none focus:ring-2 focus:ring-[#E26A4A] focus:border-transparent transition-all"
                            />
                        </div>

                        <div className="space-y-1.5">
                            <label className="text-[14px] font-medium text-[#1E2A24]" htmlFor="password">Password</label>
                            <input
                                id="password"
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                placeholder="Enter your password"
                                required
                                className="w-full px-4 py-3 rounded-xl border border-[#EBE7DC] bg-white text-[#1E2A24] placeholder:text-[#A0A7A3] focus:outline-none focus:ring-2 focus:ring-[#E26A4A] focus:border-transparent transition-all"
                            />
                        </div>

                        <div className="flex items-center justify-between text-[13px] pt-1">
                            <label className="flex items-center gap-2 cursor-pointer">
                                <input type="checkbox" className="rounded border-[#EBE7DC] text-[#E26A4A] focus:ring-[#E26A4A]" />
                                <span className="text-[#6B726F]">Remember me</span>
                            </label>
                            <a href="#" className="font-medium text-[#1E2A24] hover:text-[#E26A4A] transition-colors">Forgot password?</a>
                        </div>

                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full bg-[#1E2A24] text-white py-3.5 rounded-full text-[15px] font-medium hover:bg-[#2a3a31] hover:-translate-y-[1px] transition-all disabled:opacity-70 disabled:hover:translate-y-0"
                        >
                            {isLoading ? "Signing in..." : "Sign in"}
                        </button>
                    </form>

                    <div className="mt-8 relative">
                        <div className="absolute inset-0 flex items-center">
                            <div className="w-full border-t border-[#EBE7DC]"></div>
                        </div>
                        <div className="relative flex justify-center text-[13px]">
                            <span className="bg-[#FCFBF8] px-4 text-[#8C9F90]">or</span>
                        </div>
                    </div>

                    <div className="mt-8 text-center space-y-4">
                        <button
                            onClick={handleGuest}
                            disabled={isLoading}
                            className="w-full bg-white border border-[#EBE7DC] text-[#1E2A24] py-3.5 rounded-full text-[15px] font-medium hover:bg-black/5 transition-all flex justify-center items-center gap-2"
                        >
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" /><circle cx="12" cy="7" r="4" /></svg>
                            Continue as Guest
                        </button>
                        <p className="text-[14px] text-[#6B726F]">
                            Don't have an account? <Link href="/auth/signup" className="font-medium text-[#1E2A24] hover:text-[#E26A4A] transition-colors">Sign up</Link>
                        </p>
                    </div>
                </div>
            </div>

            {/* Right Column: Decorative */}
            <div className="hidden lg:flex flex-1 bg-[#1E2A24] relative overflow-hidden items-center justify-center p-12">
                {/* Abstract shapes inside right column */}
                <div className="absolute top-[-100px] right-[-50px] w-[600px] h-[600px] bg-[#2a3a31] rounded-full opacity-50 blur-[40px]"></div>
                <div className="absolute bottom-[-150px] left-[-100px] w-[500px] h-[500px] bg-[#E26A4A] rounded-full opacity-20 blur-[80px]"></div>
                <div className="absolute top-[20%] left-[20%] w-[300px] h-[300px] bg-[#A2B6A3] rounded-full opacity-20 blur-[60px]"></div>

                <div className="relative z-10 max-w-[500px] text-white animate-slide-up" style={{ animationDelay: '0.2s' }}>
                    <span className="text-[#A2B6A3] text-[13px] font-bold tracking-[2.5px] uppercase mb-6 block">Unlock the power</span>
                    <h2 className="font-serif text-5xl leading-[1.1] mb-6">
                        Create high-performing campaigns <span className="italic text-[#E26A4A] font-normal">in minutes.</span>
                    </h2>
                    <p className="text-[16px] leading-relaxed text-[#A0A7A3]">
                        Join thousands of marketers using CampaignMaker AI to generate ideas, optimize content, and maximize results.
                    </p>

                    <div className="mt-12 flex items-center gap-4">
                        <div className="flex -space-x-3">
                            <div className="w-10 h-10 rounded-full border-2 border-[#1E2A24] bg-cover bg-center" style={{ backgroundImage: 'url("https://i.pravatar.cc/100?img=11")' }}></div>
                            <div className="w-10 h-10 rounded-full border-2 border-[#1E2A24] bg-cover bg-center" style={{ backgroundImage: 'url("https://i.pravatar.cc/100?img=12")' }}></div>
                            <div className="w-10 h-10 rounded-full border-2 border-[#1E2A24] bg-cover bg-center" style={{ backgroundImage: 'url("https://i.pravatar.cc/100?img=13")' }}></div>
                        </div>
                        <div className="text-sm font-medium text-white">Loved by 2,000+ users</div>
                    </div>
                </div>
            </div>
        </div>
    );
}
