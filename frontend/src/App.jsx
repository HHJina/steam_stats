import { useState, useEffect } from "react";
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, ReferenceLine,
} from "recharts";

// const API = "http://localhost:8000/api";
const API = "https://steamstats-production.up.railway.app/api";

const NAV = [
  { id: "home", label: "홈" },
  { id: "games", label: "게임 순위" },
  { id: "stats", label: "장르 통계" },
  { id: "gems", label: "숨은 명작" },
];

const styles = `
  @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700&family=Noto+Sans+KR:wght@400;500;700&display=swap');
  * { box-sizing: border-box; margin: 0; padding: 0; }
  :root {
    --navy: #0a0f1e; --navy2: #0e1528; --navy3: #141c35;
    --panel: #1a2340; --panel2: #1e294a;
    --border: rgba(66,135,245,0.15);
    --blue: #4287f5; --blue2: #66a3ff; --blue-dim: rgba(66,135,245,0.08);
    --teal: #00c9b1; --amber: #f5a623; --red: #e05c5c;
    --text: #e8eaf6; --text2: #8899bb; --text3: #4a5a7a;
    --font-head: 'Rajdhani', sans-serif; --font-body: 'Noto Sans KR', sans-serif;
  }
  body { background: var(--navy); color: var(--text); font-family: var(--font-body); min-height: 100vh; }
  .app { display: flex; flex-direction: column; min-height: 100vh; }
  .nav {
    position: sticky; top: 0; z-index: 100;
    background: rgba(10,15,30,0.92); backdrop-filter: blur(12px);
    border-bottom: 1px solid var(--border);
    display: flex; align-items: center; padding: 0 2rem; height: 56px;
  }
  .nav-logo { font-family: var(--font-head); font-size: 22px; font-weight: 700; color: var(--blue2); letter-spacing: 2px; margin-right: 3rem; text-transform: uppercase; }
  .nav-logo span { color: var(--teal); }
  .nav-links { display: flex; }
  .nav-btn { background: none; border: none; cursor: pointer; font-family: var(--font-body); font-size: 14px; font-weight: 500; color: var(--text2); padding: 0 1.2rem; height: 56px; border-bottom: 2px solid transparent; transition: color 0.2s, border-color 0.2s; }
  .nav-btn:hover { color: var(--text); }
  .nav-btn.active { color: var(--blue2); border-bottom-color: var(--blue); }
  .main { flex: 1; padding: 2rem; max-width: 1200px; width: 100%; margin: 0 auto; }
  .hero { background: linear-gradient(135deg, var(--navy2) 0%, var(--navy3) 100%); border: 1px solid var(--border); border-radius: 12px; padding: 3rem 2.5rem; margin-bottom: 2rem; position: relative; overflow: hidden; }
  .hero::before { content: ''; position: absolute; top: -60px; right: -60px; width: 300px; height: 300px; border-radius: 50%; background: radial-gradient(circle, rgba(66,135,245,0.08) 0%, transparent 70%); }
  .hero-title { font-family: var(--font-head); font-size: 42px; font-weight: 700; color: var(--text); line-height: 1.1; margin-bottom: 0.5rem; }
  .hero-title span { color: var(--blue2); }
  .hero-sub { color: var(--text2); font-size: 15px; margin-bottom: 1.5rem; }
  .hero-stats { display: flex; gap: 2rem; }
  .hero-stat { text-align: center; }
  .hero-stat-val { font-family: var(--font-head); font-size: 28px; font-weight: 700; color: var(--blue2); }
  .hero-stat-label { font-size: 12px; color: var(--text3); text-transform: uppercase; letter-spacing: 1px; }
  .section-title { font-family: var(--font-head); font-size: 20px; font-weight: 600; color: var(--text); margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem; }
  .section-title::before { content: ''; display: inline-block; width: 3px; height: 18px; background: var(--blue); border-radius: 2px; }
  .grid { display: grid; gap: 1rem; }
  .grid-2 { grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); }
  .grid-3 { grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); }
  .card { background: var(--panel); border: 1px solid var(--border); border-radius: 10px; padding: 1.25rem; transition: border-color 0.2s, transform 0.2s; }
  .card:hover { border-color: rgba(66,135,245,0.35); transform: translateY(-1px); }
  .card-header { display: flex; gap: 1rem; align-items: flex-start; margin-bottom: 0.75rem; }
  .card-img { width: 80px; height: 38px; border-radius: 4px; object-fit: cover; background: var(--panel2); flex-shrink: 0; }
  .card-title { font-size: 14px; font-weight: 500; color: var(--text); line-height: 1.3; }
  .card-sub { font-size: 12px; color: var(--text2); margin-top: 2px; }
  .card-footer { display: flex; justify-content: space-between; align-items: center; margin-top: 0.75rem; }
  .badge { font-size: 11px; padding: 2px 8px; border-radius: 20px; font-weight: 500; }
  .badge-blue { background: rgba(66,135,245,0.15); color: var(--blue2); }
  .badge-teal { background: rgba(0,201,177,0.12); color: var(--teal); }
  .badge-amber { background: rgba(245,166,35,0.12); color: var(--amber); }
  .badge-red { background: rgba(224,92,92,0.12); color: var(--red); }
  .stat-card { background: var(--panel); border: 1px solid var(--border); border-radius: 10px; padding: 1.25rem; }
  .stat-val { font-family: var(--font-head); font-size: 32px; font-weight: 700; color: var(--blue2); }
  .stat-label { font-size: 12px; color: var(--text2); margin-top: 4px; text-transform: uppercase; letter-spacing: 0.5px; }
  .rank-item { display: flex; align-items: center; gap: 1rem; padding: 0.75rem; background: var(--panel); border: 1px solid var(--border); border-radius: 8px; transition: border-color 0.2s; }
  .rank-item:hover { border-color: rgba(66,135,245,0.3); }
  .rank-num { font-family: var(--font-head); font-size: 20px; font-weight: 700; color: var(--text3); width: 28px; text-align: center; flex-shrink: 0; }
  .rank-num.top { color: var(--amber); }
  .rank-img { width: 64px; height: 30px; border-radius: 3px; object-fit: cover; background: var(--panel2); flex-shrink: 0; }
  .rank-info { flex: 1; min-width: 0; }
  .rank-name { font-size: 14px; font-weight: 500; color: var(--text); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .rank-players { font-family: var(--font-head); font-size: 16px; font-weight: 600; color: var(--teal); white-space: nowrap; }
  .chart-card { background: var(--panel); border: 1px solid var(--border); border-radius: 10px; padding: 1.25rem; }
  .chart-title { font-size: 13px; color: var(--text2); margin-bottom: 1rem; }
  .genre-row { display: flex; align-items: center; gap: 1rem; padding: 0.75rem 1rem; background: var(--panel); border: 1px solid var(--border); border-radius: 8px; }
  .genre-name { font-size: 14px; font-weight: 500; color: var(--text); width: 120px; flex-shrink: 0; }
  .genre-bar-wrap { flex: 1; height: 6px; background: var(--panel2); border-radius: 3px; overflow: hidden; }
  .genre-bar { height: 100%; background: linear-gradient(90deg, var(--blue), var(--teal)); border-radius: 3px; transition: width 0.6s ease; }
  .genre-val { font-family: var(--font-head); font-size: 14px; color: var(--text2); width: 80px; text-align: right; flex-shrink: 0; }
  .genre-count { font-size: 12px; color: var(--text3); width: 60px; text-align: right; flex-shrink: 0; }
  .gem-card { background: var(--panel); border: 1px solid var(--border); border-radius: 10px; overflow: hidden; transition: border-color 0.2s, transform 0.2s; }
  .gem-card:hover { border-color: rgba(0,201,177,0.4); transform: translateY(-2px); }
  .gem-img { width: 100%; height: 80px; object-fit: cover; background: var(--panel2); }
  .gem-body { padding: 0.875rem; }
  .gem-name { font-size: 13px; font-weight: 500; color: var(--text); margin-bottom: 0.5rem; line-height: 1.3; }
  .gem-score-wrap { display: flex; align-items: center; justify-content: space-between; }
  .gem-score { font-family: var(--font-head); font-size: 22px; font-weight: 700; color: var(--teal); }
  .gem-meta { font-size: 11px; color: var(--text3); }
  .loading { display: flex; align-items: center; justify-content: center; padding: 4rem; color: var(--text2); font-size: 14px; gap: 0.5rem; }
  .spinner { width: 18px; height: 18px; border: 2px solid var(--border); border-top-color: var(--blue); border-radius: 50%; animation: spin 0.8s linear infinite; }
  @keyframes spin { to { transform: rotate(360deg); } }
  .detail-hero { display: flex; gap: 1.5rem; margin-bottom: 2rem; }
  .detail-img { width: 200px; height: 94px; border-radius: 6px; object-fit: cover; background: var(--panel); flex-shrink: 0; }
  .detail-info { flex: 1; }
  .detail-title { font-family: var(--font-head); font-size: 28px; font-weight: 700; color: var(--text); margin-bottom: 0.25rem; }
  .detail-dev { font-size: 13px; color: var(--text2); margin-bottom: 0.75rem; }
  .detail-tags { display: flex; flex-wrap: wrap; gap: 0.5rem; }
  .tabs { display: flex; border-bottom: 1px solid var(--border); margin-bottom: 1.5rem; }
  .tab-btn { background: none; border: none; border-bottom: 2px solid transparent; cursor: pointer; font-family: var(--font-body); font-size: 14px; color: var(--text2); padding: 0.625rem 1.25rem; margin-bottom: -1px; transition: color 0.2s, border-color 0.2s; }
  .tab-btn:hover { color: var(--text); }
  .tab-btn.active { color: var(--blue2); border-bottom-color: var(--blue); }
  .mb1 { margin-bottom: 1rem; }
`;

