"use client";

import { useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function SignupPage() {
    const { signup, continueAsGuest } = useAuth();
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
            await signup(username, password);
            router.push("/home"); // redirect to home or dashboard after signup
        } catch (err: any) {
            setError(err.message || "Failed to sign up. Please try again.");
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
        <div className="min-h-screen flex items-center justify-center bg-[#F6F4EB] p-4 relative overflow-hidden">
            {/* Background shapes for subtle premium aesthetic */}
            <div className="absolute top-[-100px] left-[-100px] w-[400px] h-[400px] bg-[#E26A4A] rounded-full opacity-[0.03] blur-[80px] pointer-events-none"></div>
            <div className="absolute bottom-[-50px] right-[-50px] w-[500px] h-[500px] bg-[#A2B6A3] rounded-full opacity-[0.05] blur-[80px] pointer-events-none"></div>

            <div className="w-full max-w-[440px] bg-[#FCFBF8] rounded-3xl p-8 sm:p-12 shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-[#EBE7DC] relative z-10 animate-slide-up">
                {/* Logo/Brand */}
                <div className="flex justify-center mb-8 font-serif text-xl font-semibold text-[#1E2A24]">
                    <Link href="/" className="flex items-center gap-3 cursor-pointer hover:opacity-80 transition-opacity">
                        <div className="flex items-center justify-center w-8 h-8">
                            <svg width="28" height="28" viewBox="0 0 32 32" fill="none">
                                <path d="M16 28C9.37258 28 4 22.6274 4 16C4 9.37258 9.37258 4 16 4C19.3137 4 22.3137 5.34315 24.4853 7.51472L20.2426 11.7574C19.1174 10.6321 17.6321 10 16 10C12.6863 10 10 12.6863 10 16C10 19.3137 12.6863 22 16 22C17.6321 22 19.1174 21.3679 20.2426 20.2426L24.4853 24.4853C22.3137 26.6569 19.3137 28 16 28Z" fill="#1E2A24" />
                                <circle cx="23.5" cy="16" r="4.5" fill="#E26A4A" />
                            </svg>
                        </div>
                        <span>CampaignMaker <span className="text-[#E26A4A] italic font-normal">AI</span></span>
                    </Link>
                </div>

                <div className="text-center mb-8">
                    <h1 className="font-serif text-3xl text-[#1E2A24] mb-2 font-medium">Create Account</h1>
                    <p className="text-[15px] text-[#6B726F]">Enter your details to create a new account.</p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-5">
                    {error && (
                        <div className="p-3 rounded-lg bg-red-50 border border-red-100 text-red-600 text-sm text-center">
                            {error}
                        </div>
                    )}

                    <div className="space-y-1.5 text-left">
                        <label className="text-[14px] font-medium text-[#1E2A24]" htmlFor="username">Username</label>
                        <input
                            id="username"
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            placeholder="Choose a username"
                            required
                            className="w-full px-4 py-3 rounded-xl border border-[#EBE7DC] bg-white text-[#1E2A24] placeholder:text-[#A0A7A3] focus:outline-none focus:ring-2 focus:ring-[#E26A4A] focus:border-transparent transition-all"
                        />
                    </div>

                    <div className="space-y-1.5 text-left">
                        <label className="text-[14px] font-medium text-[#1E2A24]" htmlFor="password">Password</label>
                        <input
                            id="password"
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="Choose a password"
                            required
                            className="w-full px-4 py-3 rounded-xl border border-[#EBE7DC] bg-white text-[#1E2A24] placeholder:text-[#A0A7A3] focus:outline-none focus:ring-2 focus:ring-[#E26A4A] focus:border-transparent transition-all"
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={isLoading}
                        className="w-full bg-[#1E2A24] text-white py-3.5 mt-2 rounded-full text-[15px] font-medium hover:bg-[#2a3a31] hover:-translate-y-[1px] transition-all disabled:opacity-70 disabled:hover:translate-y-0"
                    >
                        {isLoading ? "Signing up..." : "Sign up"}
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
                        className="w-full bg-white border border-[#EBE7DC] text-[#1E2A24] py-3.5 rounded-full text-[15px] font-medium hover:bg-[#F6F4EB] transition-all flex justify-center items-center gap-2"
                    >
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" /><circle cx="12" cy="7" r="4" /></svg>
                        Continue as Guest
                    </button>
                    <p className="text-[14px] text-[#6B726F] pt-2">
                        Already have an account? <Link href="/auth/login" className="font-medium text-[#1E2A24] hover:text-[#E26A4A] transition-colors">Log in</Link>
                    </p>
                </div>
            </div>
        </div>
    );
}
