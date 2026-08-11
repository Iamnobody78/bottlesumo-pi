import React, { useState } from 'react';
import AgentsView from './pages/AgentsView.jsx';
import PoliciesView from './pages/PoliciesView.jsx';
import AuditView from './pages/AuditView.jsx';
import VceView from './pages/VceView.jsx';
import EvaluateTool from './pages/EvaluateTool.jsx';
import PolicyEditorView from './pages/PolicyEditorView.jsx';

const TABS = [
  { key: 'agents', label: '代理清单', view: AgentsView },
  { key: 'policies', label: '策略管理', view: PoliciesView },
  { key: 'editor', label: '策略编辑器', view: PolicyEditorView },
  { key: 'audit', label: '审计查看', view: AuditView },
  { key: 'vce', label: 'VCE 扫描', view: VceView },
  { key: 'eval', label: '实时裁决', view: EvaluateTool },
];

export default function App() {
  const [tab, setTab] = useState('agents');
  const Active = TABS.find((t) => t.key === tab).view;

  return (
    <div className="app">
      <header className="topbar">
        <h1>🛡 Governance Center <span className="sub">BottleSumo · agent-governance-v2</span></h1>
        <nav className="tabs">
          {TABS.map((t) => (
            <button key={t.key}
                    className={tab === t.key ? 'tab active' : 'tab'}
                    onClick={() => setTab(t.key)}>{t.label}</button>
          ))}
        </nav>
      </header>
      <main className="content"><Active /></main>
      <footer className="foot">S68 Phase 1 MVP · CVE-S 闭环 S63-S66 · 治理可验证</footer>
    </div>
  );
}