function fmt(n) {
  if (!n && n !== 0) return "-";
  if (n >= 1000000) return (n / 1000000).toFixed(1) + "M";
  if (n >= 1000) return (n / 1000).toFixed(1) + "K";
  return n.toLocaleString();
}

function fmtPrice(p) {
  if (!p && p !== 0) return "무료";
  if (p === 0) return "무료";
  return "₩" + Number(p).toLocaleString("ko-KR");
}

function Loading() {
  return <div className="loading"><div className="spinner" /> 불러오는 중...</div>;
}

function GameCard({ game, onClick }) {
  return (
    <div className="card" style={{ cursor: "pointer" }} onClick={() => onClick(game)}>
      <div className="card-header">
        <img className="card-img" src={game.header_image} alt={game.name} onError={e => e.target.style.display = "none"} />
        <div>
          <div className="card-title">{game.name}</div>
          <div className="card-sub">{game.developer || "알 수 없음"}</div>
        </div>
      </div>
      <div className="card-footer">
        <div style={{ display: "flex", gap: "0.5rem" }}>
          {game.is_free && <span className="badge badge-teal">무료</span>}
          {game.is_indie && <span className="badge badge-blue">인디</span>}
        </div>
        {game.metacritic_score && <span className="badge badge-amber">MC {game.metacritic_score}</span>}
      </div>
    </div>
  );
}

