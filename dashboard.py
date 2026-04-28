import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import time
import json
from agents.research_agent import ResearchAgent
from agents.analysis_agent import AnalysisAgent
from agents.outreach_agent import OutreachAgent

# Premium UI Config
st.set_page_config(page_title="Elite Lead Intelligence", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for Premium Look
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { background-color: #00f2ea; color: #000; border-radius: 10px; font-weight: bold; }
    .stTextInput>div>div>input { background-color: #161b22; color: #fff; border: 1px solid #30363d; }
    .report-card { background-color: #161b22; padding: 20px; border-radius: 15px; border-left: 5px solid #00f2ea; margin-bottom: 20px; }
    .agent-log { font-family: 'Courier New', monospace; color: #00ff41; background: #000; padding: 10px; border-radius: 5px; height: 150px; overflow-y: auto; }
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 AI Multi-Agent Lead Intelligence Squad")
st.markdown("---")

col1, col2 = st.columns([1, 2])

with col1:
    st.header("🔍 Input Target")
    company_name = st.text_input("Company Name", placeholder="e.g. OpenAI")
    company_url = st.text_input("Website URL", placeholder="e.g. openai.com")
    
    if st.button("🚀 DEPLOY AGENT SQUAD"):
        if not company_name or not company_url:
            st.error("Please provide both name and URL.")
        else:
            # logs container
            log_container = st.empty()
            
            # --- START EXECUTION ---
            with st.spinner("Squad deploying..."):
                # Agent 1: Research
                log_container.markdown('<div class="agent-log">> Initializing ResearchAgent...<br>> Scanning news & web...</div>', unsafe_allow_html=True)
                researcher = ResearchAgent()
                research_data = researcher.execute(company_name, company_url)
                time.sleep(1)
                
                # Agent 2: Analysis
                log_container.markdown('<div class="agent-log">> Research complete.<br>> Initializing AnalysisAgent...<br>> Performing financial deep-dive...</div>', unsafe_allow_html=True)
                analyzer = AnalysisAgent()
                analysis = analyzer.analyze(research_data)
                time.sleep(1)
                
                # Agent 3: Outreach
                log_container.markdown('<div class="agent-log">> Analysis complete.<br>> Initializing OutreachAgent...<br>> Drafting un-ignorable copy...</div>', unsafe_allow_html=True)
                outreach_agent = OutreachAgent()
                outreach = outreach_agent.generate(analysis)
                
                st.session_state['analysis'] = analysis
                st.session_state['research'] = research_data
                st.session_state['outreach'] = outreach
                st.success("Mission Accomplished.")

with col2:
    if 'analysis' in st.session_state:
        analysis = st.session_state['analysis']
        research = st.session_state['research']
        outreach = st.session_state['outreach']
        
        # --- GAUGE CHART ---
        score = analysis.get('financial_score', 0)
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Lead Probability Score"},
            gauge = {
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "#00f2ea"},
                'steps': [
                    {'range': [0, 50], 'color': "#161b22"},
                    {'range': [50, 80], 'color': "#0e1117"},
                    {'range': [80, 100], 'color': "#1c1c1c"}
                ],
            }
        ))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "#fff", 'family': "Arial"})
        st.plotly_chart(fig, use_container_width=True)
        
        # --- REPORT ---
        st.subheader("📊 Strategic Intelligence Report")
        with st.container():
            st.markdown(f'<div class="report-card"><b>Market Position:</b> {analysis.get("market_position")}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="report-card"><b>Analysis:</b> {analysis.get("roi_prediction")}</div>', unsafe_allow_html=True)
            
            tabs = st.tabs(["Strategic Gaps", "Latest News", "Outreach Drafts"])
            with tabs[0]:
                for gap in analysis.get('strategic_gaps', []):
                    st.write(f"🚩 {gap}")
            with tabs[1]:
                st.write(research.get('news'))
            with tabs[2]:
                st.code(outreach.get('outreach_drafts'))
    else:
        st.info("Input a target and click 'Deploy Agent Squad' to see the intelligence report.")

st.markdown("---")
st.caption("Elite Agentic Workflow v2.0 | '99/10 Status' Prototype")
