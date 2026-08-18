import React, { useEffect, useMemo, useState } from "react";

const API_BASE = "http://127.0.0.1:8000/api/knowledge-base";

const Knowledge_Base = () => {
  const [docs, setDocs] = useState([]);
  const [title, setTitle] = useState("");
  const [note, setNote] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileText, setFileText] = useState("");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingDocs, setLoadingDocs] = useState(false);
  const [status, setStatus] = useState("");

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    setLoadingDocs(true);
    try {
      const response = await fetch(`${API_BASE}/docs/`);
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data?.error || "Failed to load knowledge base documents.");
      }
      setDocs(Array.isArray(data.documents) ? data.documents : []);
    } catch (error) {
      setStatus(error.message || "Failed to load documents.");
      setDocs([]);
    } finally {
      setLoadingDocs(false);
    }
  };

  const filteredDocs = useMemo(() => {
    const query = search.trim().toLowerCase();
    if (!query) return docs;

    return docs.filter((doc) => {
      return [doc.title, doc.file_name, doc.preview, doc.chunks]
        .filter(Boolean)
        .some((value) => String(value).toLowerCase().includes(query));
    });
  }, [docs, search]);

  const readFilePreview = async (file) => {
    if (!file) return "";

    const isTextLike =
      file.type.startsWith("text/") ||
      file.name.endsWith(".md") ||
      file.name.endsWith(".txt") ||
      file.name.endsWith(".csv") ||
      file.name.endsWith(".json");

    if (!isTextLike) {
      return "";
    }

    return await file.text();
  };

  const handleFileChange = async (event) => {
    const file = event.target.files?.[0] || null;
    setSelectedFile(file);
    setFileText("");

    if (!file) return;

    const preview = await readFilePreview(file);
    setFileText(preview.slice(0, 8000));
    if (!title.trim()) {
      setTitle(file.name.replace(/\.[^/.]+$/, ""));
    }
  };

  const tryApiUpload = async (formData) => {
    const response = await fetch(`${API_BASE}/upload/`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      let errorMessage = "Upload failed.";
      try {
        const payload = await response.json();
        errorMessage = payload?.error || payload?.detail || errorMessage;
      } catch {
        const text = await response.text();
        if (text) errorMessage = text;
      }
      throw new Error(errorMessage);
    }

    return await response.json();
  };

  const handleAddDocument = async () => {
    if (!title.trim() && !selectedFile) {
      setStatus("Add a title or choose a file first.");
      return;
    }

    setLoading(true);
    setStatus("");

    try {
      if (selectedFile) {
        const formData = new FormData();
        formData.append("title", title.trim() || selectedFile.name);
        formData.append("file", selectedFile);
        formData.append("preview", note || fileText);

        const apiResult = await tryApiUpload(formData);
        setStatus(apiResult.message || "Uploaded and indexed in Chroma.");
      } else {
        const formData = new FormData();
        formData.append("title", title.trim());
        formData.append("preview", note.trim() || "");
        const apiResult = await tryApiUpload(formData);
        setStatus(apiResult.message || "Saved and indexed in Chroma.");
      }

      setTitle("");
      setNote("");
      setSelectedFile(null);
      setFileText("");
      const input = document.getElementById("kb-file-input");
      if (input) input.value = "";
      await loadDocuments();
    } catch (error) {
      setStatus(error.message || "Failed to add knowledge item.");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (documentId) => {
    try {
      const response = await fetch(`${API_BASE}/delete/${documentId}/`, {
        method: "DELETE",
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data?.error || "Failed to delete document.");
      }
      setStatus(data.message || "Removed from Chroma.");
      await loadDocuments();
    } catch (error) {
      setStatus(error.message || "Failed to delete document.");
    }
  };

  return (
    <div style={pageStyle}>
      <div style={heroStyle}>
        <div>
          <p style={eyebrowStyle}>Knowledge Base</p>
          <h1 style={titleStyle}>Upload documents and notes for future Chroma retrieval</h1>
          <p style={subtitleStyle}>
            Add file-backed knowledge now. This page keeps a local index today and is ready to sync into your
            backend vector store when the `/api/knowledge-base/` endpoints are added.
          </p>
        </div>
        <div style={statCardRow}>
          <div style={statCard}>
            <span style={statLabel}>Items</span>
            <strong style={statValue}>{loadingDocs ? "..." : docs.length}</strong>
          </div>
          <div style={statCard}>
            <span style={statLabel}>Visible</span>
            <strong style={statValue}>{filteredDocs.length}</strong>
          </div>
        </div>
      </div>

      <div style={gridStyle}>
        <section style={panelStyle}>
          <div style={panelHeaderStyle}>
            <div>
              <p style={panelKickerStyle}>Knowledge Editor</p>
              <h2 style={sectionTitle}>Add knowledge</h2>
            </div>
            <div style={panelBadgeStyle}>Chroma ready</div>
          </div>
          <div style={fieldGroup}>
            <label style={labelStyle}>Title</label>
            <input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Example: Product FAQ"
              style={inputStyle}
            />
          </div>

          <div style={uploadBoxStyle}>
            <div style={uploadTopRowStyle}>
              <div>
                <label style={labelStyle}>File</label>
                <p style={uploadHintStyle}>
                  Drag in a text file, PDF, or code snippet and the backend will index it into Chroma.
                </p>
              </div>
              <div style={uploadTagStyle}>PDF + text</div>
            </div>
            <input
              id="kb-file-input"
              type="file"
              onChange={handleFileChange}
              style={fileInputStyle}
            />
            <p style={helperNoteStyle}>
              Supported now: text, markdown, csv, json, pdf and code files.
            </p>
          </div>

          {selectedFile && (
            <div style={filePreviewCard}>
              <div style={filePreviewHeader}>
                <strong>{selectedFile.name}</strong>
                <span style={pillStyle}>{Math.round(selectedFile.size / 1024)} KB</span>
              </div>
              <p style={metaText}>{selectedFile.type || "unknown type"}</p>
              {fileText ? (
                <pre style={previewBox}>{fileText}</pre>
              ) : (
                <p style={hintStyle}>No inline preview available for this file type.</p>
              )}
            </div>
          )}

          <button onClick={handleAddDocument} disabled={loading} style={primaryButtonStyle}>
            {loading ? "Saving..." : "Save Knowledge Item"}
          </button>

          {status && <div style={statusStyle}>{status}</div>}
        </section>

        <section style={panelStyle}>
          <div style={listHeader}>
            <h2 style={sectionTitle}>Stored knowledge</h2>
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search documents..."
              style={searchStyle}
            />
          </div>

          {filteredDocs.length === 0 ? (
            <div style={emptyState}>
              <h3>No knowledge items yet</h3>
              <p>Add your first file or note on the left.</p>
            </div>
          ) : (
            <div style={docListStyle}>
              {filteredDocs.map((doc) => (
                <article key={doc.document_id} style={docCardStyle}>
              <div style={docTopRow}>
                    <div>
                      <h3 style={docTitleStyle}>{doc.title}</h3>
                      <p style={metaText}>{doc.file_name || "Manual note"}</p>
                    </div>
                    <button onClick={() => handleDelete(doc.document_id)} style={deleteButtonStyle}>
                      Remove
                    </button>
                  </div>
                  <div style={docMetaRow}>
                    <span style={pillStyle}>{doc.chunks || 0} chunks</span>
                    <span style={pillStyle}>{doc.created_at ? new Date(doc.created_at).toLocaleString() : "recent"}</span>
                    <span style={pillStyle}>{doc.document_id}</span>
                  </div>
                  <p style={docPreviewText}>{doc.preview || "Stored in Chroma."}</p>
                </article>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
};

const pageStyle = {
  padding: "24px",
  background:
    "radial-gradient(circle at top left, rgba(0, 209, 178, 0.15), transparent 32%), linear-gradient(180deg, #f7fafc 0%, #eef3f8 100%)",
  borderRadius: "16px",
};

const heroStyle = {
  display: "flex",
  justifyContent: "space-between",
  gap: "24px",
  alignItems: "flex-start",
  marginBottom: "24px",
};

const eyebrowStyle = {
  margin: "0 0 8px",
  textTransform: "uppercase",
  letterSpacing: "0.14em",
  fontSize: "12px",
  fontWeight: 700,
  color: "#0f766e",
};

const titleStyle = {
  margin: 0,
  fontSize: "32px",
  lineHeight: 1.1,
  color: "#0f172a",
};

const subtitleStyle = {
  margin: "12px 0 0",
  maxWidth: "760px",
  color: "#475569",
  lineHeight: 1.6,
};

const statCardRow = {
  display: "grid",
  gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
  gap: "12px",
  minWidth: "260px",
};

const statCard = {
  background: "rgba(255,255,255,0.75)",
  border: "1px solid rgba(148,163,184,0.2)",
  borderRadius: "14px",
  padding: "14px",
  boxShadow: "0 10px 30px rgba(15, 23, 42, 0.06)",
};

const statLabel = {
  display: "block",
  fontSize: "12px",
  color: "#64748b",
  marginBottom: "6px",
};

const statValue = {
  fontSize: "26px",
  color: "#0f172a",
};

const gridStyle = {
  display: "grid",
  gridTemplateColumns: "1fr 1.2fr",
  gap: "20px",
  alignItems: "start",
};

const panelStyle = {
  background: "linear-gradient(180deg, rgba(255,255,255,0.96), rgba(248,250,252,0.92))",
  border: "1px solid rgba(148,163,184,0.22)",
  borderRadius: "22px",
  padding: "22px",
  boxShadow: "0 24px 60px rgba(15, 23, 42, 0.10)",
  backdropFilter: "blur(12px)",
  overflow: "hidden",
};

const sectionTitle = {
  margin: "0",
  color: "#0f172a",
  fontSize: "22px",
};

const fieldGroup = {
  display: "flex",
  flexDirection: "column",
  gap: "10px",
  marginBottom: "14px",
};

const labelStyle = {
  fontSize: "12px",
  fontWeight: 600,
  color: "#334155",
  letterSpacing: "0.06em",
  textTransform: "uppercase",
};

const inputStyle = {
  width: "100%",
  maxWidth: "100%",
  boxSizing: "border-box",
  padding: "14px 16px",
  border: "1px solid #cbd5e1",
  borderRadius: "14px",
  outline: "none",
  fontSize: "15px",
  background: "#fff",
  boxShadow: "inset 0 1px 2px rgba(15, 23, 42, 0.04)",
};

const fileInputStyle = {
  width: "100%",
  maxWidth: "100%",
  boxSizing: "border-box",
  padding: "12px 14px",
  border: "1px dashed #94a3b8",
  borderRadius: "14px",
  background: "#f8fafc",
};

const hintStyle = {
  margin: 0,
  fontSize: "12px",
  color: "#64748b",
  lineHeight: 1.5,
};

const uploadBoxStyle = {
  border: "1px solid #dbe4ef",
  borderRadius: "18px",
  padding: "16px",
  background: "linear-gradient(180deg, #ffffff, #f8fbff)",
  marginBottom: "14px",
};

const uploadTopRowStyle = {
  display: "flex",
  alignItems: "flex-start",
  justifyContent: "space-between",
  gap: "12px",
  marginBottom: "10px",
};

const uploadHintStyle = {
  margin: "6px 0 0",
  fontSize: "13px",
  color: "#64748b",
  lineHeight: 1.5,
};

const helperNoteStyle = {
  margin: "10px 0 0",
  fontSize: "12px",
  color: "#0f766e",
  fontWeight: 600,
};

const uploadTagStyle = {
  padding: "8px 12px",
  borderRadius: "999px",
  background: "#0f172a",
  color: "#fff",
  fontSize: "11px",
  fontWeight: 700,
  whiteSpace: "nowrap",
};

const panelHeaderStyle = {
  display: "flex",
  alignItems: "flex-start",
  justifyContent: "space-between",
  gap: "12px",
  marginBottom: "18px",
};

const panelKickerStyle = {
  margin: "0 0 6px",
  fontSize: "11px",
  textTransform: "uppercase",
  letterSpacing: "0.16em",
  fontWeight: 700,
  color: "#0ea5e9",
};

const panelBadgeStyle = {
  padding: "8px 12px",
  borderRadius: "999px",
  background: "rgba(14, 165, 233, 0.10)",
  color: "#0369a1",
  fontSize: "12px",
  fontWeight: 700,
  whiteSpace: "nowrap",
};

const filePreviewCard = {
  border: "1px solid #dbe4ef",
  borderRadius: "16px",
  padding: "14px",
  marginBottom: "16px",
  background: "linear-gradient(180deg, #ffffff, #f8fafc)",
};

const filePreviewHeader = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  gap: "12px",
  marginBottom: "8px",
};

const previewBox = {
  margin: 0,
  padding: "14px",
  borderRadius: "14px",
  background: "#0f172a",
  color: "#e2e8f0",
  fontSize: "12px",
  lineHeight: 1.7,
  maxHeight: "180px",
  overflow: "auto",
  whiteSpace: "pre-wrap",
  wordBreak: "break-word",
};

const metaText = {
  margin: "0 0 8px",
  fontSize: "12px",
  color: "#64748b",
};

const pillStyle = {
  display: "inline-flex",
  alignItems: "center",
  padding: "4px 10px",
  borderRadius: "999px",
  background: "#e2e8f0",
  color: "#334155",
  fontSize: "11px",
  fontWeight: 600,
};

const primaryButtonStyle = {
  width: "100%",
  padding: "14px 18px",
  border: "none",
  borderRadius: "14px",
  background: "linear-gradient(135deg, #0f766e 0%, #0ea5e9 100%)",
  color: "white",
  fontWeight: 800,
  letterSpacing: "0.02em",
  cursor: "pointer",
  boxShadow: "0 16px 28px rgba(14, 165, 233, 0.25)",
};

const statusStyle = {
  marginTop: "14px",
  padding: "12px 14px",
  borderRadius: "14px",
  background: "#ecfeff",
  color: "#155e75",
  border: "1px solid #a5f3fc",
  fontSize: "14px",
};

const listHeader = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  gap: "12px",
  marginBottom: "16px",
};

const searchStyle = {
  minWidth: "240px",
  flex: "0 0 240px",
  padding: "13px 14px",
  border: "1px solid #cbd5e1",
  borderRadius: "14px",
  outline: "none",
  background: "#fff",
};

const emptyState = {
  padding: "40px 20px",
  textAlign: "center",
  color: "#64748b",
  border: "1px dashed #cbd5e1",
  borderRadius: "16px",
  background: "#f8fafc",
};

const docListStyle = {
  display: "grid",
  gap: "14px",
};

const docCardStyle = {
  border: "1px solid #e2e8f0",
  borderRadius: "18px",
  padding: "18px",
  background: "#fff",
  boxShadow: "0 12px 26px rgba(15, 23, 42, 0.05)",
};

const docTopRow = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "flex-start",
  gap: "12px",
  marginBottom: "10px",
};

const docTitleStyle = {
  margin: "0 0 4px",
  color: "#0f172a",
  fontSize: "18px",
};

const docMetaRow = {
  display: "flex",
  flexWrap: "wrap",
  gap: "8px",
  marginBottom: "10px",
};

const docPreviewText = {
  margin: 0,
  color: "#334155",
  lineHeight: 1.6,
  whiteSpace: "pre-wrap",
  wordBreak: "break-word",
};

const deleteButtonStyle = {
  border: "none",
  background: "#fee2e2",
  color: "#b91c1c",
  padding: "8px 12px",
  borderRadius: "10px",
  cursor: "pointer",
  fontWeight: 700,
};

export default Knowledge_Base;
