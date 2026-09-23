const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

async function apiFetch(
  endpoint: string,
  options: RequestInit = {}
) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });

  if (response.status === 401) {
    throw new Error("AUTH_REQUIRED");
  }

  if (!response.ok) {
    const errorText = await response.text();
    console.error(`API error ${response.status}:`, errorText);
    throw new Error(`API request failed: ${response.status}`);
  }

  return response.json();
}


// ─────────────────────────────────────────────
// AUTH
// ─────────────────────────────────────────────

export async function fetchCurrentUser() {
  return apiFetch("/auth/me");
}


// ─────────────────────────────────────────────
// PROFILE
// ─────────────────────────────────────────────

export async function fetchProfile() {
  return apiFetch("/profile");
}


// ─────────────────────────────────────────────
// REPOSITORIES
// ─────────────────────────────────────────────

export async function fetchRepositories() {
  return apiFetch("/repos");
}


export async function fetchRepositoryDetail(
  id: number | string
) {
  return apiFetch(`/repos/${id}`);
}


// ─────────────────────────────────────────────
// CAREER
// ─────────────────────────────────────────────

export async function uploadResume(file: File) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(
    `${API_BASE_URL}/career/resume/upload`,
    {
      method: "POST",
      body: formData,
      credentials: "include",
    }
  );

  if (!response.ok) {
    const errorText = await response.text();
    console.error("Resume upload failed:", errorText);
    throw new Error("Failed to upload and analyze resume");
  }

  return response.json();
}


export async function analyzeJobDescription(
  title: string,
  company: string,
  jobText: string
) {
  return apiFetch("/career/jobs/analyze", {
    method: "POST",
    body: JSON.stringify({
      title,
      company,
      job_text: jobText,
    }),
  });
}


// ─────────────────────────────────────────────
// ROADMAP
// ─────────────────────────────────────────────

export async function fetchRoadmap(
  targetRole: string = "Backend Engineer"
) {
  return apiFetch(
    `/roadmap?target_role=${encodeURIComponent(targetRole)}`
  );
}


// ─────────────────────────────────────────────
// CHAT
// ─────────────────────────────────────────────

export async function sendChatMessage(message: string) {
  return apiFetch("/chat", {
    method: "POST",
    body: JSON.stringify({
      message,
    }),
  });
}