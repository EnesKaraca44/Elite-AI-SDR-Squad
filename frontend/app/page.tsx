"use client";

import React, { useState, useEffect, useRef } from 'react';
import { 
  Search, 
  Cpu, 
  BarChart3, 
  MessageSquare, 
  Activity, 
  Globe, 
  Zap, 
  ShieldCheck,
  ChevronRight,
  Terminal,
  ArrowUpRight
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function Dashboard() {
  const [company, setCompany] = useState('');
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);

  const addLog = (msg: string) => {
    setLogs(prev => [...prev.slice(-10), `> ${msg}`]);
  };

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  const deploySquad = async () => {
    if (!company || !url) return;
    setLoading(true);
    setResult(null);
    setLogs([]);
    
    try {
      const response = await fetch('http://localhost:5000/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ company_name: company, company_url: url })
      });

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) throw new Error("No reader");

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.replace('data: ', ''));
            if (data.log) {
              addLog(data.log);
            }
            if (data.status === 'success') {
              setResult(data.data);
              addLog("Mission Accomplished. Data vault updated.");
            }
            if (data.error) {
              addLog(`ERROR: ${data.error}`);
            }
          }
        }
      }
    } catch (err) {
      addLog("ERROR: Connection to Elite Backend lost.");
    } finally {
      setLoading(false);
    }
  };

  const downloadPDF = () => {
    if (!result?.id) return;
    window.open(`http://localhost:5000/api/export/${result.id}`, '_blank');
  };

  return (
    <div className="min-h-screen bg-[#050505] text-white p-6 md:p-12 font-sans selection:bg-primary selection:text-black">
      {/* Background Decor */}
      <div className="fixed top-0 left-0 w-full h-full pointer-events-none opacity-20 overflow-hidden">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary/20 blur-[120px] rounded-full" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-secondary/20 blur-[120px] rounded-full" />
      </div>

      <header className="relative z-10 flex justify-between items-center mb-12">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-primary glow rounded-lg flex items-center justify-center">
            <Cpu className="text-black w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight">ELITE <span className="text-primary italic">99/10</span></h1>
            <p className="text-xs text-white/40 uppercase tracking-[0.2em]">Multi-Agent Intelligence</p>
          </div>
        </div>
        <div className="hidden md:flex items-center gap-6 text-sm text-white/60">
          <span className="hover:text-primary transition-colors cursor-pointer">Network Status: <span className="text-primary">OPTIMAL</span></span>
          <span className="hover:text-primary transition-colors cursor-pointer">Agent Latency: 42ms</span>
        </div>
      </header>

      <main className="relative z-10 grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Input Panel */}
        <div className="lg:col-span-4 space-y-8">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass p-8 rounded-2xl glow"
          >
            <h2 className="text-lg font-semibold mb-6 flex items-center gap-2">
              <Zap className="w-5 h-5 text-primary" /> Deploy New Operation
            </h2>
            <div className="space-y-4">
              <div>
                <label className="text-xs uppercase tracking-widest text-white/40 mb-2 block">Target Entity</label>
                <input 
                  value={company}
                  onChange={e => setCompany(e.target.value)}
                  placeholder="e.g. Acme Corp"
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 focus:outline-none focus:border-primary/50 transition-all"
                />
              </div>
              <div>
                <label className="text-xs uppercase tracking-widest text-white/40 mb-2 block">Intelligence Source (URL)</label>
                <input 
                  value={url}
                  onChange={e => setUrl(e.target.value)}
                  placeholder="e.g. acme.com"
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 focus:outline-none focus:border-primary/50 transition-all"
                />
              </div>
              <button 
                onClick={deploySquad}
                disabled={loading}
                className="w-full bg-primary text-black font-bold py-4 rounded-xl hover:scale-[1.02] active:scale-[0.98] transition-all flex items-center justify-center gap-3 disabled:opacity-50"
              >
                {loading ? <Activity className="animate-spin" /> : <ChevronRight />}
                {loading ? "SQUAD DEPLOYING..." : "INITIALIZE SQUAD"}
              </button>
            </div>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-black/40 border border-white/5 p-6 rounded-2xl"
          >
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xs font-bold uppercase tracking-widest text-primary flex items-center gap-2">
                <Terminal className="w-4 h-4" /> Live Agent Log
              </h3>
              <div className="flex gap-1">
                <div className="w-2 h-2 rounded-full bg-red-500/50" />
                <div className="w-2 h-2 rounded-full bg-yellow-500/50" />
                <div className="w-2 h-2 rounded-full bg-green-500/50" />
              </div>
            </div>
            <div ref={scrollRef} className="h-40 overflow-y-auto space-y-2 font-mono text-[10px] text-white/40">
              {logs.length === 0 && <span className="italic opacity-30">Waiting for mission initialization...</span>}
              {logs.map((log, i) => (
                <div key={i} className={i === logs.length - 1 ? "text-primary neon-text" : ""}>{log}</div>
              ))}
            </div>
          </motion.div>
        </div>

        {/* Results Panel */}
        <div className="lg:col-span-8">
          <AnimatePresence mode="wait">
            {!result ? (
              <motion.div 
                key="empty"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="h-full min-h-[500px] border border-dashed border-white/10 rounded-2xl flex flex-col items-center justify-center text-white/20"
              >
                <div className="w-20 h-20 mb-6 rounded-full border border-white/5 flex items-center justify-center">
                  <Globe className="w-8 h-8 opacity-20" />
                </div>
                <p className="text-sm tracking-wide">Enter target data to see intelligence</p>
              </motion.div>
            ) : (
              <motion.div 
                key="result"
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                className="space-y-8"
              >
                {/* Metrics Header */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="glass p-6 rounded-2xl">
                    <p className="text-[10px] uppercase tracking-widest text-white/40 mb-1">Lead Probability</p>
                    <div className="flex items-baseline gap-2">
                      <span className="text-4xl font-black text-primary">{result.analysis.financial_score}</span>
                      <span className="text-sm text-white/20">/100</span>
                    </div>
                  </div>
                  <div className="glass p-6 rounded-2xl">
                    <p className="text-[10px] uppercase tracking-widest text-white/40 mb-1">Market Tier</p>
                    <div className="flex items-center gap-2">
                      <ShieldCheck className="w-5 h-5 text-secondary" />
                      <span className="text-xl font-bold tracking-tight">{result.analysis.market_position}</span>
                    </div>
                  </div>
                  <div className="glass p-6 rounded-2xl">
                    <p className="text-[10px] uppercase tracking-widest text-white/40 mb-1">Impact Potential</p>
                    <div className="text-sm font-semibold text-white/80 line-clamp-2">
                      {result.analysis.roi_prediction}
                    </div>
                  </div>
                </div>

                {/* Main Content Tabs */}
                <div className="glass rounded-2xl overflow-hidden">
                  <div className="flex border-b border-white/5 justify-between items-center pr-4">
                    <div className="flex">
                      {['Intelligence', 'News', 'Outreach'].map(tab => (
                        <button key={tab} className="px-8 py-5 text-xs font-bold uppercase tracking-widest hover:bg-white/5 transition-colors border-r border-white/5">{tab}</button>
                      ))}
                    </div>
                    <button 
                      onClick={downloadPDF}
                      className="text-[10px] uppercase tracking-widest bg-primary/10 text-primary border border-primary/20 px-4 py-2 rounded-lg hover:bg-primary hover:text-black transition-all flex items-center gap-2"
                    >
                      <ArrowUpRight className="w-3 h-3" /> Download PDF Report
                    </button>
                  </div>
                  <div className="p-8">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
                      <div>
                        <h4 className="text-xs font-bold uppercase tracking-widest text-white/40 mb-6 flex items-center gap-2">
                          <BarChart3 className="w-4 h-4" /> Strategic Gaps Identified
                        </h4>
                        <div className="space-y-4">
                          {result.analysis.strategic_gaps.map((gap: string, i: number) => (
                            <div key={i} className="flex items-start gap-3 p-4 bg-white/5 rounded-xl border border-white/5 hover:border-primary/20 transition-all">
                              <div className="w-5 h-5 rounded bg-primary/10 flex items-center justify-center text-[10px] font-bold text-primary">{i+1}</div>
                              <span className="text-sm text-white/70">{gap}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                      <div className="space-y-8">
                        <div>
                          <h4 className="text-xs font-bold uppercase tracking-widest text-white/40 mb-6 flex items-center gap-2">
                            <MessageSquare className="w-4 h-4" /> Optimized Outreach
                          </h4>
                          <div className="bg-black/60 p-6 rounded-xl border border-white/10 font-mono text-sm text-white/60 relative group">
                            <div className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
                              <ArrowUpRight className="w-4 h-4 text-primary" />
                            </div>
                            {result.outreach.outreach_drafts}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </main>

      <footer className="relative z-10 mt-20 text-center opacity-20 hover:opacity-100 transition-opacity">
        <p className="text-[10px] uppercase tracking-[0.4em]">Proprietary AI Architecture v4.0.0 | Elite Deployment</p>
      </footer>
    </div>
  );
}
