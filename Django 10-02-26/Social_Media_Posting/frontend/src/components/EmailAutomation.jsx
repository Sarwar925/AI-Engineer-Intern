import React, { useEffect, useRef, useState } from "react";

const EmailAutomation = () => {
  const [email, setEmail] = useState("");
  const [appPassword, setAppPassword] = useState("");
  const [running, setRunning] = useState(false);
  const [saved, setSaved] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const intervalRef = useRef(null);

  useEffect(() => {
    const loadConfig = async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/api/email-automation/config/", {
          credentials: "include",
        });
        const data = await res.json();
        setEmail(data.email || "");
        setAppPassword(data.app_password || "");
      } catch (err) {
        setError("Could not load saved email settings");
      }
    };

    loadConfig();

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  const saveCredentials = async () => {
    setError("");
    setSaved(false);

    try {
      const res = await fetch("http://127.0.0.1:8000/api/email-automation/config/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({
          email,
          app_password: appPassword,
        }),
      });

      const data = await res.json();

      if (!res.ok || !data.success) {
        throw new Error(data.error || "Could not save email settings");
      }

      setSaved(true);
      return true;
    } catch (err) {
      setError(err.message || "Could not save email settings");
      return false;
    }
  };

  const updateReadingState = async (isReading) => {
    try {
      await fetch("http://127.0.0.1:8000/api/email-automation/config/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({ is_reading: isReading }),
      });
    } catch (err) {
      setError("Could not update reading status");
    }
  };

  const runAgent = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/email-automation/run/", {
        method: "POST",
        credentials: "include",
      });

      const data = await res.json();

      if (!res.ok || !data.success) {
        throw new Error(data.error || "Email automation failed");
      }

      setResult(data);
    } catch (err) {
      setError(err.message || "Email automation failed");
    }
  };

  const startReading = async () => {
    setError("");
    setResult(null);

    const savedOk = await saveCredentials();
    if (!savedOk) {
      return;
    }

    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }

    setRunning(true);
    await runAgent();
    await updateReadingState(true);

    intervalRef.current = setInterval(() => {
      runAgent();
    }, 15000);
  };

  const stopReading = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    setRunning(false);
    updateReadingState(false);
  };

  return (
    <div style={{ padding: "20px" }}>
      <h2>Email Automation Agent</h2>
      <p>
        This agent checks unread emails, classifies them as support, sales, or spam,
        generates a reply, and sends it back in the same thread.
      </p>

      <div style={layoutStyle}>
        <div style={formCardStyle}>
          <div style={fieldStyle}>
            <label style={labelStyle}>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              style={inputStyle}
            />
          </div>

          <div style={fieldStyle}>
            <label style={labelStyle}>App Password</label>
            <input
              type="password"
              value={appPassword}
              onChange={(e) => setAppPassword(e.target.value)}
              placeholder="App password"
              style={inputStyle}
            />
          </div>

          <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
            <button onClick={saveCredentials} style={secondaryBtnStyle}>
              Save Credentials
            </button>

            {!running ? (
              <button onClick={startReading} style={runBtnStyle}>
                Read Email
              </button>
            ) : (
              <button onClick={stopReading} style={stopBtnStyle}>
                Stop Reading
              </button>
            )}
          </div>

          {saved && <p style={{ color: "green", marginTop: "10px" }}>Credentials saved.</p>}
        </div>

        <div style={helpCardStyle}>
          <h3 style={{ marginTop: 0 }}>How to generate an app password</h3>
          <p style={{ marginBottom: "10px" }}>
            If you are using Gmail, create an app password before saving it here.
          </p>
          <ol style={helpListStyle}>
            <li>Open your Google Account settings.</li>
            <li>Go to <strong>Security</strong>.</li>
            <li>Turn on <strong>2-Step Verification</strong> if it is not already enabled.</li>
            <li>Find <strong>App passwords</strong> under Security.</li>
            <li>Create a new app password for <strong>Mail</strong> or <strong>Other</strong>.</li>
            <li>Copy the generated 16-character password and paste it here.</li>
          </ol>
          <p style={{ marginBottom: 0, color: "#475569" }}>
            The app password is not your normal email password.
          </p>
        </div>
      </div>

      {error && (
        <div style={errorStyle}>
          {error}
        </div>
      )}

      {result && (
        <div style={resultCardStyle}>
          <h3>Last Run Summary</h3>
          <div style={{ marginTop: "15px", whiteSpace: "pre-wrap", lineHeight: "1.6" }}>
            {result.agent_summary ? (
              <div>{result.agent_summary}</div>
            ) : (
              <p>No unread emails were processed.</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

const runBtnStyle = {
  backgroundColor: "#4A90E2",
  color: "white",
  border: "none",
  borderRadius: "6px",
  padding: "10px 16px",
  cursor: "pointer",
  fontWeight: "bold",
};

const stopBtnStyle = {
  backgroundColor: "#c62828",
  color: "white",
  border: "none",
  borderRadius: "6px",
  padding: "10px 16px",
  cursor: "pointer",
  fontWeight: "bold",
};

const secondaryBtnStyle = {
  backgroundColor: "#6b7280",
  color: "white",
  border: "none",
  borderRadius: "6px",
  padding: "10px 16px",
  cursor: "pointer",
  fontWeight: "bold",
};

const formCardStyle = {
  flex: "1 1 520px",
  padding: "16px",
  backgroundColor: "#f7f9fc",
  borderRadius: "8px",
  border: "1px solid #d8e1ef",
};

const layoutStyle = {
  display: "flex",
  gap: "16px",
  alignItems: "flex-start",
  flexWrap: "wrap",
  marginTop: "16px",
  marginBottom: "16px",
};

const fieldStyle = {
  display: "flex",
  flexDirection: "column",
  gap: "6px",
  marginBottom: "12px",
};

const labelStyle = {
  fontWeight: "bold",
  color: "#1f2937",
};

const inputStyle = {
  padding: "10px 12px",
  borderRadius: "6px",
  border: "1px solid #cbd5e1",
};

const errorStyle = {
  marginTop: "16px",
  padding: "12px",
  backgroundColor: "#ffe1e1",
  color: "#a30000",
  borderRadius: "6px",
};

const resultCardStyle = {
  marginTop: "16px",
  padding: "16px",
  backgroundColor: "#f7f9fc",
  borderRadius: "8px",
  border: "1px solid #d8e1ef",
};

const helpCardStyle = {
  flex: "1 1 320px",
  padding: "16px",
  backgroundColor: "#fff8e8",
  borderRadius: "8px",
  border: "1px solid #f1d28a",
};

const helpListStyle = {
  marginTop: "0",
  paddingLeft: "20px",
  lineHeight: "1.6",
  color: "#334155",
};

const rowStyle = {
  padding: "10px 0",
  borderBottom: "1px solid #e5eaf2",
};

export default EmailAutomation;
