import React, { useState, useEffect, useRef, useCallback } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
  PieChart, Pie, Cell, RadialBarChart, RadialBar
} from 'recharts';
import { 
  Zap, MessageSquare, Settings, Activity, Leaf, Upload, FileText, Download, 
  CheckCircle, AlertCircle, TrendingDown, Clock, DollarSign, BarChart3, Target
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';

const API_BASE = 'http://127.0.0.1:5000/api';

const ENERGY_TIPS = [
  { tip: "Schedule heavy machinery during off-peak hours (10PM-6AM) to reduce demand charges by up to 15%.", category: "Scheduling" },
  { tip: "Install Variable Frequency Drives (VFDs) on motors to reduce machine energy use by 20-30%.", category: "Equipment" },
  { tip: "Replace old fluorescent lighting with LED — saves 40-60% on base load lighting costs.", category: "Lighting" },
  { tip: "Set AC to 24-25°C instead of 20°C. Each degree saves ~6% on cooling energy.", category: "HVAC" },
  { tip: "Implement auto power-off for computers and monitors during non-working hours.", category: "Automation" },
  { tip: "Regular maintenance of machines prevents efficiency loss of up to 15% annually.", category: "Maintenance" },
];

const PIE_COLORS = ['#3b82f6', '#f59e0b', '#a78bfa'];

const Dashboard = () => {
  const [activeTab, setActiveTab] = useState('input');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Unified Input Data
  const [inputData, setInputData] = useState({
    businessName: 'Tech Manufacturing Corp',
    employees: 10,
    workingDays: 22,
    workingHours: 9,
    machines: 5,
    machineRuntime: 8,
    monthlyUnits: 700,
    costPerUnit: 8
  });

  // Scenario Adjustments
  const [scenario, setScenario] = useState({ reduceHours: 0, reduceRuntime: 0 });

  // Simulation Results
  const [simulation, setSimulation] = useState(null);
  const [simulationHistory, setSimulationHistory] = useState([]);

  // Upload state
  const [uploadFile, setUploadFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [uploadError, setUploadError] = useState(null);
  const [dragging, setDragging] = useState(false);

  // Carbon Report
  const [generatingReport, setGeneratingReport] = useState(false);

  // Analytics
  const [forecast, setForecast] = useState(null);
  const [benchmark, setBenchmark] = useState(null);
  const [roiData, setRoiData] = useState(null);
  const [analyticsLoading, setAnalyticsLoading] = useState(false);

  // AI Chat
  const [chatQuery, setChatQuery] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setInputData(prev => ({ ...prev, [name]: value }));
  };

  const handleScenarioChange = (e) => {
    const { name, value } = e.target;
    setScenario(prev => ({ ...prev, [name]: Number(value) }));
  };

  const runSimulation = async (e) => {
    if (e) e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await axios.post(`${API_BASE}/simulate-unified`, {
        input: inputData,
        scenario: scenario
      });
      setSimulation(res.data);
      // Track history
      setSimulationHistory(prev => [...prev, {
        id: Date.now(),
        timestamp: new Date().toLocaleTimeString(),
        runtime: scenario.reduceRuntime,
        hours: scenario.reduceHours,
        savings: res.data.simulated.savings,
        score: res.data.simulated.score
      }].slice(-10));
      setActiveTab('dashboard');

      // Pre-fetch analytics in background
      fetchAnalytics(res.data);
    } catch (err) {
      setError("Simulation failed. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  const handleChat = async (e) => {
    e.preventDefault();
    if (!chatQuery.trim()) return;
    const userMsg = { role: 'user', content: chatQuery };
    const currentQuery = chatQuery;
    setChatHistory(prev => [...prev, userMsg]);
    setChatQuery('');
    try {
      const res = await axios.post(`${API_BASE}/chat`, {
        query: currentQuery,
        history: chatHistory,
        context: simulation
      });
      setChatHistory(prev => [...prev, { role: 'assistant', content: res.data.response }]);
    } catch {
      setChatHistory(prev => [...prev, { role: 'assistant', content: "AI Connection Error. Check your GROQ_API_KEY." }]);
    }
  };

  // ─── UPLOAD HANDLERS ────────────────────────────────────────────────────────
  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) { setUploadFile(file); setUploadResult(null); setUploadError(null); }
  }, []);

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) { setUploadFile(file); setUploadResult(null); setUploadError(null); }
  };

  const handleAnalyzeUpload = async () => {
    if (!uploadFile) return;
    setUploading(true);
    setUploadError(null);
    const formData = new FormData();
    formData.append('file', uploadFile);
    try {
      const res = await axios.post(`${API_BASE}/analyze-upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setUploadResult(res.data);
      if (res.data.prefill) {
        setInputData(prev => ({
          ...prev,
          monthlyUnits: res.data.prefill.monthlyUnits || prev.monthlyUnits,
          costPerUnit: res.data.prefill.costPerUnit || prev.costPerUnit
        }));
      }
    } catch (err) {
      setUploadError(err.response?.data?.error || "Failed to analyze file.");
    } finally {
      setUploading(false);
    }
  };

  // ─── CARBON REPORT HANDLER ─────────────────────────────────────────────────
  const handleDownloadReport = async () => {
    if (!simulation) return;
    setGeneratingReport(true);
    try {
      const res = await axios.post(`${API_BASE}/generate-carbon-report`, {
        baseline: simulation.baseline,
        simulated: simulation.simulated,
        scenario: scenario,
        business_name: inputData.businessName
      }, { responseType: 'blob' });

      const url = window.URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Carbon_Report_${inputData.businessName.replace(/\s/g, '_')}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch {
      alert("Report generation failed. Ensure the backend is running with fpdf2 installed.");
    } finally {
      setGeneratingReport(false);
    }
  };

  // ─── ANALYTICS FETCHER ──────────────────────────────────────────────────────
  const fetchAnalytics = async (simData) => {
    const sim = simData || simulation;
    if (!sim) return;
    setAnalyticsLoading(true);
    try {
      const [forecastRes, benchRes, roiRes] = await Promise.all([
        axios.post(`${API_BASE}/predict-costs`, {
          baseline_bill: sim.baseline.bill,
          simulated_bill: sim.simulated.bill,
          months: 6,
          inflation_rate: 0.05
        }),
        axios.post(`${API_BASE}/benchmark`, {
          monthly_units: sim.baseline.units,
          employees: Number(inputData.employees),
          industry: 'manufacturing'
        }),
        axios.post(`${API_BASE}/calculate-roi`, {
          monthly_savings: sim.simulated.savings
        })
      ]);
      setForecast(forecastRes.data);
      setBenchmark(benchRes.data);
      setRoiData(roiRes.data);
    } catch (e) {
      console.error('Analytics error:', e);
    } finally {
      setAnalyticsLoading(false);
    }
  };

  // ─── STYLES ────────────────────────────────────────────────────────────────
  const inputStyle = {
    width: '100%', background: 'rgba(255,255,255,0.05)',
    border: '1px solid rgba(255,255,255,0.1)', padding: '0.75rem',
    borderRadius: '0.75rem', color: 'white', outline: 'none', fontSize: '0.95rem'
  };

  const cardStyle = {
    background: 'rgba(15,23,42,0.6)',
    border: '1px solid rgba(255,255,255,0.08)',
    borderRadius: '24px',
    padding: '1.5rem'
  };

  // ─── PIE DATA ──────────────────────────────────────────────────────────────
  const getPieData = () => {
    if (!simulation?.baseline?.breakdown) return [];
    const b = simulation.baseline.breakdown;
    return [
      { name: 'Base Load', value: b.base },
      { name: 'Machine Load', value: b.machine },
      { name: 'Operational', value: b.operational },
    ];
  };

  return (
    <div className="min-h-screen text-white p-4">
      {/* Top Navigation */}
      <nav className="top-nav">
        <div className="logo cursor-pointer font-bold text-2xl tracking-tighter" style={{ textShadow: '0 0 15px rgba(0,242,255,0.6)' }}>
          <Zap size={22} style={{ display: 'inline', marginRight: '0.3rem', color: '#00f2ff' }} />
          AI Energy Simulator
        </div>
        <div className="nav-links flex gap-1">
          {[
            { id: 'input', label: 'Simulation', icon: <Settings size={16} /> },
            { id: 'upload', label: 'Upload', icon: <Upload size={16} /> },
            { id: 'dashboard', label: 'Dashboard', icon: <Activity size={16} />, disabled: !simulation },
            { id: 'analytics', label: 'Analytics', icon: <Target size={16} />, disabled: !simulation },
            { id: 'chat', label: 'AI Advisor', icon: <MessageSquare size={16} />, disabled: !simulation },
          ].map(({ id, label, icon, disabled }) => (
            <button
              key={id}
              className={`nav-item ${activeTab === id ? 'px-3 py-2 bg-white/10 rounded-full' : 'px-3 py-2'}`}
              onClick={() => !disabled && setActiveTab(id)}
              disabled={disabled}
              style={{ opacity: disabled ? 0.4 : 1, cursor: disabled ? 'not-allowed' : 'pointer', display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.875rem' }}
            >
              {icon} {label}
            </button>
          ))}
        </div>
      </nav>

      <AnimatePresence mode="wait">

        {/* ═══════════════════ INPUT TAB ═══════════════════════════════════════ */}
        {activeTab === 'input' && (
          <motion.div key="input" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} className="max-w-5xl mx-auto mt-10">
            <div className="text-center mb-10">
              <h2 className="text-4xl font-black mb-4" style={{ background: 'linear-gradient(90deg, #60a5fa, #a78bfa)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                Multi-Factor Simulation Engine
              </h2>
              <p className="text-gray-400">Enter operational data. The Digital Twin computes Base + Machine + Operational load independently.</p>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', marginBottom: '2rem' }}>
              {/* Business Details */}
              <div style={cardStyle}>
                <h3 style={{ marginBottom: '1.5rem', color: '#60a5fa', fontWeight: 'bold', fontSize: '1.1rem' }}>🏢 Business Details</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  {[
                    { label: 'Business Name', name: 'businessName', type: 'text' },
                    { label: 'Employees', name: 'employees', type: 'number' },
                    { label: 'Working Days / Month', name: 'workingDays', type: 'number' },
                    { label: 'Working Hours / Day', name: 'workingHours', type: 'number' }
                  ].map(f => (
                    <div key={f.name}>
                      <label style={{ color: '#9ca3af', fontSize: '0.85rem', display: 'block', marginBottom: '0.25rem' }}>{f.label}</label>
                      <input type={f.type} name={f.name} value={inputData[f.name]} onChange={handleInputChange} style={inputStyle} />
                    </div>
                  ))}
                </div>
              </div>

              {/* Equipment */}
              <div style={cardStyle}>
                <h3 style={{ marginBottom: '1.5rem', color: '#60a5fa', fontWeight: 'bold', fontSize: '1.1rem' }}>⚙️ Equipment & Load</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  {[
                    { label: 'Heavy Machines', name: 'machines', type: 'number' },
                    { label: 'Machine Runtime (hrs/day)', name: 'machineRuntime', type: 'number' },
                    { label: 'Monthly Units (kWh)', name: 'monthlyUnits', type: 'number' },
                    { label: 'Cost per Unit (₹/$)', name: 'costPerUnit', type: 'number' }
                  ].map(f => (
                    <div key={f.name}>
                      <label style={{ color: '#9ca3af', fontSize: '0.85rem', display: 'block', marginBottom: '0.25rem' }}>{f.label}</label>
                      <input type={f.type} name={f.name} value={inputData[f.name]} onChange={handleInputChange} style={inputStyle} />
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Scenario Sliders */}
            <div style={{ background: 'linear-gradient(145deg, rgba(30, 64, 175, 0.2), rgba(15,23,42,0.8))', border: '1px solid rgba(59,130,246,0.3)', borderRadius: '24px', padding: '2rem', marginBottom: '2rem' }}>
              <h3 style={{ marginBottom: '1rem', color: '#93c5fd', fontWeight: 'bold', fontSize: '1.1rem' }}><Leaf size={18} style={{ display: 'inline', marginRight: '0.5rem' }} />What-If Scenario Optimizer</h3>
              <p style={{ color: '#9ca3af', fontSize: '0.85rem', marginBottom: '1.5rem' }}>Drag sliders to simulate how targeted changes reduce each energy component independently.</p>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
                {[
                  { label: '⚙️ Reduce Machine Runtime', name: 'reduceRuntime', max: 100, unit: '%', value: scenario.reduceRuntime, desc: 'Affects Machine Load only' },
                  { label: '🕐 Decrease Operating Hours', name: 'reduceHours', max: 8, unit: 'hrs', value: scenario.reduceHours, desc: 'Affects Base + Operational Load' }
                ].map(s => (
                  <div key={s.name}>
                    <label style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.3rem' }}>
                      <span style={{ color: '#d1d5db', fontSize: '0.9rem' }}>{s.label}</span>
                      <span style={{ color: '#60a5fa', fontWeight: 'bold' }}>{s.value}{s.unit}</span>
                    </label>
                    <input type="range" min="0" max={s.max} name={s.name} value={s.value} onChange={handleScenarioChange} style={{ width: '100%', accentColor: '#3b82f6' }} />
                    <p style={{ color: '#6b7280', fontSize: '0.75rem', marginTop: '0.25rem' }}>{s.desc}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Formula Preview */}
            <div style={{ background: 'rgba(0,0,0,0.3)', borderRadius: '12px', padding: '1rem 1.5rem', marginBottom: '2rem', fontFamily: 'monospace', fontSize: '0.8rem', color: '#a3e635', border: '1px solid rgba(163,230,53,0.2)' }}>
              <span style={{ color: '#9ca3af' }}>Formula: </span>
              Total = (<span style={{ color: '#60a5fa' }}>{inputData.employees}emp × {inputData.workingHours}hr × 0.5</span>) + 
              (<span style={{ color: '#f59e0b' }}>{inputData.machines}mach × {inputData.machineRuntime}hr × 2.0kW</span>) + 
              (<span style={{ color: '#a78bfa' }}>{inputData.workingHours}hr × 1.8</span>) × {inputData.workingDays} days
            </div>

            {error && <div style={{ color: '#f87171', textAlign: 'center', marginBottom: '1rem' }}>{error}</div>}

            <div style={{ display: 'flex', justifyContent: 'center', paddingBottom: '5rem' }}>
              <button onClick={runSimulation} className="btn-premium" style={{ width: '320px', height: '60px', borderRadius: '30px', fontSize: '1.1rem' }} disabled={loading}>
                {loading ? '⚙️ Computing Digital Twin...' : '🚀 Run Simulation'}
              </button>
            </div>
          </motion.div>
        )}

        {/* ═══════════════════ UPLOAD TAB ══════════════════════════════════════ */}
        {activeTab === 'upload' && (
          <motion.div key="upload" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} className="max-w-3xl mx-auto mt-10">
            <div className="text-center mb-10">
              <h2 className="text-4xl font-black mb-4">📂 Upload Electricity Bills</h2>
              <p className="text-gray-400" style={{ fontStyle: 'italic' }}>"Since smart meter APIs are not publicly available, our system uses historical usage data uploads to perform analysis and simulation."</p>
            </div>

            {/* Drop Zone */}
            <div
              onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
              onDragLeave={() => setDragging(false)}
              onDrop={handleDrop}
              onClick={() => document.getElementById('file-input').click()}
              style={{
                border: `2px dashed ${dragging ? '#60a5fa' : 'rgba(255,255,255,0.15)'}`,
                borderRadius: '24px', padding: '4rem 2rem', textAlign: 'center', cursor: 'pointer',
                background: dragging ? 'rgba(59,130,246,0.05)' : 'rgba(15,23,42,0.4)',
                transition: 'all 0.3s ease', marginBottom: '2rem'
              }}
            >
              <input id="file-input" type="file" accept=".csv,.xlsx,.xls" style={{ display: 'none' }} onChange={handleFileSelect} />
              <Upload size={48} style={{ margin: '0 auto 1rem', color: '#60a5fa' }} />
              {uploadFile ? (
                <p style={{ color: '#a3e635', fontWeight: 'bold', fontSize: '1.1rem' }}>✅ {uploadFile.name}</p>
              ) : (
                <>
                  <p style={{ color: 'white', fontSize: '1.1rem', marginBottom: '0.5rem' }}>Drag & drop your monthly electricity bill</p>
                  <p style={{ color: '#9ca3af', fontSize: '0.875rem' }}>CSV (.csv)  ·  Excel (.xlsx, .xls)</p>
                </>
              )}
            </div>

            {/* Format Info */}
            <div style={{ ...cardStyle, marginBottom: '2rem' }}>
              <h4 style={{ color: '#93c5fd', marginBottom: '0.75rem', fontWeight: 'bold' }}>📋 Expected File Format</h4>
              <div style={{ background: 'rgba(0,0,0,0.3)', padding: '0.75rem', borderRadius: '8px', fontFamily: 'monospace', fontSize: '0.8rem', color: '#a3e635' }}>
                date | units_kwh | cost<br />
                2024-01 | 850.5 | 6804<br />
                2024-02 | 720.0 | 5760
              </div>
              <p style={{ color: '#6b7280', fontSize: '0.8rem', marginTop: '0.5rem' }}>Auto-detects columns: "consumption", "kwh", "bill", "amount", etc.</p>
            </div>

            {uploadError && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#f87171', background: 'rgba(239,68,68,0.1)', padding: '1rem', borderRadius: '12px', marginBottom: '1rem' }}>
                <AlertCircle size={18} /> {uploadError}
              </div>
            )}

            {uploadResult && (
              <div style={{ background: 'rgba(6,78,59,0.2)', border: '1px solid rgba(16,185,129,0.3)', borderRadius: '16px', padding: '1.5rem', marginBottom: '2rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#34d399', fontWeight: 'bold', marginBottom: '1rem' }}>
                  <CheckCircle size={20} /> Analysis Complete — Form Pre-filled!
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem' }}>
                  {[
                    { label: 'Rows Detected', value: uploadResult.rows_detected },
                    { label: 'Avg Monthly Units', value: `${uploadResult.avg_monthly_units} kWh` },
                    { label: 'Max Month', value: `${uploadResult.max_units} kWh` },
                    { label: 'Min Month', value: `${uploadResult.min_units} kWh` },
                    { label: 'Avg Cost/Unit', value: `₹${uploadResult.avg_cost_per_unit}` },
                    { label: 'Trend', value: uploadResult.consumption_trend || 'stable' },
                  ].map(({ label, value }) => (
                    <div key={label} style={{ background: 'rgba(0,0,0,0.2)', padding: '0.75rem', borderRadius: '10px' }}>
                      <div style={{ color: '#6b7280', fontSize: '0.75rem' }}>{label}</div>
                      <div style={{ color: 'white', fontWeight: 'bold', fontSize: '1.05rem' }}>{value}</div>
                    </div>
                  ))}
                </div>
                <button onClick={() => setActiveTab('input')} style={{ marginTop: '1.5rem', padding: '0.75rem 2rem', background: '#2563eb', borderRadius: '0.75rem', border: 'none', color: 'white', fontWeight: 'bold', cursor: 'pointer' }}>
                  → Continue to Simulation
                </button>
              </div>
            )}

            <div style={{ display: 'flex', justifyContent: 'center' }}>
              <button onClick={handleAnalyzeUpload} disabled={!uploadFile || uploading} className="btn-premium" style={{ width: '280px', height: '55px', borderRadius: '28px', opacity: (!uploadFile || uploading) ? 0.5 : 1 }}>
                {uploading ? '🔍 Analyzing...' : '📊 Analyze Upload'}
              </button>
            </div>
          </motion.div>
        )}

        {/* ═══════════════════ DASHBOARD TAB ═══════════════════════════════════ */}
        {activeTab === 'dashboard' && simulation && (
          <motion.div key="dashboard" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} style={{ maxWidth: '1200px', margin: '0 auto', marginTop: '2rem' }}>

            {/* KPI Row */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1.25rem', marginBottom: '1.5rem' }}>
              {[
                { label: 'Baseline Cost', value: `₹${simulation.baseline.bill.toLocaleString()}`, sub: `${simulation.baseline.units.toLocaleString()} kWh`, icon: <DollarSign size={18} />, color: '#94a3b8' },
                { label: 'Simulated Cost', value: `₹${simulation.simulated.bill.toLocaleString()}`, sub: `${simulation.simulated.units.toLocaleString()} kWh`, icon: <TrendingDown size={18} />, color: '#34d399' },
                { label: 'Monthly Savings', value: `₹${simulation.simulated.savings.toLocaleString()}`, sub: `₹${(simulation.simulated.savings * 12).toLocaleString()}/yr`, icon: <Leaf size={18} />, color: '#34d399' },
                { label: 'Efficiency Score', value: `${simulation.simulated.score}/100`, sub: 'Digital Twin Rating', icon: <Zap size={18} />, color: '#60a5fa' },
              ].map(({ label, value, sub, icon, color }) => (
                <motion.div key={label} whileHover={{ scale: 1.02 }} style={{ ...cardStyle, padding: '1.25rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                    <span style={{ color: '#9ca3af', fontSize: '0.8rem' }}>{label}</span>
                    <span style={{ color }}>{icon}</span>
                  </div>
                  <div style={{ fontSize: '1.75rem', fontWeight: 'bold', color }}>{value}</div>
                  <div style={{ color: '#64748b', fontSize: '0.75rem', marginTop: '0.15rem' }}>{sub}</div>
                </motion.div>
              ))}
            </div>

            {/* Charts Row */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1.25rem', marginBottom: '1.5rem' }}>
              {/* Bar Chart — Total */}
              <div style={cardStyle}>
                <h3 style={{ fontWeight: 'bold', marginBottom: '0.75rem', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}><BarChart3 size={16} /> Total Comparison</h3>
                <div style={{ height: '200px' }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={simulation.chart_data}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" vertical={false} />
                      <XAxis dataKey="name" stroke="rgba(255,255,255,0.5)" fontSize={12} />
                      <YAxis stroke="rgba(255,255,255,0.5)" fontSize={11} />
                      <Tooltip contentStyle={{ background: 'rgba(15,23,42,0.95)', border: '1px solid rgba(255,255,255,0.15)', borderRadius: '10px', fontSize: '0.85rem' }} />
                      <Bar dataKey="Units" fill="#3b82f6" radius={[6,6,0,0]} />
                      <Bar dataKey="Cost" fill="#10b981" radius={[6,6,0,0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Horizontal Bar — Component Breakdown */}
              {simulation.breakdown_chart && (
                <div style={cardStyle}>
                  <h3 style={{ fontWeight: 'bold', marginBottom: '0.75rem', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}><Zap size={16} /> Load Breakdown</h3>
                  <div style={{ height: '200px' }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={simulation.breakdown_chart} layout="vertical">
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" horizontal={false} />
                        <XAxis type="number" stroke="rgba(255,255,255,0.5)" fontSize={11} />
                        <YAxis dataKey="component" type="category" stroke="rgba(255,255,255,0.5)" width={88} fontSize={11} />
                        <Tooltip contentStyle={{ background: 'rgba(15,23,42,0.95)', border: '1px solid rgba(255,255,255,0.15)', borderRadius: '10px', fontSize: '0.85rem' }} />
                        <Legend />
                        <Bar dataKey="Baseline" fill="#f59e0b" radius={[0,4,4,0]} />
                        <Bar dataKey="Simulated" fill="#10b981" radius={[0,4,4,0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              )}

              {/* Pie Chart — Load Distribution */}
              <div style={cardStyle}>
                <h3 style={{ fontWeight: 'bold', marginBottom: '0.75rem', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}><Activity size={16} /> Load Distribution</h3>
                <div style={{ height: '200px' }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie data={getPieData()} cx="50%" cy="50%" innerRadius={50} outerRadius={75} paddingAngle={4} dataKey="value"
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                        labelLine={false}
                      >
                        {getPieData().map((_, i) => (
                          <Cell key={i} fill={PIE_COLORS[i]} />
                        ))}
                      </Pie>
                      <Tooltip contentStyle={{ background: 'rgba(15,23,42,0.95)', border: '1px solid rgba(255,255,255,0.15)', borderRadius: '10px' }} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            {/* Verdict + Reduction Bars + Report */}
            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1.25rem', marginBottom: '1.5rem' }}>
              {/* Left: Reductions + Carbon + Auto-Insight */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>

                {/* Auto-Insight Banner */}
                {simulation.auto_insight && (
                  <div style={{ background: 'linear-gradient(135deg, rgba(88,28,135,0.25), rgba(30,58,138,0.25))', border: '1px solid rgba(139,92,246,0.3)', borderRadius: '16px', padding: '1.25rem 1.5rem', display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>
                    <div style={{ fontSize: '1.5rem', flexShrink: 0 }}>🤖</div>
                    <div>
                      <div style={{ color: '#c4b5fd', fontWeight: 'bold', fontSize: '0.85rem', marginBottom: '0.25rem' }}>AI Engine Insight</div>
                      <div style={{ color: '#e2e8f0', fontSize: '0.88rem', lineHeight: '1.6' }}>{simulation.auto_insight}</div>
                    </div>
                  </div>
                )}

                {/* Component Reduction Progress Bars */}
                {simulation.simulated.reductions && (
                  <div style={cardStyle}>
                    <h3 style={{ fontWeight: 'bold', marginBottom: '1rem', fontSize: '0.9rem' }}>📊 Per-Component Impact</h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                      {[
                        { label: '⚙️ Machine Load', key: 'machine_pct', color: '#f59e0b' },
                        { label: '💡 Base Load', key: 'base_pct', color: '#60a5fa' },
                        { label: '❄️ Operational', key: 'operational_pct', color: '#a78bfa' },
                      ].map(({ label, key, color }) => (
                        <div key={key}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.3rem' }}>
                            <span style={{ color: '#d1d5db', fontSize: '0.85rem' }}>{label}</span>
                            <span style={{ color, fontWeight: 'bold', fontSize: '0.85rem' }}>{simulation.simulated.reductions[key]}% reduction</span>
                          </div>
                          <div style={{ height: '8px', background: 'rgba(255,255,255,0.08)', borderRadius: '4px', overflow: 'hidden' }}>
                            <motion.div initial={{ width: 0 }} animate={{ width: `${Math.min(simulation.simulated.reductions[key], 100)}%` }} transition={{ duration: 0.8, ease: 'easeOut' }}
                              style={{ height: '8px', background: `linear-gradient(90deg, ${color}, ${color}88)`, borderRadius: '4px' }} />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Carbon Impact */}
                <div style={{ ...cardStyle, background: 'rgba(6,78,59,0.15)', border: '1px solid rgba(34,197,94,0.2)' }}>
                  <h3 style={{ fontWeight: 'bold', marginBottom: '0.75rem', fontSize: '0.9rem', color: '#86efac' }}>🌿 Environmental Impact</h3>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0.75rem' }}>
                    {[
                      { label: 'CO₂ Saved/Month', value: `${Math.round((simulation.baseline.units - simulation.simulated.units) * 0.82)} kg` },
                      { label: 'CO₂ Saved/Year', value: `${Math.round((simulation.baseline.units - simulation.simulated.units) * 0.82 * 12)} kg` },
                      { label: 'Trees Equivalent', value: `${Math.round((simulation.baseline.units - simulation.simulated.units) * 0.82 * 12 / 21.77)} trees` },
                    ].map(({ label, value }) => (
                      <div key={label} style={{ background: 'rgba(0,0,0,0.2)', padding: '0.75rem', borderRadius: '10px', textAlign: 'center' }}>
                        <div style={{ color: '#6b7280', fontSize: '0.7rem' }}>{label}</div>
                        <div style={{ color: '#86efac', fontWeight: 'bold', fontSize: '1.1rem', marginTop: '0.2rem' }}>{value}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Right: Quick Actions + Tips + Report */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                {/* Scenario Summary */}
                <div style={cardStyle}>
                  <h3 style={{ fontWeight: 'bold', marginBottom: '0.75rem', fontSize: '0.9rem' }}>📋 Active Scenario</h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem 0.75rem', background: 'rgba(0,0,0,0.2)', borderRadius: '8px', fontSize: '0.85rem' }}>
                      <span style={{ color: '#9ca3af' }}>Machine Runtime Cut</span>
                      <span style={{ color: '#f59e0b', fontWeight: 'bold' }}>{scenario.reduceRuntime}%</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem 0.75rem', background: 'rgba(0,0,0,0.2)', borderRadius: '8px', fontSize: '0.85rem' }}>
                      <span style={{ color: '#9ca3af' }}>Hours Reduced</span>
                      <span style={{ color: '#60a5fa', fontWeight: 'bold' }}>{scenario.reduceHours} hrs</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem 0.75rem', background: 'rgba(6,78,59,0.2)', border: '1px solid rgba(16,185,129,0.3)', borderRadius: '8px', fontSize: '0.85rem' }}>
                      <span style={{ color: '#9ca3af' }}>Annual ROI</span>
                      <span style={{ color: '#34d399', fontWeight: 'bold' }}>₹{(simulation.simulated.savings * 12).toLocaleString()}</span>
                    </div>
                  </div>
                </div>

                {/* Energy Tips */}
                <div style={cardStyle}>
                  <h3 style={{ fontWeight: 'bold', marginBottom: '0.75rem', fontSize: '0.9rem' }}>💡 Smart Energy Tips</h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', maxHeight: '180px', overflowY: 'auto' }}>
                    {ENERGY_TIPS.map((t, i) => (
                      <div key={i} style={{ padding: '0.5rem 0.75rem', background: 'rgba(0,0,0,0.15)', borderRadius: '8px', borderLeft: '3px solid #3b82f6' }}>
                        <span style={{ fontSize: '0.65rem', color: '#60a5fa', fontWeight: 'bold', textTransform: 'uppercase' }}>{t.category}</span>
                        <p style={{ color: '#d1d5db', fontSize: '0.78rem', margin: 0, lineHeight: 1.4 }}>{t.tip}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* PDF Report Button */}
                <button onClick={handleDownloadReport} disabled={generatingReport}
                  style={{
                    width: '100%', padding: '0.85rem', borderRadius: '14px',
                    background: generatingReport ? 'rgba(255,255,255,0.05)' : 'linear-gradient(135deg, #16a34a, #15803d)',
                    border: 'none', color: 'white', fontWeight: 'bold', cursor: 'pointer',
                    display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', fontSize: '0.9rem',
                    boxShadow: generatingReport ? 'none' : '0 4px 20px rgba(22,163,74,0.3)'
                  }}
                >
                  {generatingReport ? <><FileText size={16} /> Generating PDF...</> : <><Download size={16} /> Download Carbon Report (PDF)</>}
                </button>
              </div>
            </div>

            {/* Simulation History Table */}
            {simulationHistory.length > 1 && (
              <div style={{ ...cardStyle, marginBottom: '2rem' }}>
                <h3 style={{ fontWeight: 'bold', marginBottom: '1rem', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}><Clock size={16} /> Simulation History</h3>
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                    <thead>
                      <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                        {['#', 'Time', 'Runtime Cut %', 'Hours Cut', 'Savings (₹)', 'Score'].map(h => (
                          <th key={h} style={{ padding: '0.5rem 0.75rem', textAlign: 'left', color: '#9ca3af', fontWeight: '500' }}>{h}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {simulationHistory.map((h, i) => (
                        <tr key={h.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                          <td style={{ padding: '0.5rem 0.75rem', color: '#6b7280' }}>{i + 1}</td>
                          <td style={{ padding: '0.5rem 0.75rem', color: '#9ca3af' }}>{h.timestamp}</td>
                          <td style={{ padding: '0.5rem 0.75rem', color: '#f59e0b' }}>{h.runtime}%</td>
                          <td style={{ padding: '0.5rem 0.75rem', color: '#60a5fa' }}>{h.hours} hrs</td>
                          <td style={{ padding: '0.5rem 0.75rem', color: '#34d399', fontWeight: 'bold' }}>₹{h.savings.toLocaleString()}</td>
                          <td style={{ padding: '0.5rem 0.75rem', color: '#a78bfa' }}>{h.score}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

          </motion.div>
        )}

        {/* ═══════════════════ ANALYTICS TAB ═══════════════════════════════════ */}
        {activeTab === 'analytics' && simulation && (
          <motion.div key="analytics" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} style={{ maxWidth: '1200px', margin: '0 auto', marginTop: '2rem' }}>
            <div className="text-center mb-8">
              <h2 className="text-3xl font-black mb-2" style={{ background: 'linear-gradient(90deg, #a78bfa, #60a5fa)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                📈 Advanced Analytics Suite
              </h2>
              <p className="text-gray-400">Predictive Forecasting · Industry Benchmarking · ROI Calculator</p>
            </div>

            {analyticsLoading ? (
              <div style={{ textAlign: 'center', padding: '4rem', color: '#9ca3af' }}>⏳ Loading analytics...</div>
            ) : (
              <>
                {/* Row 1: Forecast + Benchmark */}
                <div style={{ display: 'grid', gridTemplateColumns: '3fr 2fr', gap: '1.5rem', marginBottom: '1.5rem' }}>

                  {/* Predictive Forecasting */}
                  {forecast && (
                    <div style={cardStyle}>
                      <h3 style={{ fontWeight: 'bold', marginBottom: '0.5rem', fontSize: '0.95rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                        <TrendingDown size={16} /> 6-Month Cost Forecast
                        <span style={{ marginLeft: 'auto', fontSize: '0.7rem', color: '#6b7280' }}>Inflation: {forecast.inflation_rate_used}</span>
                      </h3>
                      <div style={{ height: '250px' }}>
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={forecast.forecast}>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" vertical={false} />
                            <XAxis dataKey="month" stroke="rgba(255,255,255,0.5)" fontSize={11} />
                            <YAxis stroke="rgba(255,255,255,0.5)" fontSize={11} />
                            <Tooltip contentStyle={{ background: 'rgba(15,23,42,0.95)', border: '1px solid rgba(255,255,255,0.15)', borderRadius: '10px', fontSize: '0.85rem' }} />
                            <Legend />
                            <Bar dataKey="baseline_cost" name="No Change" fill="#ef4444" radius={[4,4,0,0]} />
                            <Bar dataKey="simulated_cost" name="Optimized" fill="#22c55e" radius={[4,4,0,0]} />
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-around', marginTop: '0.75rem' }}>
                        <div style={{ textAlign: 'center' }}>
                          <div style={{ color: '#6b7280', fontSize: '0.7rem' }}>6-Month Without Changes</div>
                          <div style={{ color: '#ef4444', fontWeight: 'bold', fontSize: '1.1rem' }}>₹{forecast.total_baseline_cost?.toLocaleString()}</div>
                        </div>
                        <div style={{ textAlign: 'center' }}>
                          <div style={{ color: '#6b7280', fontSize: '0.7rem' }}>6-Month Optimized</div>
                          <div style={{ color: '#22c55e', fontWeight: 'bold', fontSize: '1.1rem' }}>₹{forecast.total_simulated_cost?.toLocaleString()}</div>
                        </div>
                        <div style={{ textAlign: 'center' }}>
                          <div style={{ color: '#6b7280', fontSize: '0.7rem' }}>6-Month Savings</div>
                          <div style={{ color: '#a3e635', fontWeight: 'bold', fontSize: '1.1rem' }}>₹{forecast.total_savings_6m?.toLocaleString()}</div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Industry Benchmark */}
                  {benchmark && (
                    <div style={cardStyle}>
                      <h3 style={{ fontWeight: 'bold', marginBottom: '1rem', fontSize: '0.95rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                        <Target size={16} /> Industry Benchmark
                      </h3>
                      {/* Rating Badge */}
                      <div style={{ textAlign: 'center', marginBottom: '1.25rem' }}>
                        <div style={{
                          display: 'inline-block', padding: '0.5rem 1.5rem', borderRadius: '1rem',
                          background: `${benchmark.rating_color}22`, border: `2px solid ${benchmark.rating_color}`,
                          color: benchmark.rating_color, fontWeight: 'bold', fontSize: '1.1rem'
                        }}>
                          {benchmark.rating}
                        </div>
                        <div style={{ color: '#9ca3af', fontSize: '0.8rem', marginTop: '0.5rem' }}>
                          {benchmark.kwh_per_employee} kWh/employee · Top {100 - benchmark.percentile}%
                        </div>
                      </div>
                      {/* Comparison Bars */}
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
                        {benchmark.comparison_chart?.map(({ label, value, fill }) => (
                          <div key={label}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '0.15rem' }}>
                              <span style={{ color: '#d1d5db' }}>{label}</span>
                              <span style={{ color: fill, fontWeight: 'bold' }}>{value} kWh/emp</span>
                            </div>
                            <div style={{ height: '8px', background: 'rgba(255,255,255,0.08)', borderRadius: '4px', overflow: 'hidden' }}>
                              <div style={{ height: '8px', width: `${Math.min((value / (benchmark.benchmarks?.poor || 150)) * 100, 100)}%`, background: fill, borderRadius: '4px', transition: 'width 0.5s ease' }} />
                            </div>
                          </div>
                        ))}
                      </div>
                      {benchmark.gap_to_excellent > 0 && (
                        <div style={{ marginTop: '1rem', padding: '0.75rem', background: 'rgba(245,158,11,0.1)', border: '1px solid rgba(245,158,11,0.2)', borderRadius: '10px', fontSize: '0.8rem', color: '#fbbf24' }}>
                          Gap to Excellent: <strong>{benchmark.gap_to_excellent} kWh/emp</strong> · Can save <strong>{benchmark.potential_savings_kwh} kWh/month</strong> more
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {/* Row 2: ROI Payback Calculator */}
                {roiData && (
                  <div style={{ ...cardStyle, marginBottom: '2rem' }}>
                    <h3 style={{ fontWeight: 'bold', marginBottom: '1rem', fontSize: '0.95rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                      <DollarSign size={16} /> ROI Payback Calculator
                      <span style={{ marginLeft: 'auto', fontSize: '0.75rem', color: '#6b7280' }}>Base Monthly Savings: ₹{roiData.base_monthly_savings?.toLocaleString()}</span>
                    </h3>
                    <div style={{ overflowX: 'auto' }}>
                      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                        <thead>
                          <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                            {['Investment', 'Cost (₹)', 'Extra Savings', 'Total/Month', 'Payback', 'Annual ROI', '5-Year Profit', ''].map(h => (
                              <th key={h} style={{ padding: '0.6rem 0.75rem', textAlign: 'left', color: '#9ca3af', fontWeight: '500' }}>{h}</th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {roiData.investments?.map((inv, i) => (
                            <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)', background: inv.recommended ? 'rgba(34,197,94,0.05)' : 'transparent' }}>
                              <td style={{ padding: '0.6rem 0.75rem', color: 'white', fontWeight: '500' }}>{inv.name}</td>
                              <td style={{ padding: '0.6rem 0.75rem', color: '#f59e0b' }}>₹{inv.investment_cost?.toLocaleString()}</td>
                              <td style={{ padding: '0.6rem 0.75rem', color: '#60a5fa' }}>+{inv.extra_savings_pct}%</td>
                              <td style={{ padding: '0.6rem 0.75rem', color: '#34d399', fontWeight: 'bold' }}>₹{inv.total_monthly_saving?.toLocaleString()}</td>
                              <td style={{ padding: '0.6rem 0.75rem', color: inv.payback_months < 24 ? '#a3e635' : '#f87171', fontWeight: 'bold' }}>
                                {inv.payback_months < 999 ? `${inv.payback_months} mo` : '∞'}
                              </td>
                              <td style={{ padding: '0.6rem 0.75rem', color: '#a78bfa' }}>{inv.annual_roi_pct}%</td>
                              <td style={{ padding: '0.6rem 0.75rem', color: inv.five_year_profit > 0 ? '#34d399' : '#f87171', fontWeight: 'bold' }}>
                                ₹{inv.five_year_profit?.toLocaleString()}
                              </td>
                              <td style={{ padding: '0.6rem 0.75rem' }}>
                                {inv.recommended && <span style={{ background: '#22c55e22', color: '#22c55e', padding: '0.2rem 0.5rem', borderRadius: '4px', fontSize: '0.7rem', fontWeight: 'bold' }}>RECOMMENDED</span>}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                    <p style={{ color: '#6b7280', fontSize: '0.75rem', marginTop: '0.75rem' }}>
                      * Investments with payback period ≤ 24 months are marked as RECOMMENDED. ROI calculations assume constant savings.
                    </p>
                  </div>
                )}
              </>
            )}
          </motion.div>
        )}

        {/* ═══════════════════ AI ADVISOR TAB ══════════════════════════════════ */}
        {activeTab === 'chat' && simulation && (
          <motion.div key="chat" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} style={{ maxWidth: '900px', margin: '0 auto', marginTop: '2.5rem' }}>
            <div className="text-center mb-6">
              <h2 className="text-3xl font-black mb-2">🧠 AI Energy Advisor</h2>
              <p className="text-gray-400">Powered by Llama-3. The AI is briefed on your full simulation context.</p>
            </div>

            {/* Quick Context Banner */}
            <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
              {[
                { label: 'Baseline', value: `₹${simulation.baseline.bill}`, color: '#94a3b8' },
                { label: 'Simulated', value: `₹${simulation.simulated.bill}`, color: '#34d399' },
                { label: 'Savings', value: `₹${simulation.simulated.savings}`, color: '#a3e635' },
                { label: 'Score', value: `${simulation.simulated.score}/100`, color: '#60a5fa' },
              ].map(({ label, value, color }) => (
                <div key={label} style={{ padding: '0.4rem 1rem', background: 'rgba(255,255,255,0.05)', borderRadius: '0.5rem', fontSize: '0.8rem', border: '1px solid rgba(255,255,255,0.08)' }}>
                  <span style={{ color: '#9ca3af' }}>{label}: </span><span style={{ color, fontWeight: 'bold' }}>{value}</span>
                </div>
              ))}
            </div>

            <div style={{ ...cardStyle, height: '460px', display: 'flex', flexDirection: 'column', marginBottom: '5rem' }}>
              <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.75rem', marginBottom: '1rem' }}>
                {chatHistory.length === 0 && (
                  <div style={{ textAlign: 'center', marginTop: '3rem', color: '#9ca3af' }}>
                    <Zap size={32} style={{ margin: '0 auto 1rem', color: '#60a5fa' }} />
                    <p>AI has full context: <strong style={{ color: '#34d399' }}>₹{simulation.baseline.bill} → ₹{simulation.simulated.bill}</strong></p>
                    <p style={{ fontSize: '0.85rem', marginTop: '0.5rem' }}>Try: <em>"Which component should I prioritize?"</em></p>
                    <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'center', marginTop: '1.5rem', flexWrap: 'wrap' }}>
                      {["Explain my simulation results", "How do I implement these savings?", "What should I prioritize first?"].map(q => (
                        <button key={q} onClick={() => { setChatQuery(q); }} style={{ padding: '0.4rem 0.75rem', background: 'rgba(59,130,246,0.15)', border: '1px solid rgba(59,130,246,0.3)', borderRadius: '0.5rem', color: '#93c5fd', fontSize: '0.8rem', cursor: 'pointer' }}>{q}</button>
                      ))}
                    </div>
                  </div>
                )}
                {chatHistory.map((msg, idx) => (
                  <motion.div key={idx} initial={{ opacity: 0, x: msg.role === 'user' ? 20 : -20 }} animate={{ opacity: 1, x: 0 }}
                    style={{
                      padding: '0.85rem 1rem', borderRadius: '1rem', maxWidth: '80%',
                      alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                      background: msg.role === 'user' ? 'linear-gradient(135deg, #2563eb, #1d4ed8)' : 'rgba(255,255,255,0.06)',
                      borderBottomRightRadius: msg.role === 'user' ? '4px' : '1rem',
                      borderBottomLeftRadius: msg.role === 'assistant' ? '4px' : '1rem',
                      border: msg.role === 'assistant' ? '1px solid rgba(255,255,255,0.08)' : 'none',
                      lineHeight: '1.55', fontSize: '0.9rem', whiteSpace: 'pre-wrap'
                    }}>
                    {msg.content}
                  </motion.div>
                ))}
                <div ref={chatEndRef} />
              </div>
              <form onSubmit={handleChat} style={{ display: 'flex', gap: '0.75rem', padding: '0.5rem', background: 'rgba(0,0,0,0.2)', borderRadius: '0.75rem', border: '1px solid rgba(255,255,255,0.05)' }}>
                <input type="text" style={{ flex: 1, background: 'transparent', padding: '0 1rem', border: 'none', outline: 'none', color: 'white' }}
                  placeholder="Ask about savings, carbon impact, implementation strategy..."
                  value={chatQuery} onChange={(e) => setChatQuery(e.target.value)} />
                <button type="submit" style={{ padding: '0.5rem 1.5rem', background: '#2563eb', borderRadius: '0.5rem', fontWeight: 'bold', border: 'none', color: 'white', cursor: 'pointer' }}>Send</button>
              </form>
            </div>
          </motion.div>
        )}

      </AnimatePresence>
    </div>
  );
};

export default Dashboard;