function GameDetail({ game, onBack }) {
  const [tab, setTab] = useState("prices");
  const [prices, setPrices] = useState(null);
  const [players, setPlayers] = useState(null);
  const [reviews, setReviews] = useState(null);
  const [spikes, setSpikes] = useState(null);
  const [sentiment, setSentiment] = useState(null);

  useEffect(() => {
    fetch(`${API}/games/${game.app_id}/prices`).then(r => r.json()).then(d => {
      setPrices(d.map(p => ({ date: new Date(p.collected_at).toLocaleDateString("ko-KR", { month: "short", day: "numeric" }), price: Number(p.price) })));
    }).catch(() => setPrices([]));
    fetch(`${API}/games/${game.app_id}/players`).then(r => r.json()).then(d => {
      setPlayers(d.map(p => ({ date: new Date(p.collected_at).toLocaleDateString("ko-KR", { month: "short", day: "numeric" }), players: p.player_count })));
    }).catch(() => setPlayers([]));
    fetch(`${API}/reviews/${game.app_id}?limit=5&language=korean`).then(r => r.json()).then(setReviews).catch(() => setReviews([]));
    fetch(`${API}/reviews/${game.app_id}/spikes`).then(r => r.json()).then(setSpikes).catch(() => setSpikes([]));
    fetch(`${API}/reviews/${game.app_id}/sentiment`).then(r => r.json()).then(setSentiment).catch(() => setSentiment(null));
  }, [game.app_id]);

  const TABS = [
    ["prices", "가격 히스토리"],
    ["players", "동시접속자"],
    ["reviews", "리뷰"],
    ["spikes", "리뷰 폭증"],
    ["sentiment", "감성 분석"],
  ];

  return (
    <div>
      <button onClick={onBack} style={{ background: "none", border: "1px solid var(--border)", color: "var(--text2)", cursor: "pointer", padding: "6px 14px", borderRadius: 6, fontSize: 13, marginBottom: "1.5rem", fontFamily: "var(--font-body)", outline: "none" }}>
        ← 목록으로
      </button>
      <div className="detail-hero">
        <img className="detail-img" src={game.header_image} alt={game.name} />
        <div className="detail-info">
          <div className="detail-title">{game.name}</div>
          <div className="detail-dev">{game.developer} · {game.publisher}</div>
          <div className="detail-tags">
            {game.is_free && <span className="badge badge-teal">무료</span>}
            {game.is_indie && <span className="badge badge-blue">인디</span>}
            {game.metacritic_score && <span className="badge badge-amber">Metacritic {game.metacritic_score}</span>}
            {game.release_date && <span className="badge" style={{ background: "var(--blue-dim)", color: "var(--text2)" }}>{game.release_date}</span>}
          </div>
        </div>
        <div style={{ textAlign: "right" }}>
          <div className="stat-val">{fmt(game.peak_in_game)}</div>
          <div className="stat-label">최고 동접자</div>
        </div>
      </div>

      <div className="tabs">
        {TABS.map(([id, label]) => (
          <button key={id} className={`tab-btn${tab === id ? " active" : ""}`} onClick={() => setTab(id)}>{label}</button>
        ))}
      </div>

      {tab === "prices" && (
        <div className="chart-card">
          <div className="chart-title">가격 변동 히스토리 (₩)</div>
          {!prices ? <Loading /> : prices.length === 0 ? <div className="loading">데이터 없음</div> : (
            <ResponsiveContainer width="100%" height={240}>
              <LineChart data={prices}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="date" tick={{ fill: "#8899bb", fontSize: 11 }} />
                <YAxis tick={{ fill: "#8899bb", fontSize: 11 }} tickFormatter={v => "₩" + Number(v).toLocaleString("ko-KR")} />
                <Tooltip contentStyle={{ background: "#1a2340", border: "1px solid rgba(66,135,245,0.2)", borderRadius: 8, color: "#e8eaf6", fontSize: 13 }} formatter={v => ["₩" + Number(v).toLocaleString("ko-KR"), "가격"]} />
                <Line type="monotone" dataKey="price" stroke="#4287f5" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>
      )}

      {tab === "players" && (
        <div className="chart-card">
          <div className="chart-title">동시접속자 수 변동</div>
          {!players ? <Loading /> : players.length === 0 ? <div className="loading">데이터 없음</div> : (
            <ResponsiveContainer width="100%" height={240}>
              <LineChart data={players}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="date" tick={{ fill: "#8899bb", fontSize: 11 }} />
                <YAxis tick={{ fill: "#8899bb", fontSize: 11 }} tickFormatter={fmt} />
                <Tooltip contentStyle={{ background: "#1a2340", border: "1px solid rgba(66,135,245,0.2)", borderRadius: 8, color: "#e8eaf6", fontSize: 13 }} formatter={v => [fmt(v) + "명", "동시접속자"]} />
                <Line type="monotone" dataKey="players" stroke="#00c9b1" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>
      )}

      {tab === "reviews" && (
        <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
          {!reviews ? <Loading /> : reviews.length === 0 ? <div className="loading">리뷰 없음</div> : reviews.map(r => (
            <div key={r.review_id} className="card">
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.5rem" }}>
                <span className={`badge ${r.voted_up ? "badge-teal" : "badge-red"}`}>{r.voted_up ? "👍 긍정" : "👎 부정"}</span>
                <span style={{ fontSize: 11, color: "var(--text3)" }}>{r.playtime_hours ? r.playtime_hours + "시간 플레이" : ""}</span>
              </div>
              <div style={{ fontSize: 13, color: "var(--text2)", lineHeight: 1.6, maxHeight: 80, overflow: "hidden" }}>{r.review_text}</div>
            </div>
          ))}
        </div>
      )}

      {tab === "spikes" && (
        <div>
          <div className="chart-card" style={{ marginBottom: "1rem" }}>
            <div className="chart-title">일별 리뷰 증가량</div>
            {!spikes ? <Loading /> : spikes.length === 0 ? <div className="loading">데이터 없음</div> : (
              <ResponsiveContainer width="100%" height={240}>
                <BarChart data={spikes.slice().reverse()}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="collected_at" tick={{ fill: "#8899bb", fontSize: 11 }} tickFormatter={v => new Date(v).toLocaleDateString("ko-KR", { month: "short", day: "numeric" })} />
                  <YAxis tick={{ fill: "#8899bb", fontSize: 11 }} />
                  <Tooltip contentStyle={{ background: "#1a2340", border: "1px solid rgba(66,135,245,0.2)", borderRadius: 8, color: "#e8eaf6", fontSize: 13 }} labelFormatter={v => new Date(v).toLocaleDateString("ko-KR")} formatter={v => [v + "개", "리뷰 증가"]} />
                  <Bar dataKey="review_delta" name="리뷰 증가" fill="#4287f5" radius={[4, 4, 0, 0]} />
                  <ReferenceLine y={0} stroke="rgba(255,255,255,0.3)" strokeWidth={1} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
          <div style={{ display: "flex", gap: "1rem", marginBottom: "1rem", fontSize: 12 }}>
            {[["#00c9b1", "긍정 폭증 (화제작)"], ["#e05c5c", "부정 폭증 (리뷰 폭탄)"], ["#4287f5", "일반"]].map(([color, label]) => (
              <span key={label} style={{ display: "flex", alignItems: "center", gap: 6 }}>
                <span style={{ width: 12, height: 12, borderRadius: 2, background: color, display: "inline-block" }} />
                <span style={{ color: "var(--text2)" }}>{label}</span>
              </span>
            ))}
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
            {!spikes ? null : spikes.filter(s => s.is_positive_spike || s.is_negative_spike).length === 0 ? (
              <div style={{ fontSize: 13, color: "var(--text3)", padding: "1rem", textAlign: "center" }}>감지된 리뷰 폭증 이벤트가 없습니다</div>
            ) : spikes.filter(s => s.is_positive_spike || s.is_negative_spike).map((s, i) => (
              <div key={i} className="card" style={{ borderColor: s.is_negative_spike ? "rgba(224,92,92,0.3)" : "rgba(0,201,177,0.3)" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                    <span className={`badge ${s.is_negative_spike ? "badge-red" : "badge-teal"}`}>{s.is_negative_spike ? "🚨 리뷰 폭탄" : "🔥 화제작"}</span>
                    <span style={{ fontSize: 13, color: "var(--text2)" }}>{new Date(s.collected_at).toLocaleDateString("ko-KR")}</span>
                  </div>
                  <div style={{ textAlign: "right" }}>
                    <div style={{ fontFamily: "var(--font-head)", fontSize: 18, fontWeight: 700, color: s.is_negative_spike ? "#e05c5c" : "#00c9b1" }}>+{s.review_delta?.toLocaleString()}</div>
                    <div style={{ fontSize: 11, color: "var(--text3)" }}>리뷰 증가</div>
                  </div>
                </div>
                <div style={{ marginTop: "0.5rem", fontSize: 12, color: "var(--text3)" }}>전체 {s.total_reviews?.toLocaleString()}개</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {tab === "sentiment" && (
        <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          {!sentiment ? <Loading /> : (
            <>
              {/* 요약 카드 3개 */}
              <div className="grid grid-3">
                {(() => {
                  const avg = Number(sentiment.avg_sentiment ?? 0);
                  const positive = sentiment.positive_count ?? 0;
                  const negative = sentiment.negative_count ?? 0;
                  const neutral = sentiment.neutral_count ?? 0;
                  const total = positive + negative + neutral || 1;
                  const scoreColor = avg > 0.2 ? "#00c9b1" : avg < -0.2 ? "#e05c5c" : "#f5a623";
                  const scoreLabel = avg > 0.2 ? "긍정적" : avg < -0.2 ? "부정적" : "중립적";
                  return (
                    <>
                      <div className="stat-card">
                        <div style={{ fontFamily: "var(--font-head)", fontSize: 36, fontWeight: 700, color: scoreColor }}>{avg.toFixed(2)}</div>
                        <div className="stat-label">평균 감성 점수</div>
                        <div style={{ fontSize: 12, color: scoreColor, marginTop: 4 }}>{scoreLabel}</div>
                      </div>
                      <div className="stat-card">
                        <div style={{ fontFamily: "var(--font-head)", fontSize: 36, fontWeight: 700, color: "#00c9b1" }}>{Math.round((positive / total) * 100)}%</div>
                        <div className="stat-label">긍정 리뷰</div>
                        <div style={{ fontSize: 12, color: "var(--text3)", marginTop: 4 }}>{positive.toLocaleString()}개</div>
                      </div>
                      <div className="stat-card">
                        <div style={{ fontFamily: "var(--font-head)", fontSize: 36, fontWeight: 700, color: "#e05c5c" }}>{Math.round((negative / total) * 100)}%</div>
                        <div className="stat-label">부정 리뷰</div>
                        <div style={{ fontSize: 12, color: "var(--text3)", marginTop: 4 }}>{negative.toLocaleString()}개</div>
                      </div>
                    </>
                  );
                })()}
              </div>

              {/* 긍정/중립/부정 비율 바 */}
              {(() => {
                const positive = sentiment.positive_count ?? 0;
                const negative = sentiment.negative_count ?? 0;
                const neutral = sentiment.neutral_count ?? 0;
                const total = positive + negative + neutral || 1;
                return (
                  <div className="chart-card">
                    <div className="chart-title">긍정 / 중립 / 부정 비율</div>
                    <div style={{ display: "flex", height: 24, borderRadius: 4, overflow: "hidden", gap: 2, marginBottom: "0.75rem" }}>
                      <div style={{ flex: positive, background: "#00c9b1" }} />
                      <div style={{ flex: neutral, background: "#f5a623" }} />
                      <div style={{ flex: negative, background: "#e05c5c" }} />
                    </div>
                    <div style={{ display: "flex", gap: "1.5rem", fontSize: 12, flexWrap: "wrap" }}>
                      {[["#00c9b1", "긍정", positive, total], ["#f5a623", "중립", neutral, total], ["#e05c5c", "부정", negative, total]].map(([color, label, count, t]) => (
                        <span key={label} style={{ display: "flex", alignItems: "center", gap: 6 }}>
                          <span style={{ width: 10, height: 10, borderRadius: 2, background: color, display: "inline-block" }} />
                          <span style={{ color: "var(--text2)" }}>{label} {Math.round((count / t) * 100)}% ({count.toLocaleString()}개)</span>
                        </span>
                      ))}
                    </div>
                  </div>
                );
              })()}

              {/* 감성 점수 게이지 */}
              {(() => {
                const avg = Number(sentiment.avg_sentiment ?? 0);
                const scoreColor = avg > 0.2 ? "#00c9b1" : avg < -0.2 ? "#e05c5c" : "#f5a623";
                return (
                  <div className="chart-card">
                    <div className="chart-title">감성 점수 (-1 부정 ~ +1 긍정)</div>
                    <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.5rem" }}>
                      <span style={{ fontSize: 11, color: "var(--text3)", width: 36 }}>-1</span>
                      <div style={{ flex: 1, height: 8, background: "linear-gradient(90deg, #e05c5c, #f5a623, #00c9b1)", borderRadius: 4, position: "relative" }}>
                        <div style={{ position: "absolute", top: -4, left: `${((avg + 1) / 2) * 100}%`, transform: "translateX(-50%)", width: 16, height: 16, borderRadius: "50%", background: scoreColor, border: "2px solid var(--navy)" }} />
                      </div>
                      <span style={{ fontSize: 11, color: "var(--text3)", width: 36, textAlign: "right" }}>+1</span>
                    </div>
                    <div style={{ textAlign: "center", fontSize: 13, color: scoreColor, marginTop: "0.5rem" }}>평균 {avg.toFixed(3)}</div>
                  </div>
                );
              })()}
            </>
          )}
        </div>
      )}
    </div>
  );
}

function HomePage({ onSelectGame }) {
  const [topGames, setTopGames] = useState(null);
  const [gems, setGems] = useState(null);

  useEffect(() => {
    fetch(`${API}/stats/top-players?limit=10`).then(r => r.json()).then(setTopGames).catch(() => setTopGames([]));
    fetch(`${API}/gems/?limit=6`).then(r => r.json()).then(setGems).catch(() => setGems([]));
  }, []);

  return (
    <div>
      <div className="hero">
        <div className="hero-title">STEAM <span>STATS</span></div>
        <div className="hero-sub">Steam 게임 데이터 분석 대시보드 · 실시간 업데이트</div>
        <div className="hero-stats">
          <div className="hero-stat"><div className="hero-stat-val">{topGames ? "118+" : "..."}</div><div className="hero-stat-label">추적 게임</div></div>
          <div className="hero-stat"><div className="hero-stat-val">매일</div><div className="hero-stat-label">업데이트</div></div>
          <div className="hero-stat"><div className="hero-stat-val">NLP</div><div className="hero-stat-label">리뷰 분석</div></div>
        </div>
      </div>

      <div className="section-title mb1">실시간 인기 게임 TOP 10</div>
      <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem", marginBottom: "2rem" }}>
        {!topGames ? <Loading /> : topGames.map((g, i) => (
          <div key={g.app_id} className="rank-item" style={{ cursor: "pointer" }} onClick={() => onSelectGame({ app_id: g.app_id, name: g.name, header_image: g.header_image })}>
            <div className={`rank-num${i < 3 ? " top" : ""}`}>{i + 1}</div>
            <img className="rank-img" src={g.header_image} alt={g.name} onError={e => e.target.style.display = "none"} />
            <div className="rank-info"><div className="rank-name">{g.name}</div></div>
            <div className="rank-players">{fmt(g.player_count)}명</div>
          </div>
        ))}
      </div>

      <div className="section-title mb1">숨은 명작 추천</div>
      <div className="grid grid-3">
        {!gems ? <Loading /> : gems.map(g => (
          <div key={g.app_id} className="gem-card">
            <img className="gem-img" src={g.header_image} alt={g.name} onError={e => e.target.style.background = "#1e294a"} />
            <div className="gem-body">
              <div className="gem-name">{g.name}</div>
              <div className="gem-score-wrap">
                <div>
                  <div className="gem-score">{Number(g.gem_score * 100).toFixed(0)}<span style={{ fontSize: 12, color: "var(--text3)" }}>/100</span></div>
                  <div className="gem-meta">리뷰 {g.review_count}개 · 긍정 {Math.round(Number(g.positive_ratio) * 100)}%</div>
                </div>
                <span className="badge badge-teal">💎 명작</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function GamesPage({ onSelectGame }) {
  const [games, setGames] = useState(null);
  const [search, setSearch] = useState("");

  useEffect(() => {
    fetch(`${API}/games/?limit=100`)
      .then(r => r.json())
      .then(setGames)
      .catch(() => setGames([]));
  }, []);

  const filtered = games
    ?.filter(g => g.name.toLowerCase().includes(search.toLowerCase()))
    .sort((a, b) => (b.peak_in_game || 0) - (a.peak_in_game || 0));

  return (
    <div>
      <div style={{ display: "flex", gap: "1rem", marginBottom: "1.5rem", alignItems: "center" }}>
        <div className="section-title" style={{ margin: 0 }}>게임 순위</div>
        <input value={search} onChange={e => setSearch(e.target.value)} placeholder="게임 검색..."
          style={{ marginLeft: "auto", background: "var(--panel)", border: "1px solid var(--border)", color: "var(--text)", borderRadius: 6, padding: "6px 12px", fontSize: 13, fontFamily: "var(--font-body)", outline: "none", width: 200 }} />
      </div>
      {!filtered ? <Loading /> : filtered.length === 0 ? (
        <div className="loading">검색 결과가 없습니다</div>
      ) : (
        <div className="grid grid-2">
          {filtered.map((g, i) => (
            <div key={g.app_id} style={{ position: "relative" }}>
              <div style={{
                position: "absolute", top: 8, left: 8, zIndex: 1,
                fontFamily: "var(--font-head)", fontSize: 16, fontWeight: 700,
                color: i < 3 ? "var(--amber)" : "var(--text3)",
                background: "rgba(10,15,30,0.7)", borderRadius: 4, padding: "1px 6px"
              }}>
                #{i + 1}
              </div>
              <GameCard game={g} onClick={onSelectGame} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function StatsPage() {
  const [genres, setGenres] = useState(null);
  const [selectedGenre, setSelectedGenre] = useState(null);
  const [indieGames, setIndieGames] = useState(null);

  useEffect(() => {
    fetch(`${API}/stats/genres`).then(r => r.json()).then(setGenres).catch(() => setGenres([]));
  }, []);

  const handleGenreClick = async (genreName) => {
    if (selectedGenre === genreName) { setSelectedGenre(null); setIndieGames(null); return; }
    setSelectedGenre(genreName);
    setIndieGames(null);
    const data = await fetch(`${API}/stats/indie/${encodeURIComponent(genreName)}?limit=10`).then(r => r.json()).catch(() => []);
    setIndieGames(data);
  };

  const maxGames = genres ? Math.max(...genres.map(g => g.total_games)) : 1;

  return (
    <div>
      <div className="section-title mb1">장르별 통계</div>
      <div style={{ fontSize: 12, color: "var(--text3)", marginBottom: "1rem" }}>장르를 클릭하면 해당 장르의 인디게임 추천 목록을 볼 수 있어요</div>
      {!genres ? <Loading /> : (
        <>
          <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem", marginBottom: "2rem" }}>
            {genres.sort((a, b) => b.total_games - a.total_games).map(g => (
              <div key={g.genre_name} className="genre-row"
                style={{ cursor: "pointer", borderColor: selectedGenre === g.genre_name ? "rgba(66,135,245,0.5)" : undefined, background: selectedGenre === g.genre_name ? "var(--panel2)" : undefined }}
                onClick={() => handleGenreClick(g.genre_name)}>
                <div className="genre-name" style={{ color: selectedGenre === g.genre_name ? "var(--blue2)" : undefined }}>{g.genre_name}</div>
                <div className="genre-bar-wrap"><div className="genre-bar" style={{ width: `${(g.total_games / maxGames) * 100}%` }} /></div>
                <div className="genre-val">{fmtPrice(g.avg_price)}</div>
                <div className="genre-count">{g.total_games}개</div>
              </div>
            ))}
          </div>

          {selectedGenre && (
            <div style={{ marginBottom: "2rem" }}>
              <div className="section-title mb1">💎 {selectedGenre} 인디게임 추천</div>
              {!indieGames ? <Loading /> : indieGames.length === 0 ? (
                <div style={{ fontSize: 13, color: "var(--text3)", padding: "1rem" }}>해당 장르의 인디게임이 없습니다</div>
              ) : (
                <div className="grid grid-2">
                  {indieGames.map(g => (
                    <div key={g.app_id} className="card">
                      <div className="card-header">
                        <img className="card-img" src={g.header_image} alt={g.name} onError={e => e.target.style.display = "none"} />
                        <div><div className="card-title">{g.name}</div><div className="card-sub">{g.developer || "알 수 없음"}</div></div>
                      </div>
                      <div className="card-footer">
                        <div style={{ display: "flex", gap: "0.5rem" }}>
                          <span className="badge badge-blue">인디</span>
                          {g.is_free && <span className="badge badge-teal">무료</span>}
                        </div>
                        {g.metacritic_score && <span className="badge badge-amber">MC {g.metacritic_score}</span>}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          <div className="chart-card">
            <div className="chart-title">장르별 게임 수</div>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={genres.sort((a, b) => b.total_games - a.total_games).slice(0, 10)} layout="vertical" margin={{ left: 80 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" horizontal={false} />
                <XAxis type="number" tick={{ fill: "#8899bb", fontSize: 11 }} />
                <YAxis type="category" dataKey="genre_name" tick={{ fill: "#8899bb", fontSize: 11 }} width={80} />
                <Tooltip contentStyle={{ background: "#1a2340", border: "1px solid rgba(66,135,245,0.2)", borderRadius: 8, color: "#e8eaf6", fontSize: 13 }} />
                <Bar dataKey="total_games" fill="#4287f5" radius={[0, 4, 4, 0]} name="게임 수" />
                <ReferenceLine y={0} stroke="rgba(255,255,255,0.3)" strokeWidth={1} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </>
      )}
    </div>
  );
}

function GemsPage() {
  const [gems, setGems] = useState(null);

  useEffect(() => {
    fetch(`${API}/gems/?limit=20`).then(r => r.json()).then(setGems).catch(() => setGems([]));
  }, []);

  return (
    <div>
      <div className="section-title mb1">💎 숨은 명작</div>
      <div style={{ marginBottom: "1.5rem", padding: "1rem", background: "var(--panel)", border: "1px solid var(--border)", borderRadius: 8, fontSize: 13, color: "var(--text2)", lineHeight: 1.7 }}>
        긍정 비율 90% 이상 · 리뷰 수 500개 이하 · 가격 가성비 조합으로 선정된 숨은 명작 게임입니다.
      </div>
      {!gems ? <Loading /> : gems.length === 0 ? (
        <div className="loading">아직 분석 데이터가 없습니다. 분석 ETL 실행 후 확인해주세요.</div>
      ) : (
        <div className="grid grid-3">
          {gems.map(g => (
            <div key={g.app_id} className="gem-card">
              <img className="gem-img" src={g.header_image} alt={g.name} onError={e => e.target.style.background = "#1e294a"} />
              <div className="gem-body">
                <div className="gem-name">{g.name}</div>
                <div style={{ display: "flex", gap: "0.5rem", marginBottom: "0.5rem", flexWrap: "wrap" }}>
                  <span className="badge badge-teal">긍정 {Math.round(Number(g.positive_ratio) * 100)}%</span>
                  <span className="badge badge-blue">리뷰 {g.review_count}개</span>
                </div>
                <div className="gem-score-wrap">
                  <div>
                    <div className="gem-score">{Number(g.gem_score * 100).toFixed(0)}<span style={{ fontSize: 12, color: "var(--text3)" }}>/100</span></div>
                    <div className="gem-meta">gem score</div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function App() {
  const [page, setPage] = useState("home");
  const [selectedGame, setSelectedGame] = useState(null);

  const handleSelectGame = async (game) => {
    const full = await fetch(`${API}/games/${game.app_id}`).then(r => r.json()).catch(() => game);
    setSelectedGame(full);
    setPage("detail");
  };

  return (
    <>
      <style>{styles}</style>
      <div className="app">
        <nav className="nav">
          <div className="nav-logo">STEAM<span>DB</span></div>
          <div className="nav-links">
            {NAV.map(n => (
              <button key={n.id} className={`nav-btn${page === n.id && !selectedGame ? " active" : ""}`}
                onClick={() => { setPage(n.id); setSelectedGame(null); }}>
                {n.label}
              </button>
            ))}
          </div>
        </nav>
        <main className="main">
          {selectedGame ? (
            <GameDetail game={selectedGame} onBack={() => { setSelectedGame(null); setPage("games"); }} />
          ) : page === "home" ? (
            <HomePage onSelectGame={handleSelectGame} />
          ) : page === "games" ? (
            <GamesPage onSelectGame={handleSelectGame} />
          ) : page === "stats" ? (
            <StatsPage />
          ) : (
            <GemsPage />
          )}
        </main>
      </div>
    </>
  );
}